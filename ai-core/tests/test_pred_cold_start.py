"""
Unit tests for NETRA Phase 6 Cold Start and Data Sufficiency Gating.
Enforces strict epistemic safety rules:
- Fewer than 3 events -> INSUFFICIENT data, UNKNOWN state, confidence capped <= 0.30.
- 3 to 5 events -> LIMITED data, confidence capped <= 0.55.
- More than 5 events -> SUFFICIENT data.
"""

import pytest
from models.predictive_intelligence import (
    DataSufficiency,
    ForecastHorizon,
    ForecastState,
    PredictiveTarget,
    TrendMetrics,
)
from prediction.forecasting import ForecastingEngine


@pytest.fixture
def engine():
    return ForecastingEngine()


def test_cold_start_under_three_events(engine):
    trend = TrendMetrics(slope=0.0, direction="STABLE", strength=0.0, persistence=1.0, acceleration=0.0, volatility=0.0, is_regime_change=False)

    for count in [0, 1, 2]:
        forecast, candidates = engine.generate_forecast(
            target=PredictiveTarget.ACTIVITY_STATE,
            current_state="NOMINAL",
            trend=trend,
            horizon=ForecastHorizon.SHORT,
            sample_count=count,
        )
        assert forecast.data_sufficiency == DataSufficiency.INSUFFICIENT
        assert forecast.forecast_state == ForecastState.UNKNOWN.value
        assert forecast.confidence <= 0.30
        assert forecast.uncertainty >= 0.85
        assert forecast.strategy_used == "COLD_START_FALLBACK"


def test_limited_history_three_to_five_events(engine):
    trend = TrendMetrics(slope=0.10, direction="RISING", strength=0.8, persistence=1.0, acceleration=0.0, volatility=0.03, is_regime_change=False)

    for count in [3, 4, 5]:
        forecast, candidates = engine.generate_forecast(
            target=PredictiveTarget.ACTIVITY_STATE,
            current_state="NOMINAL",
            trend=trend,
            horizon=ForecastHorizon.SHORT,
            sample_count=count,
        )
        assert forecast.data_sufficiency == DataSufficiency.LIMITED
        assert forecast.confidence <= 0.55


def test_sufficient_history_over_five_events(engine):
    trend = TrendMetrics(slope=0.10, direction="RISING", strength=0.8, persistence=1.0, acceleration=0.0, volatility=0.03, is_regime_change=False)

    forecast, _ = engine.generate_forecast(
        target=PredictiveTarget.ACTIVITY_STATE,
        current_state="NOMINAL",
        trend=trend,
        horizon=ForecastHorizon.SHORT,
        sample_count=8,
    )
    assert forecast.data_sufficiency == DataSufficiency.SUFFICIENT
    assert forecast.confidence > 0.55
