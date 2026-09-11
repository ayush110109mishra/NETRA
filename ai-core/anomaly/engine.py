"""
Master Anomaly Engine for NETRA Phase 4 Anomaly Intelligence.
Orchestrates all 8 analytical dimensions, aggregates scores, computes mathematical attribution,
analyzes persistence and trends, calibrates confidence, and tracks anomaly lifecycle.
"""

from typing import List, Dict, Optional, Any, Tuple
from config import NetraConfig, default_config
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from models.anomaly_intelligence import (
    AnomalySummary,
    AnomalyLifecycle,
    MultiDimensionalScores,
    DimensionScoreItem,
    AnomalyAttribution,
    AnomalyTrend,
    AnomalyPersistence,
    EvidenceLineage,
)

from anomaly.temporal import TemporalAnomalyDetector
from anomaly.spatial import SpatialAnomalyDetector
from anomaly.kinematic import KinematicAnomalyDetector
from anomaly.frequency import FrequencyAnomalyDetector
from anomaly.event_type import EventTypeAnomalyDetector
from anomaly.behavioral import BehavioralAnomalyDetector
from anomaly.relational import RelationalAnomalyDetector
from anomaly.contextual import ContextualAnomalyDetector
from anomaly.aggregation import AnomalyAggregator
from anomaly.attribution import AnomalyAttributor
from anomaly.trend import AnomalyTrendAnalyzer
from anomaly.persistence import AnomalyPersistenceAnalyzer
from anomaly.calibration import ConfidenceCalibrator


class AnomalyEngine:
    """Master orchestrator for Phase 4 multi-dimensional anomaly detection."""

    def __init__(self, config: Optional[NetraConfig] = None):
        self.config = config or default_config
        self.aggregator = AnomalyAggregator(
            weights=self.config.anomaly_weights,
            thresholds=self.config.anomaly_thresholds,
        )
        self.attributor = AnomalyAttributor(weights=self.config.anomaly_weights)
        self.persistence_analyzer = AnomalyPersistenceAnalyzer(config=self.config.persistence)

    def evaluate_entity_anomaly(
        self,
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        baseline: Optional[EntityBehaviorProfile] = None,
        context: Optional[Dict[str, Any]] = None,
        previous_score: Optional[float] = None,
        historical_scores: Optional[List[float]] = None,
        time_delta_hours: Optional[float] = None,
    ) -> Tuple[
        AnomalySummary,
        MultiDimensionalScores,
        Dict[str, DimensionScoreItem],
        AnomalyAttribution,
        AnomalyTrend,
        AnomalyPersistence,
        Dict[str, Any],
        EvidenceLineage,
    ]:
        """
        Execute full multi-dimensional anomaly assessment for an entity.
        Returns complete suite of Phase 4 anomaly assessment objects.
        """
        # 1. Execute all 8 dimensional detectors
        dim_scores: Dict[str, DimensionScoreItem] = {
            "temporal": TemporalAnomalyDetector.detect(entity, events, baseline, context),
            "spatial": SpatialAnomalyDetector.detect(entity, events, baseline, context),
            "kinematic": KinematicAnomalyDetector.detect(entity, events, baseline, context),
            "frequency": FrequencyAnomalyDetector.detect(entity, events, baseline, context),
            "event_type": EventTypeAnomalyDetector.detect(entity, events, baseline, context),
            "behavioral": BehavioralAnomalyDetector.detect(entity, events, baseline, context),
            "relational": RelationalAnomalyDetector.detect(entity, events, baseline, context),
            "contextual": ContextualAnomalyDetector.detect(entity, events, baseline, context),
        }

        # 2. Multi-dimensional aggregation
        aggregate_score, level, multi_dim = self.aggregator.aggregate(dim_scores)

        # 3. Factor attribution
        attribution = self.attributor.attribute(dim_scores)

        # 4. Trend progression
        trend = AnomalyTrendAnalyzer.analyze(
            current_score=aggregate_score,
            previous_score=previous_score,
            time_delta_hours=time_delta_hours,
        )

        # 5. Persistence across historical evaluation windows
        eval_history = list(historical_scores) if historical_scores else []
        if not eval_history or eval_history[-1] != aggregate_score:
            eval_history.append(aggregate_score)

        persistence = self.persistence_analyzer.analyze(
            history_scores=eval_history,
            trend=trend,
        )

        # 6. Decoupled Confidence Calibration
        dim_confidences = [item.confidence for item in dim_scores.values()]
        anom_evidence_ids = []
        for item in dim_scores.values():
            if item.score >= 0.25:
                anom_evidence_ids.extend(item.evidence_event_ids)

        calibrated_conf, conf_level, conf_audit = ConfidenceCalibrator.calibrate(
            entity=entity,
            events=events,
            dimension_confidences=dim_confidences,
            evidence_event_ids=anom_evidence_ids,
        )

        # 7. Lifecycle Determination
        if aggregate_score >= 0.25:
            if persistence.state.value == "PERSISTENT":
                lifecycle = AnomalyLifecycle.PERSISTING
            elif persistence.state.value == "DECLINING":
                lifecycle = AnomalyLifecycle.RESOLVING
            elif persistence.state.value == "ESCALATING":
                lifecycle = AnomalyLifecycle.ACTIVE
            else:
                lifecycle = AnomalyLifecycle.DETECTED
        else:
            if previous_score is not None and previous_score >= 0.25:
                lifecycle = AnomalyLifecycle.RESOLVED
            else:
                lifecycle = AnomalyLifecycle.RESOLVED

        summary = AnomalySummary(
            score=aggregate_score,
            level=level,
            state=persistence.state,
            confirmation=conf_level,
            lifecycle=lifecycle,
        )

        # 8. Assemble Evidence Lineage
        all_evidence_ids = []
        for item in dim_scores.values():
            all_evidence_ids.extend(item.evidence_event_ids)
        for e in events:
            all_evidence_ids.append(e.event_id)
        unique_evidence_ids = list(dict.fromkeys(all_evidence_ids))

        # Collect source reliabilities
        source_rel_map = {}
        for e in events:
            if hasattr(e, "source") and hasattr(e.source, "source_type"):
                src = str(e.source.source_type)
                rel = float(getattr(e.source, "reliability", 0.80))
                source_rel_map[src] = rel

        evidence = EvidenceLineage(
            event_ids=unique_evidence_ids,
            entity_ids=[entity.entity_id] + list(getattr(entity, "associated_entity_ids", None) or []),
            baseline_window={
                "sample_count": baseline.sample_count if baseline else 0,
                "status": baseline.baseline_status if baseline else "NONE",
            },
            analysis_window={
                "event_count": len(events),
                "first_event": events[0].timestamp.isoformat() if events else None,
                "last_event": events[-1].timestamp.isoformat() if events else None,
            },
            source_reliability=source_rel_map,
        )

        confidence_bundle = {
            "calibrated_confidence": calibrated_conf,
            "confirmation_level": conf_level.value,
            "audit": conf_audit,
        }

        return (
            summary,
            multi_dim,
            dim_scores,
            attribution,
            trend,
            persistence,
            confidence_bundle,
            evidence,
        )
