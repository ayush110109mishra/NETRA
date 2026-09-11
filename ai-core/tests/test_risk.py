"""
Unit tests for NETRA Risk Engine.
Verifies factor weights, mathematical bounds, explainability breakdown, and determinism.
"""

import pytest
from config import default_config, RiskWeights
from simulation.synthetic_data import SCENARIO_NORMAL, SCENARIO_ANOMALOUS, SCENARIO_HIGH_RISK_CORRELATED
from risk.engine import calculate_explainable_risk
from models.common import RiskLevel


def test_risk_weights_sum_to_one():
    """Verify configured risk weights sum to exactly 1.0."""
    weights = default_config.risk_weights
    total = (
        weights.activity_deviation
        + weights.speed_anomaly
        + weights.event_severity_baseline
        + weights.relationship_density
    )
    assert abs(total - 1.0) < 1e-6


def test_risk_weights_invalid_sum():
    """Verify invalid weights raise a ValueError."""
    with pytest.raises(ValueError):
        invalid_weights = RiskWeights(activity_deviation=0.5, speed_anomaly=0.5, event_severity_baseline=0.5)
        invalid_weights.validate()


def test_risk_score_bounds():
    """Verify calculated risk score is always within [0.0, 1.0]."""
    for scenario in [SCENARIO_NORMAL, SCENARIO_ANOMALOUS, SCENARIO_HIGH_RISK_CORRELATED]:
        res = calculate_explainable_risk(scenario)
        assert 0.0 <= res.breakdown.score <= 1.0
        assert res.breakdown.level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]


def test_risk_explainability_factors():
    """Verify all 4 explainable factors are returned with proper weights and descriptions."""
    res = calculate_explainable_risk(SCENARIO_ANOMALOUS)
    factors = res.breakdown.factors
    assert len(factors) == 4

    factor_names = [f.factor for f in factors]
    assert "activity_deviation" in factor_names
    assert "speed_anomaly" in factor_names
    assert "event_severity_baseline" in factor_names
    assert "relationship_density" in factor_names

    for f in factors:
        assert f.weight > 0.0
        assert 0.0 <= f.contribution <= f.weight + 0.0001
        assert len(f.description) > 0


def test_risk_determinism():
    """Verify calling risk engine multiple times with identical input yields identical output."""
    res1 = calculate_explainable_risk(SCENARIO_ANOMALOUS)
    res2 = calculate_explainable_risk(SCENARIO_ANOMALOUS)
    assert res1.breakdown.score == res2.breakdown.score
    assert res1.breakdown.level == res2.breakdown.level
    assert res1.indicators == res2.indicators
