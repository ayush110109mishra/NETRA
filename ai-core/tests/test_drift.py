"""
Unit tests for Baseline Drift Analyzer.
Tests trend detection (INCREASE, DECREASE, STABLE) and cold-start handling.
"""

from datetime import datetime, timezone
import pytest

from models.common import Coordinates
from models.event_intelligence import CanonicalEvent
from events.drift import BaselineDriftAnalyzer

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)
LOC = Coordinates(latitude=26.84, longitude=80.94)


def test_baseline_drift_increase():
    """Verify significant upward drift in activity is flagged as INCREASE."""
    analyzer = BaselineDriftAnalyzer()
    events = [
        CanonicalEvent(event_id="D1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, attributes={"activity_level": 0.75}),
        CanonicalEvent(event_id="D2", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, attributes={"activity_level": 0.80}),
    ]
    res = analyzer.analyze_drift(events, historical_baseline=0.30, recent_baseline=0.75)
    assert res.direction == "INCREASE"
    assert res.score > 0.50
    assert "upward operational drift" in res.description


def test_baseline_drift_decrease():
    """Verify significant downward drift in activity is flagged as DECREASE."""
    analyzer = BaselineDriftAnalyzer()
    events = [
        CanonicalEvent(event_id="D1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, attributes={"activity_level": 0.15}),
    ]
    res = analyzer.analyze_drift(events, historical_baseline=0.60, recent_baseline=0.15)
    assert res.direction == "DECREASE"
    assert "downward operational drift" in res.description


def test_baseline_drift_stable():
    """Verify nominal activity matching baseline is flagged as STABLE."""
    analyzer = BaselineDriftAnalyzer()
    events = [
        CanonicalEvent(event_id="D1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, attributes={"activity_level": 0.32}),
    ]
    res = analyzer.analyze_drift(events, historical_baseline=0.30, recent_baseline=0.32)
    assert res.direction == "STABLE"


def test_baseline_drift_cold_start():
    """Verify missing historical baseline yields STABLE with low confidence."""
    analyzer = BaselineDriftAnalyzer()
    events = [
        CanonicalEvent(event_id="D1", event_type="MOVEMENT", timestamp=BASE_TIME, location=LOC, attributes={"activity_level": 0.50}),
    ]
    res = analyzer.analyze_drift(events, historical_baseline=None, recent_baseline=0.50)
    assert res.direction == "STABLE"
    assert res.confidence == 0.30
    assert "cold start" in res.description
