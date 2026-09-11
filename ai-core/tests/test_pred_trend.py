"""
Unit tests for NETRA Phase 6 Trend & Regime Shift Engine.
Validates least-squares linear slope, directionality, trend strength,
persistence ratio, volatility, and regime shift detection (delta slope >= 0.20).
"""

from datetime import datetime, timezone, timedelta
import pytest

from models.predictive_intelligence import TemporalStatePoint, TemporalStateSequence
from prediction.trend import TrendEngine


@pytest.fixture
def engine():
    return TrendEngine()


def test_trend_minimal_points(engine):
    seq = TemporalStateSequence(
        entity_id="E1",
        points=[
            TemporalStatePoint(timestamp=datetime.now(timezone.utc), value=0.5, state="NOMINAL")
        ],
        sample_count=1,
        sampling_regularity=1.0,
    )
    metrics = engine.analyze_trend(seq)
    assert metrics.direction == "STABLE"
    assert metrics.slope == 0.0
    assert metrics.strength == 0.0
    assert metrics.is_regime_change is False


def test_trend_monotonic_rising(engine):
    t0 = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)
    points = [
        TemporalStatePoint(timestamp=t0 + timedelta(minutes=i * 10), value=0.20 + i * 0.08, state="ELEVATED")
        for i in range(8)
    ]
    seq = TemporalStateSequence(entity_id="E-RISE", points=points, sample_count=8, sampling_regularity=1.0)
    metrics = engine.analyze_trend(seq)

    assert metrics.direction == "RISING"
    assert metrics.slope > 0.05
    assert metrics.strength > 0.85
    assert metrics.persistence == 1.0


def test_trend_monotonic_falling(engine):
    t0 = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)
    points = [
        TemporalStatePoint(timestamp=t0 + timedelta(minutes=i * 10), value=0.90 - i * 0.09, state="NOMINAL")
        for i in range(8)
    ]
    seq = TemporalStateSequence(entity_id="E-FALL", points=points, sample_count=8, sampling_regularity=1.0)
    metrics = engine.analyze_trend(seq)

    assert metrics.direction == "FALLING"
    assert metrics.slope < -0.05
    assert metrics.strength > 0.85
    assert metrics.persistence == 1.0


def test_trend_regime_shift_detection(engine):
    t0 = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)
    # First 5 points flat at 0.10 (slope 0.0), next 5 points surging with delta slope >= 0.20
    vals = [0.10, 0.10, 0.10, 0.10, 0.10, 0.15, 0.38, 0.62, 0.85, 1.00]
    points = [
        TemporalStatePoint(timestamp=t0 + timedelta(minutes=i * 10), value=vals[i], state="NOMINAL")
        for i in range(10)
    ]

    seq = TemporalStateSequence(entity_id="E-REGIME", points=points, sample_count=10, sampling_regularity=1.0)
    metrics = engine.analyze_trend(seq)

    assert metrics.is_regime_change is True
