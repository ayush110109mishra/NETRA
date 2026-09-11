"""
Master Predictive Intelligence Integration Engine for NETRA Phase 6.
Coordinates PredictionEngine with Phase 3 Entity Intelligence,
Phase 4 Anomaly & Risk Intelligence, and Phase 5 Multi-Source Fusion.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import logging

from config import NetraConfig, default_config
from models.common import Coordinates, EventSource
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityProfile
from models.predictive_intelligence import (
    EntityForecastResponse,
    EntityPredictionsHistoryResponse,
    ForecastEvaluationItem,
    ForecastEvaluationResponse,
    ForecastHorizon,
    PredictiveForecast,
    PredictionAnalyzeRequest,
    PredictionAnalyzeResponse,
    PredictiveTarget,
)
from entities.repository import EntityRepository
from intelligence.anomaly_intelligence import AnomalyIntelligenceEngine
from intelligence.fusion_intelligence import FusionIntelligenceEngine
from prediction.engine import PredictionEngine

logger = logging.getLogger("netra.intelligence.prediction")


class PredictiveIntelligenceEngine:
    """
    Master coordinator for Phase 6 Predictive Intelligence.
    Integrates entity state, multi-source fused feeds, anomaly scores, and generates
    probabilistic forecasts with uncertainty bounds and epistemic explainability.
    """

    _entity_forecast_cache: Dict[str, List[PredictionAnalyzeResponse]] = {}
    _synthetic_evaluations: List[ForecastEvaluationItem] = []

    def __init__(
        self,
        config: Optional[NetraConfig] = None,
        repository: Optional[EntityRepository] = None,
        anomaly_engine: Optional[AnomalyIntelligenceEngine] = None,
        fusion_engine: Optional[FusionIntelligenceEngine] = None,
    ):
        self.config = config or default_config
        self.repository = repository
        self.anomaly_engine = anomaly_engine or AnomalyIntelligenceEngine(
            config=self.config,
            repository=self.repository,
        )
        self.fusion_engine = fusion_engine or FusionIntelligenceEngine(
            config=self.config,
            repository=self.repository,
            anomaly_engine=self.anomaly_engine,
        )
        self.prediction_engine = PredictionEngine(self.config)

    def analyze_prediction(self, request: PredictionAnalyzeRequest) -> PredictionAnalyzeResponse:
        """
        Executes predictive intelligence analysis for an entity.
        Fuses entity telemetry, Phase 4 anomaly history, and Phase 5 multi-source observations.
        """
        entity_id = request.entity_id
        entity: Optional[CanonicalEntity] = None
        events: List[CanonicalEvent] = []
        profile: Optional[EntityProfile] = None

        # 1. Resolve Entity and Events
        if self.repository:
            entity = self.repository.get_entity(entity_id)
            if entity:
                profile = self.repository.get_entity_profile(entity_id)
                events = self.repository.get_entity_events(entity_id) or []

        # Custom events override (useful for synthetic scenarios and tests)
        if request.custom_events:
            custom_events: List[CanonicalEvent] = []
            for ev_data in request.custom_events:
                if isinstance(ev_data, CanonicalEvent):
                    custom_events.append(ev_data)
                elif isinstance(ev_data, dict):
                    # Handle raw dict event parsing
                    ts = ev_data.get("timestamp")
                    if isinstance(ts, str):
                        ts = datetime.fromisoformat(ts)
                    elif ts is None:
                        ts = request.as_of or datetime.now(timezone.utc)

                    loc = ev_data.get("location")
                    if isinstance(loc, dict):
                        loc = Coordinates(**loc)
                    elif not isinstance(loc, Coordinates):
                        loc = Coordinates(latitude=34.0, longitude=74.5)

                    src = ev_data.get("source")
                    if isinstance(src, dict):
                        src = EventSource(**src)
                    elif not isinstance(src, EventSource):
                        src = EventSource(
                            source_id="SIM_SYNTHETIC",
                            source_type="SYNTHETIC_OVERRIDE",
                            reliability=0.90,
                        )

                    custom_events.append(
                        CanonicalEvent(
                            event_id=ev_data.get("event_id", f"EVT-CUSTOM-{len(custom_events)}"),
                            event_type=ev_data.get("event_type", "GENERIC_OBSERVATION"),
                            timestamp=ts,
                            location=loc,
                            entity_ids=[entity_id],
                            attributes=ev_data.get("attributes", {}),
                            source=src,
                        )
                    )
            events = custom_events

        # 2. Multi-Source Fusion Feed Integration (Phase 5)
        fused_observations: List[Any] = []
        conflicts_count = 0
        if request.include_phase5_fusion and self.fusion_engine:
            try:
                fusion_summary = self.fusion_engine.get_entity_fused_intelligence(entity_id)
                if fusion_summary:
                    fused_observations = fusion_summary.fused_observations
                    conflicts_count = len(fusion_summary.conflicts)
            except Exception as exc:
                logger.warning(f"Phase 5 fusion integration non-fatal notice: {exc}")

        # 3. Anomaly & Risk Integration (Phase 4)
        anomaly_assessment: Optional[Dict[str, Any]] = None
        if self.anomaly_engine:
            try:
                hist = self.anomaly_engine.get_entity_anomalies_history(entity_id, limit=1)
                if hist.history:
                    anomaly_assessment = hist.history[0].model_dump()
            except Exception:
                pass

        # 4. Run Master Prediction Engine
        response = self.prediction_engine.analyze(
            request=request,
            entity=entity,
            events=events,
            profile=profile,
            anomaly_assessment=anomaly_assessment,
            fused_observations=fused_observations,
            conflicts_count=conflicts_count,
        )

        # 5. Cache Generated Prediction
        if entity_id not in self._entity_forecast_cache:
            self._entity_forecast_cache[entity_id] = []
        self._entity_forecast_cache[entity_id].append(response)

        return response

    def get_entity_predictions(self, entity_id: str, limit: int = 50) -> EntityPredictionsHistoryResponse:
        """Retrieves chronological history of generated predictions for an entity."""
        cached = self._entity_forecast_cache.get(entity_id, [])
        history = cached[-limit:]
        return EntityPredictionsHistoryResponse(
            entity_id=entity_id,
            predictions=history,
            metadata={
                "total_cached": len(cached),
                "returned_count": len(history),
            },
        )

    def get_entity_forecast(
        self,
        entity_id: str,
        as_of: Optional[datetime] = None,
    ) -> EntityForecastResponse:
        """
        Generates or retrieves multi-target operational forecast across all 6 core targets.
        """
        eval_time = as_of or datetime.now(timezone.utc)
        targets = [
            PredictiveTarget.ACTIVITY_STATE,
            PredictiveTarget.ANOMALY_STATE,
            PredictiveTarget.RISK_TREND,
            PredictiveTarget.SPATIAL_STATE,
            PredictiveTarget.EVENT_TYPE_RECURRENCE,
            PredictiveTarget.BEHAVIORAL_STATE,
        ]

        current_forecasts: Dict[str, PredictiveForecast] = {}
        confs: List[float] = []
        uncs: List[float] = []

        for target in targets:
            req = PredictionAnalyzeRequest(
                entity_id=entity_id,
                target=target,
                horizon=ForecastHorizon.SHORT,
                as_of=eval_time,
                include_phase5_fusion=True,
            )
            res = self.analyze_prediction(req)
            current_forecasts[target.value] = res.forecast
            confs.append(res.forecast.confidence)
            uncs.append(res.forecast.uncertainty)

        mean_conf = sum(confs) / len(confs) if confs else 0.50
        mean_unc = sum(uncs) / len(uncs) if uncs else 0.50

        return EntityForecastResponse(
            entity_id=entity_id,
            current_forecasts=current_forecasts,
            overall_confidence=round(mean_conf, 4),
            overall_uncertainty=round(mean_unc, 4),
            as_of=eval_time,
        )

    def evaluate_predictions(
        self,
        evaluations: Optional[List[ForecastEvaluationItem]] = None,
    ) -> ForecastEvaluationResponse:
        """
        Tracks and reports synthetic accuracy evaluation metrics (MAE and directional accuracy).
        """
        if evaluations:
            for item in evaluations:
                self._synthetic_evaluations.append(item)

        total = len(self._synthetic_evaluations)
        if total == 0:
            return ForecastEvaluationResponse(
                total_evaluated=0,
                mean_absolute_error=0.0,
                directional_accuracy=1.0,
                evaluations=[],
            )

        mae = sum(item.absolute_error for item in self._synthetic_evaluations) / total
        correct_dir = sum(1 for item in self._synthetic_evaluations if item.is_directionally_correct)
        dir_acc = correct_dir / total

        return ForecastEvaluationResponse(
            total_evaluated=total,
            mean_absolute_error=round(mae, 4),
            directional_accuracy=round(dir_acc, 4),
            evaluations=list(self._synthetic_evaluations),
        )
