"""
Deterministic Baseline Forecasting Strategies for NETRA Phase 6.
Provides modular, interpretable forecasting implementations (Persistence, Trend, Recurrence)
under an extensible ForecastStrategy interface.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, Optional
import logging

from models.predictive_intelligence import (
    ForecastHorizon,
    ForecastState,
    PredictiveTarget,
    TrendMetrics,
)

logger = logging.getLogger("netra.prediction.baseline_forecast")


class ForecastStrategy(ABC):
    """Abstract interface for deterministic and future ML forecasting models."""

    @abstractmethod
    def forecast(
        self,
        target: PredictiveTarget,
        current_state: str,
        trend: TrendMetrics,
        horizon: ForecastHorizon,
        sample_count: int,
    ) -> Tuple[str, float]:
        """
        Produces projected future state and base strategy confidence.
        Returns (forecast_state, strategy_confidence).
        """
        pass


class PersistenceForecastStrategy(ForecastStrategy):
    """
    Inertia-based baseline: projects continuation of the current state,
    decaying confidence with volatility and longer horizons.
    """

    def forecast(
        self,
        target: PredictiveTarget,
        current_state: str,
        trend: TrendMetrics,
        horizon: ForecastHorizon,
        sample_count: int,
    ) -> Tuple[str, float]:
        # Horizon decay
        horizon_penalty = 0.0 if horizon == ForecastHorizon.SHORT else (0.10 if horizon == ForecastHorizon.MEDIUM else 0.20)
        # Volatility decay
        vol_penalty = trend.volatility * 0.35

        conf = max(0.20, 0.85 - horizon_penalty - vol_penalty)

        # If high volatility, state flips to VOLATILE
        if trend.volatility >= 0.25 and trend.direction == "VOLATILE":
            return ForecastState.VOLATILE.value, round(conf, 4)

        return current_state, round(conf, 4)


class TrendForecastStrategy(ForecastStrategy):
    """
    Extrapolates directional slope and momentum across the chosen horizon.
    """

    def forecast(
        self,
        target: PredictiveTarget,
        current_state: str,
        trend: TrendMetrics,
        horizon: ForecastHorizon,
        sample_count: int,
    ) -> Tuple[str, float]:
        horizon_penalty = 0.0 if horizon == ForecastHorizon.SHORT else (0.08 if horizon == ForecastHorizon.MEDIUM else 0.15)
        conf = max(0.20, (0.50 + 0.40 * trend.strength * trend.persistence) - horizon_penalty)

        if trend.direction == "VOLATILE":
            return ForecastState.VOLATILE.value, round(conf * 0.8, 4)

        if target == PredictiveTarget.ACTIVITY_STATE:
            if trend.direction == "RISING":
                return ForecastState.INCREASING.value, round(conf, 4)
            elif trend.direction == "FALLING":
                return ForecastState.DECREASING.value, round(conf, 4)
            return ForecastState.STABLE.value, round(conf, 4)

        elif target == PredictiveTarget.ANOMALY_STATE:
            if trend.direction == "RISING":
                return ForecastState.ESCALATING.value, round(conf, 4)
            elif trend.direction == "FALLING":
                return ForecastState.RESOLVING.value, round(conf, 4)
            return ForecastState.PERSISTENT.value if trend.strength > 0.40 else ForecastState.NORMAL.value, round(conf, 4)

        elif target == PredictiveTarget.RISK_TREND:
            if trend.direction == "RISING":
                return ForecastState.RISING.value, round(conf, 4)
            elif trend.direction == "FALLING":
                return ForecastState.FALLING.value, round(conf, 4)
            return ForecastState.STABLE.value, round(conf, 4)

        elif target == PredictiveTarget.SPATIAL_STATE:
            if trend.direction == "RISING":
                return ForecastState.EXPANDING.value, round(conf, 4)
            elif trend.direction == "FALLING":
                return ForecastState.CONTRACTING.value, round(conf, 4)
            return ForecastState.STABLE_REGION.value, round(conf, 4)

        elif target == PredictiveTarget.BEHAVIORAL_STATE:
            if trend.is_regime_change:
                return ForecastState.REGIME_CHANGE.value, round(conf * 0.75, 4)
            return ForecastState.CONTINUATION.value, round(conf, 4)

        # Fallback default
        return current_state, round(conf, 4)


class RecurrenceForecastStrategy(ForecastStrategy):
    """
    Evaluates periodic interval regularity and cadence recurrence.
    """

    def forecast(
        self,
        target: PredictiveTarget,
        current_state: str,
        trend: TrendMetrics,
        horizon: ForecastHorizon,
        sample_count: int,
    ) -> Tuple[str, float]:
        # High persistence and low volatility indicate high recurrence probability
        recurrence_likeliness = (trend.persistence * 0.60) + ((1.0 - trend.volatility) * 0.40)
        conf = max(0.20, min(1.0, recurrence_likeliness * 0.90))

        if target == PredictiveTarget.EVENT_TYPE_RECURRENCE:
            if recurrence_likeliness >= 0.60:
                return ForecastState.RECURRING.value, round(conf, 4)
            return ForecastState.NON_RECURRING.value, round(conf, 4)

        if recurrence_likeliness >= 0.70 and trend.direction == "RISING":
            return ForecastState.INCREASING.value, round(conf, 4)

        return current_state, round(conf, 4)
