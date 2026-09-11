"""
Master Fusion Engine for NETRA Phase 5.
Orchestrates end-to-end normalization, alignment, entity resolution, conflict arbitration,
cross-source corroboration, weighted synthesis, evidence ledgering, and epistemic assessment.
"""

from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, List, Optional
import logging

from config import NetraConfig, default_config
from models.fusion_intelligence import (
    CanonicalObservation,
    ConflictRecord,
    CorroborationResult,
    EntityResolutionResult,
    EntityResolutionStatus,
    EvidenceRecord,
    FusedObservation,
    FusionAnalyzeRequest,
    FusionAnalyzeResponse,
    FusionAssessment,
    SourceHealth,
)
from entities.repository import EntityRepository
from fusion.source_registry import SourceRegistry
from fusion.normalization import SourceNormalizer
from fusion.temporal_alignment import TemporalAligner
from fusion.spatial_alignment import SpatialAligner
from fusion.entity_resolution import EntityResolver
from fusion.corroboration import CorroborationEngine
from fusion.conflict import ConflictDetector
from fusion.evidence import EvidenceLedger
from fusion.fusion import EvidenceFuser

logger = logging.getLogger("netra.fusion.engine")


class FusionEngine:
    """
    Central orchestration engine for NETRA Phase 5 Multi-Source Intelligence Fusion.
    Guarantees strict determinism, complete provenance tracking, and epistemic integrity.
    """

    def __init__(
        self,
        config: Optional[NetraConfig] = None,
        repository: Optional[EntityRepository] = None,
        source_registry: Optional[SourceRegistry] = None,
    ):
        self.config = config or default_config
        self.repository = repository
        self.registry = source_registry or SourceRegistry(self.config)
        self.normalizer = SourceNormalizer()
        self.temporal_aligner = TemporalAligner(self.config)
        self.spatial_aligner = SpatialAligner(self.config)
        self.entity_resolver = EntityResolver(self.config, repository=self.repository)
        self.corroboration_engine = CorroborationEngine(self.registry)
        self.conflict_detector = ConflictDetector(self.config, self.registry)
        self.evidence_ledger = EvidenceLedger(self.registry)
        self.fuser = EvidenceFuser(self.config, self.registry)

    def analyze(self, request: FusionAnalyzeRequest) -> FusionAnalyzeResponse:
        """
        Executes complete multi-source intelligence fusion workflow deterministically.
        """
        raw_obs_list = request.observations
        if not raw_obs_list:
            raise ValueError("Fusion request must contain at least one observation.")

        # 1. Normalization
        normalized_obs: List[CanonicalObservation] = []
        for raw in raw_obs_list:
            norm = self.normalizer.normalize_observation(raw)
            normalized_obs.append(norm)

        # Sort normalized observations deterministically
        normalized_obs.sort(key=lambda o: (o.timestamp, o.source_id, o.observation_id))

        # Deterministic Analysis ID based on observation signatures
        hash_input = ":".join(f"{o.source_id}_{o.timestamp.isoformat()}_{o.entity_hint}" for o in normalized_obs)
        analysis_id = f"FUS-RUN-{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()[:10].upper()}"

        # 2. Entity Resolution & Partitioning
        # Map each observation to an entity resolution result
        obs_by_entity: Dict[str, List[CanonicalObservation]] = {}
        resolutions_by_entity: Dict[str, EntityResolutionResult] = {}
        all_resolutions: List[EntityResolutionResult] = []

        for obs in normalized_obs:
            res = self.entity_resolver.resolve(obs)
            all_resolutions.append(res)
            target_key = res.resolved_entity_id
            if request.target_entity_id:
                # If specific target entity requested, prioritize matching
                if res.status != EntityResolutionStatus.UNRESOLVED and res.resolved_entity_id == request.target_entity_id:
                    target_key = request.target_entity_id

            if target_key not in obs_by_entity:
                obs_by_entity[target_key] = []
                resolutions_by_entity[target_key] = res
            obs_by_entity[target_key].append(obs)

        # 3. Conflict Detection across all observations
        all_conflicts = self.conflict_detector.detect_conflicts(normalized_obs)

        # 4. Multi-Source Corroboration & Fusion per Entity Cluster
        fused_observations: List[FusedObservation] = []
        evidence_records: List[EvidenceRecord] = []
        global_corroboration: Optional[CorroborationResult] = None

        # Sort entity keys deterministically
        for entity_key in sorted(obs_by_entity.keys()):
            group = obs_by_entity[entity_key]
            res = resolutions_by_entity[entity_key]

            # Corroboration for this group
            corrob = self.corroboration_engine.evaluate(group)
            if global_corroboration is None or len(group) >= len(normalized_obs) // 2:
                global_corroboration = corrob

            # Relevant conflicts involving this group
            group_obs_ids = set(o.observation_id for o in group)
            group_conflicts = [
                c for c in all_conflicts
                if any(oid in group_obs_ids for oid in c.observation_ids)
            ]

            # Evidence Ledger Record
            ev_record = self.evidence_ledger.create_evidence_record(
                observations=group,
                derived_from=[res.resolved_entity_id, f"CORROB-{corrob.independent_source_count}"],
                conflicts=group_conflicts,
            )
            evidence_records.append(ev_record)

            # Alignment checks within group
            temp_agree, spat_agree = self._compute_group_alignment_scores(group)

            # Weighted Fusion
            fused = self.fuser.fuse(
                observations=group,
                entity_resolution=res,
                corroboration=corrob,
                conflicts=group_conflicts,
                evidence_quality=ev_record.evidence_quality,
                temporal_agreement=temp_agree,
                spatial_agreement=spat_agree,
            )
            fused_observations.append(fused)

        if global_corroboration is None:
            global_corroboration = self.corroboration_engine.evaluate(normalized_obs)

        # 5. Source Health Summary
        source_health_summary: Dict[str, SourceHealth] = {}
        for obs in normalized_obs:
            sid = obs.source_id
            if sid not in source_health_summary:
                # Count observations and contradictions for this source
                obs_count = sum(1 for o in normalized_obs if o.source_id == sid)
                conflict_count = sum(1 for c in all_conflicts if sid in c.sources)
                is_stale = self.temporal_aligner.is_stale_observation(obs)
                # Check for dropout metadata in payload
                is_dropout = bool(obs.attributes.get("dropout", False) or obs.attributes.get("is_dropout", False))

                health = self.registry.get_source_health(
                    source_id=sid,
                    observation_count=obs_count,
                    contradiction_count=conflict_count,
                    is_stale=is_stale,
                    is_dropout=is_dropout,
                )
                source_health_summary[sid] = health

        # 6. Epistemic Four-Tier Assessment
        assessment = self._build_epistemic_assessment(
            normalized_obs=normalized_obs,
            fused_obs=fused_observations,
            resolutions=all_resolutions,
            conflicts=all_conflicts,
            corroboration=global_corroboration,
        )

        # 7. Overall Confidence Summary
        mean_fusion_confidence = (
            sum(f.fusion_confidence for f in fused_observations) / len(fused_observations)
            if fused_observations else 0.50
        )
        confidence_summary = {
            "overall_fusion_confidence": round(mean_fusion_confidence, 4),
            "independent_sources": global_corroboration.independent_source_count,
            "corroboration_score": global_corroboration.corroboration_score,
            "contradiction_penalty_applied": len(all_conflicts) > 0,
            "active_conflicts_count": len(all_conflicts),
        }

        return FusionAnalyzeResponse(
            schema_version="phase5-v1",
            analysis_id=analysis_id,
            status="SUCCESS",
            normalized_observations=normalized_obs,
            fused_observations=fused_observations,
            conflicts=all_conflicts,
            corroboration=global_corroboration,
            evidence_ledger=evidence_records,
            source_health_summary=source_health_summary,
            confidence_summary=confidence_summary,
            assessment=assessment,
            phase4_anomaly_assessment=None,  # Populated downstream by FusionIntelligenceEngine
            provenance={
                "platform": "NETRA_INTELLIGENCE_CORE",
                "phase": "PHASE_5_MULTI_SOURCE_FUSION",
                "total_observations_analyzed": len(normalized_obs),
                "unique_sources_reporting": len(source_health_summary),
                "fused_entities_count": len(fused_observations),
            },
        )

    def _compute_group_alignment_scores(
        self,
        group: List[CanonicalObservation],
    ) -> (float, float):
        if len(group) <= 1:
            return 1.0, 1.0

        temp_scores = []
        spat_scores = []
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                t_res = self.temporal_aligner.align(group[i], group[j])
                temp_scores.append(t_res.compatibility_score)
                s_res = self.spatial_aligner.align(group[i], group[j])
                spat_scores.append(s_res.spatial_compatibility_score)

        avg_temp = sum(temp_scores) / len(temp_scores) if temp_scores else 1.0
        avg_spat = sum(spat_scores) / len(spat_scores) if spat_scores else 1.0
        return round(avg_temp, 4), round(avg_spat, 4)

    def _build_epistemic_assessment(
        self,
        normalized_obs: List[CanonicalObservation],
        fused_obs: List[FusedObservation],
        resolutions: List[EntityResolutionResult],
        conflicts: List[ConflictRecord],
        corroboration: CorroborationResult,
    ) -> FusionAssessment:
        observed: List[str] = []
        fused: List[str] = []
        inferred: List[str] = []
        uncertain: List[str] = []

        # OBSERVED: Direct single-source measurements
        for o in normalized_obs:
            loc_str = f"at ({o.position.latitude:.4f}, {o.position.longitude:.4f})" if o.position else "no coordinates"
            vel_str = f"at {o.velocity.speed_kmh} km/h" if o.velocity else "no velocity"
            observed.append(
                f"[{o.source_id}] {o.event_type or 'ACTIVITY'} observed {loc_str} {vel_str} (t={o.timestamp.strftime('%H:%M:%S')})."
            )

        # FUSED: Multi-source corroborated telemetry
        for fo in fused_obs:
            pos_str = f"({fo.fused_position.latitude:.4f}, {fo.fused_position.longitude:.4f})" if fo.fused_position else "N/A"
            speed_str = f"{fo.fused_velocity.speed_kmh:.1f} km/h" if fo.fused_velocity else "N/A"
            fused.append(
                f"Entity {fo.entity_id}: Fused consensus pos {pos_str} (±{fo.position_uncertainty_km:.2f}km), "
                f"speed {speed_str} from {len(fo.supporting_sources)} sources ({fo.independent_source_count} independent, "
                f"agreement={fo.agreement_score:.2f}, conf={fo.fusion_confidence:.2f})."
            )

        # INFERRED: Analytical projections and entity resolutions
        for res in resolutions:
            if res.status == EntityResolutionStatus.RESOLVED:
                inferred.append(
                    f"Entity Resolution: Track hint successfully resolved to canonical {res.resolved_entity_id} "
                    f"(match confidence={res.match_confidence:.2f})."
                )

        # UNCERTAIN: Conflicts, ambiguities, and unverified feeds
        for conf in conflicts:
            uncertain.append(
                f"Contradiction [{conf.conflict_type.value}]: {conf.explanation} (status={conf.status.value})."
            )

        for res in resolutions:
            if res.status == EntityResolutionStatus.AMBIGUOUS:
                uncertain.append(f"Ambiguity: {res.explanation}")
            elif res.status == EntityResolutionStatus.UNRESOLVED:
                uncertain.append(f"Unresolved: {res.explanation}")

        # Summary
        summary = (
            f"Multi-source intelligence fusion processed {len(normalized_obs)} observation(s) across "
            f"{len(set(o.source_id for o in normalized_obs))} sensor(s) resulting in {len(fused_obs)} fused track(s). "
            f"Corroboration score: {corroboration.corroboration_score:.2f} ({corroboration.independent_source_count} independent groups). "
            f"Detected {len(conflicts)} contradiction(s)."
        )

        epistemic_ledger = {
            "OBSERVED": observed,
            "FUSED": fused,
            "INFERRED": inferred,
            "UNCERTAIN": uncertain,
        }

        return FusionAssessment(
            summary=summary,
            observed=observed,
            fused=fused,
            inferred=inferred,
            uncertain=uncertain,
            epistemic_ledger=epistemic_ledger,
        )
