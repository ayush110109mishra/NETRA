"""
Test suite for NETRA Phase 4 Anomaly Trend Analyzer.
Verifies rate of change, delta computations, and directional trajectories.
"""

from models.anomaly_intelligence import TrendDirection
from anomaly.trend import AnomalyTrendAnalyzer


def test_trend_unknown_previous():
    trend = AnomalyTrendAnalyzer.analyze(current_score=0.45, previous_score=None)
    assert trend.direction == TrendDirection.UNKNOWN
    assert trend.delta == 0.0
    assert trend.previous is None


def test_trend_increase():
    trend = AnomalyTrendAnalyzer.analyze(
        current_score=0.75,
        previous_score=0.40,
        time_delta_hours=2.0,
    )
    assert trend.direction == TrendDirection.INCREASE
    assert abs(trend.delta - 0.35) < 1e-4
    assert abs(trend.rate_of_change - 0.175) < 1e-4


def test_trend_decrease():
    trend = AnomalyTrendAnalyzer.analyze(
        current_score=0.30,
        previous_score=0.60,
        time_delta_hours=1.0,
    )
    assert trend.direction == TrendDirection.DECREASE
    assert trend.delta < -0.05


def test_trend_stable():
    trend = AnomalyTrendAnalyzer.analyze(
        current_score=0.52,
        previous_score=0.50,
        time_delta_hours=1.0,
    )
    assert trend.direction == TrendDirection.STABLE
    assert abs(trend.delta - 0.02) < 1e-4
