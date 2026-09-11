"""
Forecasting Engine for NETRA Phase 6.
Coordinates strategy candidate evaluation, cold-start gating, model agreement,
probability and uncertainty estimation, and produces final PredictiveForecast instances.
"""

from typing import Any, Dict, List, Optional, Tuple
import logging

from config import NetraConfig, default_config, PredictionGatingConfig
from models.predictive_intelligence import (
    DataSufficiency,
    ForecastHorizon,
    ForecastInterval,
    ForecastLifecycleState,
    ForecastState,
    PredictiveForecast,
    PredictiveTarget,
    TrendMetrics,
)
from prediction.baseline_forecast import (
    ForecastStrategy,
    PersistenceForecastStrategy,
    TrendForecastStrategy,
    RecurrenceForecastStrategy,
)
from prediction.probability import ProbabilityEstimator
from prediction.uncertainty import UncertaintyEstimator
from prediction.calibration import ModelCalibrator

logger = logging.getLogger("netra.prediction.forecasting")


class ForecastingEngine:
    """
    Evaluates multi-strategy candidate projections and synthesizes
    evidence-calibrated, probabilistic forecasts.
    """

    def __init__(self, config: Optional[NetraConfig] = None):
        self.config = config or default_config
        self.gating: PredictionGatingConfig = self.config.prediction_gating

        # Initialize forecasting strategies
        self.persistence_strategy = PersistenceForecastStrategy()
        self.trend_strategy = TrendForecastStrategy()
        self.recurrence_strategy = RecurrenceForecastStrategy()

        self.prob_estimator = ProbabilityEstimator(self.config)
        self.unc_estimator = UncertaintyEstimator(self.config)

    def generate_forecast(
        self,
        target: PredictiveTarget,
        current_state: str,
        trend: TrendMetrics,
        horizon: ForecastHorizon,
        sample_count: int,
        evidence_quality: float = 0.80,
        fusion_confidence: float = 0.75,
        fusion_conflict_severity: float = 0.0,
    ) -> Tuple[PredictiveForecast, Dict[str, str]]:
        """
        Executes strategy evaluation, cold start checks, probability and uncertainty estimation.
        Returns (PredictiveForecast, candidate_forecasts_map).
        """
        # 1. Cold Start and Sufficiency Evaluation (Section 17)
        if sample_count < self.gating.cold_start_threshold:
            sufficiency = DataSufficiency.INSUFFICIENT
            is_cold_start = True
            forecast_state = ForecastState.UNKNOWN.value
            probability = 0.20
            confidence = 0.25
            uncertainty = 0.85
            interval = ForecastInterval(lower=0.0, upper=0.40, interval_type="heuristic")
            candidate_map = {
                "persistence": ForecastState.UNKNOWN.value,
                "trend": ForecastState.UNKNOWN.value,
                "recurrence": ForecastState.UNKNOWN.value,
            }

            forecast = PredictiveForecast(
                target=target,
                current_state=current_state,
                forecast_state=forecast_state,
                horizon=horizon,
                probability=probability,
                confidence=confidence,
                uncertainty=uncertainty,
                interval=interval,
                model_agreement=1.0,
                strategy_used="COLD_START_FALLBACK",
                data_sufficiency=sufficiency,
                lifecycle_state=ForecastLifecycleState.ACTIVE,
            )
            return forecast, candidate_map

        is_cold_start = False
        if sample_count <= self.gating.limited_history_threshold:
            sufficiency = DataSufficiency.LIMITED
        else:
            sufficiency = DataSufficiency.SUFFICIENT

        # 2. Candidate Strategy Forecasts
        p_state, p_conf = self.persistence_strategy.forecast(target, current_state, trend, horizon, sample_count)
        t_state, t_conf = self.trend_strategy.forecast(target, current_state, trend, horizon, sample_count)
        r_state, r_conf = self.recurrence_strategy.forecast(target, current_state, trend, horizon, sample_count)

        candidate_map = {
            "persistence": p_state,
            "trend": t_state,
            "recurrence": r_state,
        }

        # 3. Model Agreement
        model_agreement = ModelCalibrator.calculate_model_agreement(candidate_map)

        # 4. Primary Strategy Selection
        if target == PredictiveTarget.EVENT_TYPE_RECURRENCE:
            chosen_state = r_state
            chosen_strategy_name = "RecurrenceForecastStrategy"
            base_strategy_conf = r_conf
        elif trend.strength >= 0.35 and trend.persistence >= 0.55:
            chosen_state = t_state
            chosen_strategy_name = "TrendForecastStrategy"
            base_strategy_conf = t_conf
        else:
            chosen_state = p_state
            chosen_strategy_name = "PersistenceForecastStrategy"
            base_strategy_conf = p_conf

        # 5. Probability Estimation
        prob, _ = self.prob_estimator.estimate_probability(
            trend=trend,
            evidence_quality=evidence_quality,
            fusion_confidence=fusion_confidence,
            data_completeness=1.0 if sufficiency == DataSufficiency.SUFFICIENT else 0.60,
            model_agreement=model_agreement,
        )

        # 6. Uncertainty & Interval Estimation
        unc, interval = self.unc_estimator.estimate_uncertainty(
            sample_count=sample_count,
            trend=trend,
            probability=prob,
            fusion_conflict_severity=fusion_conflict_severity,
            model_agreement=model_agreement,
            is_cold_start=is_cold_start,
        )

        # 7. Confidence Calculation
        raw_conf = (
            (0.40 * base_strategy_conf)
            + (0.35 * (1.0 - unc))
            + (0.25 * fusion_confidence)
        )
        if model_agreement >= 0.85:
            raw_conf += 0.05
        elif model_agreement < 0.60:
            raw_conf -= 0.10

        if sufficiency == DataSufficiency.LIMITED:
            raw_conf = min(raw_conf, 0.55)

        bounded_conf = round(max(0.15, min(0.95, raw_conf)), 4)

        forecast = PredictiveForecast(
            target=target,
            current_state=current_state,
            forecast_state=chosen_state,
            horizon=horizon,
            probability=prob,
            confidence=bounded_conf,
            uncertainty=unc,
            interval=interval,
            model_agreement=model_agreement,
            strategy_used=chosen_strategy_name,
            data_sufficiency=sufficiency,
            lifecycle_state=ForecastLifecycleState.ACTIVE,
        )

        return forecast, candidate_map
