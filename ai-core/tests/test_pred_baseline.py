"""
Unit tests for NETRA Phase 6 Forecasting Strategies.
Tests Persistence, Trend, and Recurrence baseline strategies, horizon confidence decay,
and state projections across analytical targets.
"""

import pytest
from models.predictive_intelligence import (
    ForecastHorizon,
    ForecastState,
    PredictiveTarget,
    TrendMetrics,
)
from prediction.baseline_forecast import (
    PersistenceForecastStrategy,
    TrendForecastStrategy,
    RecurrenceForecastStrategy,
)


def test_persistence_forecast_strategy():
    strat = PersistenceForecastStrategy()
    trend = TrendMetrics(slope=0.01, direction="STABLE", strength=0.1, persistence=0.9, acceleration=0.0, volatility=0.05, is_regime_change=False)

    # SHORT horizon
    state_short, conf_short = strat.forecast(PredictiveTarget.ACTIVITY_STATE, "NOMINAL", trend, ForecastHorizon.SHORT, 10)
    assert state_short == "NOMINAL"
    assert conf_short > 0.60

    # LONG horizon has confidence decay
    state_long, conf_long = strat.forecast(PredictiveTarget.ACTIVITY_STATE, "NOMINAL", trend, ForecastHorizon.LONG, 10)
    assert state_long == "NOMINAL"
    assert conf_long < conf_short


def test_trend_forecast_strategy_rising():
    strat = TrendForecastStrategy()
    trend = TrendMetrics(slope=0.12, direction="RISING", strength=0.85, persistence=1.0, acceleration=0.0, volatility=0.05, is_regime_change=False)

    state, conf = strat.forecast(PredictiveTarget.ACTIVITY_STATE, "NOMINAL", trend, ForecastHorizon.SHORT, 8)
    assert state == ForecastState.INCREASING.value
    assert conf > 0.70

    # For RISK_TREND
    state_r, conf_r = strat.forecast(PredictiveTarget.RISK_TREND, "MEDIUM", trend, ForecastHorizon.SHORT, 8)
    assert state_r == ForecastState.RISING.value


def test_recurrence_forecast_strategy():
    strat = RecurrenceForecastStrategy()
    trend = TrendMetrics(slope=0.0, direction="STABLE", strength=0.1, persistence=0.9, acceleration=0.0, volatility=0.04, is_regime_change=False)

    state, conf = strat.forecast(PredictiveTarget.EVENT_TYPE_RECURRENCE, "PATROL_SWEEP", trend, ForecastHorizon.SHORT, 12)
    assert state == ForecastState.RECURRING.value
    assert conf > 0.65

