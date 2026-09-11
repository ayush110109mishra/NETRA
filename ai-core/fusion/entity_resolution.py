"""
Entity Resolution Engine for NETRA Phase 5.
Deterministically correlates heterogeneous source-level identifiers and telemetry
signatures to synthetic entities in EntityRepository without forcing speculative matches.
"""

from typing import Dict, List, Optional, Tuple, Any
import logging

from config import NetraConfig, default_config, EntityResolutionConfig
from models.geo import haversine_distance_km
from models.fusion_intelligence import (
    CanonicalObservation,
    EntityResolutionResult,
    EntityResolutionStatus,
)
from entities.repository import EntityRepository

logger = logging.getLogger("netra.fusion.entity_resolution")


class EntityResolver:
    """
    Resolves multi-source observation signatures to synthetic entity records.
    Distinguishes unambiguous matches, ambiguous candidate sets, and unresolvable entities.
    """

    # Predefined deterministic synthetic entity alias mappings (Section 12 & 25)
    DEFAULT_KNOWN_ALIASES: Dict[str, str] = {
        "R-104": "ENTITY-07",
        "O-771": "ENTITY-07",
        "T-22": "ENTITY-07",
        "RADAR-104": "ENTITY-07",
        "OPT-771": "ENTITY-07",
        "TRACK-ALPHA-01": "ENTITY-01",
        "TGT-BETA-02": "ENTITY-02",
        "RADAR-T-03": "ENTITY-03",
    }

    def __init__(
        self,
        config: Optional[NetraConfig] = None,
        repository: Optional[EntityRepository] = None,
        custom_aliases: Optional[Dict[str, str]] = None,
    ):
        self.config = config or default_config
        self.params: EntityResolutionConfig = self.config.entity_resolution
        self.repository = repository
        self.aliases: Dict[str, str] = dict(self.DEFAULT_KNOWN_ALIASES)
        if custom_aliases:
            self.aliases.update(custom_aliases)

    def register_alias(self, source_hint: str, canonical_entity_id: str) -> None:
        """Register a known synthetic track/target alias to an entity ID."""
        self.aliases[source_hint.upper()] = canonical_entity_id

    def resolve(
        self,
        observation: CanonicalObservation,
        candidate_entity_ids: Optional[List[str]] = None,
    ) -> EntityResolutionResult:
        """
        Resolves an observation to a synthetic entity.
        Returns EntityResolutionResult with match confidence, factor breakdown, and alternatives.
        """
        hint = (observation.entity_hint or "").strip().upper()

        # 1. Direct Canonical Entity ID match (e.g. already "ENTITY-07")
        if hint.startswith("ENTITY-"):
            return EntityResolutionResult(
                resolved_entity_id=hint,
                status=EntityResolutionStatus.RESOLVED,
                match_confidence=0.98,
                resolution_factors={"direct_entity_id_match": 1.0},
                alternatives=[],
                explanation=f"Observation provides direct canonical entity identifier: {hint}.",
            )

        # 2. Known Synthetic Alias Match
        if hint in self.aliases:
            resolved_id = self.aliases[hint]
            return EntityResolutionResult(
                resolved_entity_id=resolved_id,
                status=EntityResolutionStatus.RESOLVED,
                match_confidence=0.92,
                resolution_factors={"known_alias_mapping": 0.95, "hint": 1.0},
                alternatives=[],
                explanation=f"Observation track hint '{hint}' explicitly mapped to canonical entity {resolved_id}.",
            )

        # 3. Dynamic Telemetry Matching against Repository
        if self.repository is not None and observation.position is not None:
            candidates = candidate_entity_ids or self.repository.get_all_entity_ids()
            scored_candidates: List[Tuple[str, float, Dict[str, float]]] = []

            for cid in sorted(candidates):
                entity = self.repository.get_entity(cid)
                if not entity:
                    continue

                factors: Dict[str, float] = {}

                # Spatial proximity to entity last observed location or centroid
                profile = self.repository.get_profile(cid)
                spatial_score = 0.50
                if profile and profile.behavior and profile.behavior.spatial:
                    dist = haversine_distance_km(observation.position, profile.behavior.spatial.centroid)
                    spatial_score = max(0.0, 1.0 - (dist / 20.0))  # Decays over 20km
                factors["spatial_proximity"] = round(spatial_score, 4)

                # Kinematic compatibility
                kinematic_score = 0.50
                if observation.velocity and profile and profile.behavior and profile.behavior.kinematic:
                    v_diff = abs(observation.velocity.speed_kmh - profile.behavior.kinematic.mean_speed_kmh)
                    kinematic_score = max(0.0, 1.0 - (v_diff / 50.0))
                factors["kinematic_consistency"] = round(kinematic_score, 4)

                # Platform / Event type compatibility
                type_score = 0.50
                if observation.event_type and profile and profile.dominant_event_type:
                    if observation.event_type.lower() in profile.dominant_event_type.lower():
                        type_score = 0.90
                factors["type_compatibility"] = round(type_score, 4)

                total_score = (
                    (0.45 * spatial_score)
                    + (0.35 * kinematic_score)
                    + (0.20 * type_score)
                )
                scored_candidates.append((cid, total_score, factors))

            # Sort by total score descending
            scored_candidates.sort(key=lambda x: x[1], reverse=True)

            if scored_candidates:
                top_cid, top_score, top_factors = scored_candidates[0]
                alternatives = [
                    {"entity_id": c[0], "match_score": round(c[1], 4), "factors": c[2]}
                    for c in scored_candidates[1:4]
                ]

                # Ambiguity check
                if len(scored_candidates) > 1:
                    second_score = scored_candidates[1][1]
                    if top_score >= self.params.match_threshold and (top_score - second_score) < self.params.ambiguity_margin:
                        return EntityResolutionResult(
                            resolved_entity_id="ENTITY_UNRESOLVED",
                            status=EntityResolutionStatus.AMBIGUOUS,
                            match_confidence=round(top_score, 4),
                            resolution_factors=top_factors,
                            alternatives=[{"entity_id": top_cid, "match_score": round(top_score, 4)}] + alternatives,
                            explanation=(
                                f"Ambiguous resolution: Top candidate {top_cid} ({top_score:.2f}) "
                                f"and {scored_candidates[1][0]} ({second_score:.2f}) differ by less than "
                                f"margin {self.params.ambiguity_margin}."
                            ),
                        )

                if top_score >= self.params.match_threshold:
                    return EntityResolutionResult(
                        resolved_entity_id=top_cid,
                        status=EntityResolutionStatus.RESOLVED,
                        match_confidence=round(top_score, 4),
                        resolution_factors=top_factors,
                        alternatives=alternatives,
                        explanation=f"Telemetry matched to canonical entity {top_cid} with confidence {top_score:.2f}.",
                    )

        # 4. Fallback: Unresolved
        return EntityResolutionResult(
            resolved_entity_id="ENTITY_UNRESOLVED",
            status=EntityResolutionStatus.UNRESOLVED,
            match_confidence=0.20,
            resolution_factors={"insufficient_evidence": 1.0},
            alternatives=[],
            explanation=f"Insufficient telemetry or unknown hint '{hint}' to resolve synthetic entity.",
        )
