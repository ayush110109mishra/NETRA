"""
Test suite for NETRA Phase 4 Anomaly Persistence Analyzer.
Verifies persistence states: TRANSIENT, PERSISTENT, RECURRING, ESCALATING, DECLINING.
"""

import pytest
from config import PersistenceConfig
from models.anomaly_intelligence import (
    AnomalyPersistenceState,
    AnomalyTrend,
    TrendDirection,
)
from anomaly.persistence import AnomalyPersistenceAnalyzer


@pytest.fixture
def analyzer():
    return AnomalyPersistenceAnalyzer(
        PersistenceConfig(
            transient_max_windows=1,
            persistent_min_windows=2,
            escalating_rate_threshold=0.15,
            declining_rate_threshold=-0.15,
        )
    )


def test_persistence_transient(analyzer):
    # Single elevated score
    history = [0.10, 0.10, 0.45]
    trend = AnomalyTrend(current=0.45, previous=0.10, delta=0.35, rate_of_change=0.35, direction=TrendDirection.INCREASE)
    res = analyzer.analyze(history, trend)
    # Only 1 consecutive elevated window
    assert res.state == AnomalyPersistenceState.TRANSIENT
    assert res.consecutive_windows == 1
    assert res.elevated_windows == 1


def test_persistence_persistent(analyzer):
    # Multiple consecutive elevated windows (score >= 0.25)
    history = [0.10, 0.50, 0.55, 0.52]
    trend = AnomalyTrend(current=0.52, previous=0.55, delta=-0.03, rate_of_change=-0.03, direction=TrendDirection.STABLE)
    res = analyzer.analyze(history, trend)
    assert res.state == AnomalyPersistenceState.PERSISTENT
    assert res.consecutive_windows == 3
    assert res.peak_score == 0.55


def test_persistence_recurring(analyzer):
    # Elevated in the past, dropped to normal, elevated again (consecutive = 1, total elevated >= 2)
    history = [0.60, 0.10, 0.10, 0.55]
    trend = AnomalyTrend(current=0.55, previous=0.10, delta=0.45, rate_of_change=0.10, direction=TrendDirection.INCREASE)
    res = analyzer.analyze(history, trend)
    assert res.state == AnomalyPersistenceState.RECURRING
    assert res.consecutive_windows == 1
    assert res.elevated_windows == 2


def test_persistence_escalating(analyzer):
    # Consecutive elevated windows accelerating rapidly (rate_of_change >= 0.15, current >= 0.70)
    history = [0.35, 0.50, 0.80]
    trend = AnomalyTrend(current=0.80, previous=0.50, delta=0.30, rate_of_change=0.30, direction=TrendDirection.INCREASE)
    res = analyzer.analyze(history, trend)
    assert res.state == AnomalyPersistenceState.ESCALATING
    assert res.consecutive_windows == 3


def test_persistence_declining(analyzer):
    # Dropping rapidly or dropping below nominal after historical peak
    history = [0.80, 0.60, 0.35]
    trend = AnomalyTrend(current=0.35, previous=0.60, delta=-0.25, rate_of_change=-0.25, direction=TrendDirection.DECREASE)
    res = analyzer.analyze(history, trend)
    assert res.state == AnomalyPersistenceState.DECLINING
