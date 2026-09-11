"""
Evidence Fusion Engine for NETRA Phase 5.
Synthesizes multi-source telemetry into unified FusedObservation models using
explainable weighted mathematical fusion, reliability weighting, and uncertainty estimation.
"""

from datetime import datetime, timezone
import hashlib
import math
from typing import Any, Dict, List, Optional, Tuple
import logging

from config import NetraConfig, default_config, FusionWeights
from models.common import Coordinates
from models.fusion_intelligence import (
    CanonicalObservation,
    ConflictRecord,
    ConflictStatus,
    ConflictType,
    CorroborationResult,
    EntityResolutionResult,
    FusedObservation,
    Velocity,
)
from fusion.source_registry import SourceRegistry

logger = logging.getLogger("netra.fusion.fusion")


class EvidenceFuser:
    """
    Synthesizes compatible multi-sensor observations into unified fused states.
    Applies inverse-uncertainty reliability weighting for kinematics and coordinates.
    """

    def __init__(
        self,
        config: Optional[NetraConfig] = None,
        source_registry: Optional[SourceRegistry] = None,
    ):
        self.config = config or default_config
        self.weights: FusionWeights = self.config.fusion_weights
        self.registry = source_registry or SourceRegistry(self.config)

    def fuse(
        self,
        observations: List[CanonicalObservation],
        entity_resolution: EntityResolutionResult,
        corroboration: CorroborationResult,
        conflicts: List[ConflictRecord],
        evidence_quality: float,
        temporal_agreement: float = 1.0,
        spatial_agreement: float = 1.0,
    ) -> FusedObservation:
        """
        Synthesizes a group of aligned observations for a resolved entity
        into a single explainable FusedObservation.
        """
        if not observations:
            raise ValueError("Cannot fuse empty observation set.")

        entity_id = entity_resolution.resolved_entity_id
        supporting_sources = sorted(list(set(o.source_id for o in observations)))

        # 1. Consensus Timestamp (reliability-weighted or latest high-reliability observation)
        fused_ts = self._compute_fused_timestamp(observations)

        # 2. Geospatial Fusion (weighted centroid)
        fused_pos, fused_unc = self._compute_fused_position(observations, conflicts)

        # 3. Kinematic Fusion (weighted velocity)
        fused_vel = self._compute_fused_velocity(observations, conflicts)

        # 4. Event Type Consensus
        fused_event_type = self._compute_fused_event_type(observations, conflicts)

        # 5. Multi-Source Fusion Score & Confidence
        # Mean source reliability
        rels = [self.registry.get_source(o.source_id).reliability for o in observations]
        mean_rel = sum(rels) / len(rels)

        # Field completeness
        completeness = sum(
            (1 if o.position else 0) + (1 if o.velocity else 0) + (1 if o.event_type else 0)
            for o in observations
        ) / (3.0 * len(observations))

        # Conflict score
        conflict_score = max([c.severity for c in conflicts], default=0.0)

        # Weighted Fusion Agreement Score
        w = self.weights
        agreement_score = (
            (w.source_reliability * mean_rel)
            + (w.temporal_agreement * temporal_agreement)
            + (w.spatial_agreement * spatial_agreement)
            + (w.corroboration * corroboration.corroboration_score)
            + (w.evidence_quality * evidence_quality)
            + (w.completeness * completeness)
        )
        agreement_score = round(max(0.0, min(1.0, agreement_score)), 4)

        # Confidence Calibration (decoupled, penalizing conflicts and unverified sources)
        confidence = agreement_score
        if conflict_score > 0.0:
            confidence -= (conflict_score * 0.25)

        # Multi-source independent bonus
        if corroboration.independent_source_count >= 3:
            confidence += 0.08
        elif corroboration.independent_source_count == 2:
            confidence += 0.04

        # Cold-start cap if all sources are cold-start or low reliability
        if all(self.registry.get_source(o.source_id).metadata.get("cold_start", False) for o in observations):
            confidence = min(confidence, 0.35)
        elif mean_rel <= 0.40:
            confidence = min(confidence, 0.45)

        # Ambiguous entity resolution cap
        if entity_resolution.status.value == "AMBIGUOUS":
            confidence = min(confidence, 0.50)
        elif entity_resolution.status.value == "UNRESOLVED":
            confidence = min(confidence, 0.30)

        confidence = round(max(0.0, min(1.0, confidence)), 4)

        # Deterministic Fused Observation ID
        hash_str = f"{entity_id}_{fused_ts.isoformat()}_{':'.join(supporting_sources)}"
        fused_id = f"FO-{hashlib.sha256(hash_str.encode('utf-8')).hexdigest()[:8].upper()}"

        # Compile source claims
        source_claims = {}
        for o in observations:
            source_claims[o.source_id] = {
                "observation_id": o.observation_id,
                "timestamp": o.timestamp.isoformat(),
                "position": o.position.model_dump() if o.position else None,
                "velocity": o.velocity.model_dump() if o.velocity else None,
                "event_type": o.event_type,
                "reliability": self.registry.get_source(o.source_id).reliability,
            }

        # Human-readable explanation
        expl_parts = [
            f"Fused from {len(observations)} observations across {len(supporting_sources)} sources ({corroboration.independent_source_count} independent)",
            f"Agreement {agreement_score:.2f}",
            f"Evidence quality {evidence_quality:.2f}",
            f"Confidence {confidence:.2f}",
        ]
        if conflicts:
            expl_parts.append(f"Contains {len(conflicts)} conflict(s) [max severity {conflict_score:.2f}]")
        if corroboration.duplicate_source_count > 0:
            expl_parts.append(f"Filtered {corroboration.duplicate_source_count} duplicate feeds")

        return FusedObservation(
            fused_observation_id=fused_id,
            entity_id=entity_id,
            fused_timestamp=fused_ts,
            fused_position=fused_pos,
            position_uncertainty_km=round(fused_unc, 3),
            fused_velocity=fused_vel,
            fused_event_type=fused_event_type,
            supporting_sources=supporting_sources,
            independent_source_count=corroboration.independent_source_count,
            agreement_score=agreement_score,
            conflict_score=round(conflict_score, 4),
            evidence_quality=round(evidence_quality, 4),
            fusion_confidence=confidence,
            source_claims=source_claims,
            provenance={
                "fusion_engine": "NETRA_PHASE_5_EVIDENCE_FUSER",
                "observations_fused": [o.observation_id for o in observations],
                "entity_resolution_confidence": entity_resolution.match_confidence,
            },
            explanation=". ".join(expl_parts) + ".",
        )

    def _compute_fused_timestamp(self, observations: List[CanonicalObservation]) -> datetime:
        # Highest reliability source timestamp or latest
        best_obs = max(
            observations,
            key=lambda o: (self.registry.get_source(o.source_id).reliability, o.timestamp)
        )
        return best_obs.timestamp

    def _compute_fused_position(
        self,
        observations: List[CanonicalObservation],
        conflicts: List[ConflictRecord],
    ) -> Tuple[Optional[Coordinates], float]:
        pos_obs = [o for o in observations if o.position is not None]
        if not pos_obs:
            return None, 0.10

        # Check if there is an unresolved position conflict
        unresolved_pos_conf = any(
            c.conflict_type == ConflictType.POSITION and c.status == ConflictStatus.UNRESOLVED
            for c in conflicts
        )

        if unresolved_pos_conf:
            # Under severe unresolved position conflict, adopt highest reliability source
            # but expand uncertainty radius to encompass divergence
            best_o = max(pos_obs, key=lambda o: self.registry.get_source(o.source_id).reliability)
            return best_o.position, max(5.0, best_o.position_uncertainty_km * 2.0)

        # Check for resolved claim
        resolved_claim = None
        for c in conflicts:
            if c.conflict_type == ConflictType.POSITION and c.status == ConflictStatus.RESOLVED and c.resolved_claim:
                resolved_claim = c.resolved_claim
                break

        if resolved_claim and "latitude" in resolved_claim:
            return Coordinates(
                latitude=resolved_claim["latitude"],
                longitude=resolved_claim["longitude"],
                sector_id=pos_obs[0].position.sector_id,
            ), resolved_claim.get("uncertainty_km", 0.20)

        # Reliability & inverse-uncertainty weighted centroid
        total_weight = 0.0
        weighted_lat = 0.0
        weighted_lon = 0.0
        weighted_alt = 0.0
        alt_count = 0
        sector = None

        for o in pos_obs:
            rel = self.registry.get_source(o.source_id).reliability
            unc = max(0.01, o.position_uncertainty_km or 0.10)
            weight = rel / unc
            total_weight += weight
            weighted_lat += weight * o.position.latitude
            weighted_lon += weight * o.position.longitude
            if o.position.altitude_m is not None:
                weighted_alt += weight * o.position.altitude_m
                alt_count += 1
            if not sector and o.position.sector_id:
                sector = o.position.sector_id

        if total_weight <= 0.0:
            return pos_obs[0].position, pos_obs[0].position_uncertainty_km

        fused_lat = weighted_lat / total_weight
        fused_lon = weighted_lon / total_weight
        fused_alt = (weighted_alt / total_weight) if alt_count > 0 else None

        # Fused uncertainty reduction from multiple independent sensors
        unc_sum_sq = sum(1.0 / (max(0.01, o.position_uncertainty_km)**2) for o in pos_obs)
        fused_unc = max(0.02, 1.0 / math.sqrt(unc_sum_sq))

        return Coordinates(
            latitude=round(fused_lat, 6),
            longitude=round(fused_lon, 6),
            altitude_m=round(fused_alt, 2) if fused_alt is not None else None,
            sector_id=sector,
        ), fused_unc

    def _compute_fused_velocity(
        self,
        observations: List[CanonicalObservation],
        conflicts: List[ConflictRecord],
    ) -> Optional[Velocity]:
        vel_obs = [o for o in observations if o.velocity is not None]
        if not vel_obs:
            return None

        # Check for resolved velocity claim
        for c in conflicts:
            if c.conflict_type == ConflictType.VELOCITY and c.status == ConflictStatus.RESOLVED and c.resolved_claim:
                return Velocity(
                    speed_kmh=c.resolved_claim["speed_kmh"],
                    heading_deg=c.resolved_claim.get("heading_deg"),
                )

        total_weight = 0.0
        weighted_speed = 0.0
        hdg_sin = 0.0
        hdg_cos = 0.0
        hdg_count = 0

        for o in vel_obs:
            rel = self.registry.get_source(o.source_id).reliability
            total_weight += rel
            weighted_speed += rel * o.velocity.speed_kmh
            if o.velocity.heading_deg is not None:
                rad = math.radians(o.velocity.heading_deg)
                hdg_sin += rel * math.sin(rad)
                hdg_cos += rel * math.cos(rad)
                hdg_count += 1

        if total_weight <= 0.0:
            return vel_obs[0].velocity

        fused_speed = round(weighted_speed / total_weight, 2)
        fused_heading = None
        if hdg_count > 0:
            angle_rad = math.atan2(hdg_sin, hdg_cos)
            angle_deg = math.degrees(angle_rad) % 360.0
            fused_heading = round(angle_deg, 2)

        return Velocity(speed_kmh=fused_speed, heading_deg=fused_heading)

    def _compute_fused_event_type(
        self,
        observations: List[CanonicalObservation],
        conflicts: List[ConflictRecord],
    ) -> Optional[str]:
        # Check for resolved event type claim
        for c in conflicts:
            if c.conflict_type == ConflictType.EVENT_TYPE and c.status == ConflictStatus.RESOLVED and c.resolved_claim:
                return c.resolved_claim.get("event_type")

        # Select event type supported by highest accumulated source reliability
        type_weights: Dict[str, float] = {}
        for o in observations:
            if o.event_type:
                rel = self.registry.get_source(o.source_id).reliability
                type_weights[o.event_type] = type_weights.get(o.event_type, 0.0) + rel

        if not type_weights:
            return None

        # Return event type with maximum weight deterministically
        sorted_types = sorted(type_weights.items(), key=lambda x: (-x[1], x[0]))
        return sorted_types[0][0]
