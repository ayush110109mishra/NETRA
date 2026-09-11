"""
Master Prediction Engine for NETRA Phase 6.
Coordinates feature extraction, temporal state modeling, trend analysis,
multi-strategy forecasting evaluation, and explainable intelligence synthesis.
"""

from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, List, Optional
import logging

from config import NetraConfig, default_config
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityProfile
from models.predictive_intelligence import (
    DataSufficiency,
    ForecastHorizon,
    ForecastLifecycleState,
    ForecastState,
    PredictionAnalyzeRequest,
    PredictionAnalyzeResponse,
    PredictiveForecast,
    PredictiveTarget,
    TrendMetrics,
)
from prediction.feature_engineering import FeatureExtractor
from prediction.temporal_state import TemporalStateManager
from prediction.trend import TrendEngine
from prediction.forecasting import ForecastingEngine
from prediction.explainability import PredictionExplainer

logger = logging.getLogger("netra.prediction.engine")


class PredictionEngine:
    """
    Core engine orchestrating Phase 6 predictive intelligence pipelines.
    Guarantees strict determinism, uncertainty quantification, and epistemic explainability.
    """

    def __init__(self, config: Optional[NetraConfig] = None):
        self.config = config or default_config
        self.temporal_state_mgr = TemporalStateManager()
        self.trend_engine = TrendEngine(self.config)
        self.forecasting_engine = ForecastingEngine(self.config)
        self.feature_extractor = FeatureExtractor()
        self.explainer = PredictionExplainer()

    def _determine_current_state(
        self,
        target: PredictiveTarget,
        events: List[CanonicalEvent],
        entity: Optional[CanonicalEntity] = None,
        anomaly_assessment: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Determines the baseline current state label for the selected analytical target."""
        if not events:
            return "UNKNOWN"

        last_event = events[-1]
        attrs = last_event.attributes or {}

        if target == PredictiveTarget.ACTIVITY_STATE:
            act = float(attrs.get("activity_level", 0.5))
            if act <= 0.25:
                return "LOW"
            elif act <= 0.60:
                return "NOMINAL"
            elif act <= 0.85:
                return "ELEVATED"
            return "CRITICAL"

        elif target == PredictiveTarget.ANOMALY_STATE:
            if anomaly_assessment:
                anom_score = float(anomaly_assessment.get("anomaly_score", 0.0))
                if anom_score > 0.75:
                    return "HIGH_ANOMALY"
                elif anom_score > 0.45:
                    return "ANOMALOUS"
                return "NOMINAL"
            # Fallback to event attributes
            anom = float(attrs.get("anomaly_score", 0.2))
            return "ANOMALOUS" if anom > 0.50 else "NOMINAL"

        elif target == PredictiveTarget.RISK_TREND:
            if entity and entity.risk_level:
                return entity.risk_level
            if anomaly_assessment and "risk_score" in anomaly_assessment:
                r_score = float(anomaly_assessment["risk_score"])
                if r_score > 0.8:
                    return "CRITICAL"
                elif r_score > 0.6:
                    return "HIGH"
                elif r_score > 0.35:
                    return "MEDIUM"
                return "LOW"
            return "MEDIUM"

        elif target == PredictiveTarget.SPATIAL_STATE:
            speed = float(attrs.get("speed", 30.0))
            if speed < 5.0:
                return "STATIONARY"
            elif speed < 25.0:
                return "LOITERING"
            return "DIRECTED_TRANSIT"

        elif target == PredictiveTarget.EVENT_TYPE_RECURRENCE:
            return last_event.event_type

        elif target == PredictiveTarget.BEHAVIORAL_STATE:
            if entity and entity.behavioral_profile and "primary_behavior" in entity.behavioral_profile:
                return str(entity.behavioral_profile["primary_behavior"])
            return "NOMINAL"

        return "NOMINAL"

    def _map_metric_key(self, target: PredictiveTarget) -> str:
        """Maps predictive target dimension to time-series attribute key."""
        if target == PredictiveTarget.ACTIVITY_STATE:
            return "activity_level"
        elif target == PredictiveTarget.ANOMALY_STATE:
            return "anomaly_score"
        elif target == PredictiveTarget.RISK_TREND:
            return "risk_score"
        elif target == PredictiveTarget.SPATIAL_STATE:
            return "speed"
        elif target == PredictiveTarget.EVENT_TYPE_RECURRENCE:
            return "activity_level"
        elif target == PredictiveTarget.BEHAVIORAL_STATE:
            return "activity_level"
        return "activity_level"

    def analyze(
        self,
        request: PredictionAnalyzeRequest,
        entity: Optional[CanonicalEntity] = None,
        events: Optional[List[CanonicalEvent]] = None,
        profile: Optional[EntityProfile] = None,
        anomaly_assessment: Optional[Dict[str, Any]] = None,
        fused_observations: Optional[List[Any]] = None,
        conflicts_count: int = 0,
    ) -> PredictionAnalyzeResponse:
        """
        Executes end-to-end predictive intelligence analysis for a single entity and target.
        """
        eval_time = request.as_of or datetime.now(timezone.utc)
        if eval_time.tzinfo is None:
            eval_time = eval_time.replace(tzinfo=timezone.utc)

        # 1. Temporal filtering up to evaluation time to prevent future leakage
        raw_events = events or []
        filtered_events = [
            e for e in raw_events
            if (e.timestamp.tzinfo is None and e.timestamp.replace(tzinfo=timezone.utc) <= eval_time)
            or (e.timestamp.tzinfo is not None and e.timestamp <= eval_time)
        ]
        sorted_events = sorted(filtered_events, key=lambda e: e.timestamp)
        sample_count = len(sorted_events)

        # 2. Metric Sequence & Trend Analysis
        metric_key = self._map_metric_key(request.target)
        sequence = self.temporal_state_mgr.build_sequence(
            entity_id=request.entity_id,
            events=sorted_events,
            metric_key=metric_key,
        )
        trend = self.trend_engine.analyze_trend(sequence)

        # 3. Multi-Phase Feature Extraction
        features = self.feature_extractor.extract_features(
            events=sorted_events,
            entity=entity,
            profile=profile,
            anomaly_assessment=anomaly_assessment,
            fused_observations=fused_observations,
        )

        # 4. Multi-Source Fusion Quality Metrics
        fusion_conf = 0.80
        evidence_quality = 0.85
        conflict_severity = min(1.0, conflicts_count * 0.25)

        if fused_observations:
            confs = [getattr(fo, "fusion_confidence", 0.75) for fo in fused_observations]
            if confs:
                fusion_conf = sum(confs) / len(confs)
            agrees = [getattr(fo, "agreement_score", 0.80) for fo in fused_observations]
            if agrees:
                evidence_quality = sum(agrees) / len(agrees)

        # 5. Baseline Current State
        current_state = self._determine_current_state(
            target=request.target,
            events=sorted_events,
            entity=entity,
            anomaly_assessment=anomaly_assessment,
        )

        # 6. Forecasting Strategy Execution & Calibration
        forecast, candidate_map = self.forecasting_engine.generate_forecast(
            target=request.target,
            current_state=current_state,
            trend=trend,
            horizon=request.horizon,
            sample_count=sample_count,
            evidence_quality=evidence_quality,
            fusion_confidence=fusion_conf,
            fusion_conflict_severity=conflict_severity,
        )

        # 7. Explainability & Five-Tier Epistemic Synthesis
        explanation, assessment = self.explainer.explain_forecast(
            forecast=forecast,
            trend=trend,
            features=features,
            observed_events_count=sample_count,
            conflicts_count=conflicts_count,
        )

        # Deterministic Prediction Run Identifier
        time_token = int(eval_time.timestamp())
        raw_seed = f"{request.entity_id}:{request.target.value}:{request.horizon.value}:{time_token}:{sample_count}"
        h_suffix = hashlib.sha256(raw_seed.encode("utf-8")).hexdigest()[:8]
        pred_id = f"PRD-{request.entity_id}-{request.target.value}-{request.horizon.value}-{h_suffix}"

        provenance = {
            "prediction_id": pred_id,
            "entity_id": request.entity_id,
            "engine_version": self.config.version,
            "as_of": eval_time.isoformat(),
            "sample_count": sample_count,
            "feature_count": len(features),
            "strategies_evaluated": list(candidate_map.keys()),
            "candidate_agreement": forecast.model_agreement,
            "fused_sources_active": len(fused_observations or []),
            "active_conflicts": conflicts_count,
        }

        return PredictionAnalyzeResponse(
            schema_version="phase6-v1",
            prediction_id=pred_id,
            status="SUCCESS",
            entity_id=request.entity_id,
            target=request.target,
            horizon=request.horizon,
            forecast=forecast,
            assessment=assessment,
            features=features,
            trend_metrics=trend,
            explanation=explanation,
            candidate_model_forecasts=candidate_map,
            provenance=provenance,
        )
