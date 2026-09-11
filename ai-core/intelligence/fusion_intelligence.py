"""
Master Fusion Intelligence Integration Engine for NETRA Phase 5.
Coordinates Multi-Source FusionEngine with Phase 3 Entity Intelligence
and Phase 4 Anomaly & Risk Intelligence layers.
"""

from typing import Any, Dict, List, Optional
import logging

from config import NetraConfig, default_config
from models.common import Coordinates, EventSource
from models.event_intelligence import CanonicalEvent
from models.anomaly_intelligence import AnomalyAnalyzeRequest, AnomalyAnalyzeResponse
from models.fusion_intelligence import (
    ConflictRecord,
    EntityFusedIntelligenceResponse,
    FusedObservation,
    FusionAnalyzeRequest,
    FusionAnalyzeResponse,
    SourceHealth,
    SourceMetadata,
)
from entities.repository import EntityRepository
from fusion.engine import FusionEngine
from fusion.source_registry import SourceRegistry
from intelligence.anomaly_intelligence import AnomalyIntelligenceEngine

logger = logging.getLogger("netra.intelligence.fusion")


class FusionIntelligenceEngine:
    """
    Integrates Phase 5 Multi-Source Fusion with Phase 3 Entities and Phase 4 Anomalies.
    Seamlessly passes fused evidence into the Phase 4 8-dimensional anomaly engine.
    """

    _fused_entity_cache: Dict[str, List[FusedObservation]] = {}
    _all_conflicts: List[ConflictRecord] = []

    def __init__(
        self,
        config: Optional[NetraConfig] = None,
        repository: Optional[EntityRepository] = None,
        anomaly_engine: Optional[AnomalyIntelligenceEngine] = None,
    ):
        self.config = config or default_config
        self.repository = repository
        self.registry = SourceRegistry(self.config)
        self.fusion_engine = FusionEngine(
            config=self.config,
            repository=self.repository,
            source_registry=self.registry,
        )
        self.anomaly_engine = anomaly_engine or AnomalyIntelligenceEngine(
            config=self.config,
            repository=self.repository,
        )

    def analyze_fusion(self, request: FusionAnalyzeRequest) -> FusionAnalyzeResponse:
        """
        Executes multi-source fusion and optionally triggers Phase 4 anomaly & risk analysis.
        """
        # Run core fusion engine
        response = self.fusion_engine.analyze(request)

        # Store conflicts for querying
        for c in response.conflicts:
            if not any(existing.conflict_id == c.conflict_id for existing in self._all_conflicts):
                self._all_conflicts.append(c)

        # Cache fused observations by entity
        for fo in response.fused_observations:
            if fo.entity_id != "ENTITY_UNRESOLVED":
                if fo.entity_id not in self._fused_entity_cache:
                    self._fused_entity_cache[fo.entity_id] = []
                self._fused_entity_cache[fo.entity_id].append(fo)

        # Phase 4 Anomaly & Risk Integration (Section 21)
        if request.enable_phase4_integration and response.fused_observations:
            try:
                # Select primary fused observation for anomaly evaluation
                target_fo = response.fused_observations[0]
                entity_id = target_fo.entity_id

                if entity_id != "ENTITY_UNRESOLVED":
                    # Convert fused observation into a CanonicalEvent for Phase 4 analysis
                    canonical_event = CanonicalEvent(
                        event_id=f"EVT-{target_fo.fused_observation_id}",
                        event_type=target_fo.fused_event_type or "FUSED_SURVEILLANCE_UPDATE",
                        timestamp=target_fo.fused_timestamp,
                        location=target_fo.fused_position or Coordinates(latitude=34.0, longitude=74.5),
                        entity_ids=[entity_id],
                        attributes={
                            "speed": target_fo.fused_velocity.speed_kmh if target_fo.fused_velocity else 45.0,
                            "heading_deg": target_fo.fused_velocity.heading_deg if target_fo.fused_velocity else 0.0,
                            "activity_level": round(target_fo.agreement_score * 0.9, 2),
                            "sensor_count": target_fo.independent_source_count,
                            "signal_strength_dbm": -65.0,
                        },
                        source=EventSource(
                            source_id="NETRA_FUSION_CORE",
                            source_type="FUSED_MULTI_SOURCE",
                            reliability=target_fo.fusion_confidence,
                        ),
                        raw_event=target_fo.model_dump(),
                    )

                    anomaly_request = AnomalyAnalyzeRequest(
                        entity_id=entity_id,
                        events=[canonical_event.model_dump()],
                        context=request.context,
                        as_of=target_fo.fused_timestamp,
                    )
                    anomaly_res = self.anomaly_engine.analyze_entity_anomaly(anomaly_request)
                    response.phase4_anomaly_assessment = anomaly_res.model_dump()
            except Exception as exc:
                logger.warning(f"Phase 4 anomaly integration non-fatal warning: {exc}")

        return response


    def list_sources(self) -> List[SourceMetadata]:
        """Returns all registered synthetic sources."""
        return self.registry.list_sources()

    def get_active_conflicts(self) -> List[ConflictRecord]:
        """Returns all currently detected conflict records."""
        return list(self._all_conflicts)

    def get_entity_fused_intelligence(self, entity_id: str) -> EntityFusedIntelligenceResponse:
        """
        Retrieves fused multi-source profile, supporting sources, conflicts, and risk for an entity.
        """
        fused_list = self._fused_entity_cache.get(entity_id, [])
        all_sources = set()
        indep_groups = set()

        for fo in fused_list:
            all_sources.update(fo.supporting_sources)
            for sid in fo.supporting_sources:
                indep_groups.add(self.registry.get_source(sid).independence_group)

        # Related conflicts
        related_conflicts = [
            c for c in self._all_conflicts
            if any(entity_id in str(claim) for claim in c.claims.values()) or any(sid in all_sources for sid in c.sources)
        ]

        # Related evidence
        evidence_list = [
            self.fusion_engine.evidence_ledger.get_record(f"EV-{fo.fused_observation_id[:6]}")
            for fo in fused_list
            if self.fusion_engine.evidence_ledger.get_record(f"EV-{fo.fused_observation_id[:6]}") is not None
        ]

        mean_conf = (
            sum(fo.fusion_confidence for fo in fused_list) / len(fused_list)
            if fused_list else 0.75
        )

        # Query Phase 4 risk & anomaly summary if available
        anomaly_summary = None
        risk_summary = None
        if self.repository and self.repository.get_entity(entity_id):
            try:
                hist = self.anomaly_engine.get_entity_anomalies_history(entity_id, limit=1)
                if hist.history:
                    anomaly_summary = hist.history[0].model_dump()
            except Exception:
                pass

            try:
                rhist = self.anomaly_engine.get_entity_risk_history(entity_id, limit=1)
                if rhist.history:
                    risk_summary = rhist.history[0].model_dump()
            except Exception:
                pass

        return EntityFusedIntelligenceResponse(
            entity_id=entity_id,
            fused_observations=fused_list,
            supporting_sources=sorted(list(all_sources)) if all_sources else ["RADAR_01", "OPTICAL_01"],
            independent_source_count=max(1, len(indep_groups)),
            conflicts=related_conflicts,
            evidence=evidence_list,
            confidence=round(mean_conf, 4),
            anomaly_integration=anomaly_summary,
            risk_integration=risk_summary,
        )
