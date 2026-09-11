"""
Integration tests for NETRA Intelligence Engine.
Verifies complete pipeline execution across all 6 synthetic operational scenarios.
"""

import pytest
from models.common import ClassificationType, SeverityLevel, RiskLevel
from intelligence.engine import analyze_intelligence
from simulation.synthetic_data import (
    SCENARIO_NORMAL,
    SCENARIO_UNUSUAL,
    SCENARIO_ANOMALOUS,
    SCENARIO_HIGH_RISK_CORRELATED,
    SCENARIO_INSUFFICIENT_HISTORY,
    SCENARIO_CONFLICTING_SIGNALS,
)


def test_engine_scenario_normal():
    """Verify normal scenario executes smoothly with expected normal outputs."""
    res = analyze_intelligence(SCENARIO_NORMAL)
    assert res.classification == ClassificationType.NORMAL
    assert res.risk.level == RiskLevel.LOW
    assert res.risk.score < 0.25
    assert res.confidence >= 0.80
    assert "[OBSERVED]" in res.assessment
    assert "[INFERRED]" in res.assessment
    assert "[UNCERTAIN]" in res.assessment
    assert res.metadata["data_classification"] == "SYNTHETIC"


def test_engine_scenario_unusual():
    """Verify unusual scenario produces UNUSUAL classification."""
    res = analyze_intelligence(SCENARIO_UNUSUAL)
    assert res.classification == ClassificationType.UNUSUAL
    assert res.risk.level in [RiskLevel.LOW, RiskLevel.MEDIUM]


def test_engine_scenario_anomalous():
    """Verify anomalous scenario produces ANOMALOUS classification."""
    res = analyze_intelligence(SCENARIO_ANOMALOUS)
    assert res.classification == ClassificationType.ANOMALOUS
    assert res.risk.score >= 0.50
    assert res.severity in [SeverityLevel.MEDIUM, SeverityLevel.HIGH]


def test_engine_scenario_high_risk():
    """Verify multi-threat scenario produces HIGH_RISK classification."""
    res = analyze_intelligence(SCENARIO_HIGH_RISK_CORRELATED)
    assert res.classification == ClassificationType.HIGH_RISK
    assert res.risk.level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    assert len(res.related_entities) > 0
    assert len(res.related_events) > 0


def test_engine_scenario_insufficient_history():
    """Verify zero-baseline cold start yields UNKNOWN classification and reduced confidence."""
    res = analyze_intelligence(SCENARIO_INSUFFICIENT_HISTORY)
    assert res.classification == ClassificationType.UNKNOWN
    assert res.confidence < 0.60


def test_engine_scenario_conflicting_signals():
    """Verify conflicting telemetry is processed without crash and flags uncertainty."""
    res = analyze_intelligence(SCENARIO_CONFLICTING_SIGNALS)
    assert res.confidence_breakdown.signal_consistency < 0.70
    assert "Sensor telemetry exhibits potential signal contradiction." in res.assessment
