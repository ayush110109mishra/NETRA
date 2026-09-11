"""
Test suite for NETRA Phase 4 Risk Trend & Propagation Engines.
Verifies score delta, volatility computation, and graph-based risk propagation.
"""

from datetime import datetime, timezone
from models.entity_intelligence import CanonicalEntity
from models.risk_intelligence import RiskTrendDirection
from risk.trend import RiskTrendAnalyzer
from risk.propagation import RiskPropagator


def test_risk_trend_analysis():
    # Stable trend
    t_stable = RiskTrendAnalyzer.analyze(current_score=0.42, previous_score=0.40, history=[0.40, 0.41, 0.42])
    assert t_stable.direction == RiskTrendDirection.STABLE

    # Rising trend
    t_rising = RiskTrendAnalyzer.analyze(current_score=0.65, previous_score=0.40, history=[0.35, 0.40, 0.65])
    assert t_rising.direction == RiskTrendDirection.RISING

    # Volatile trend
    t_volatile = RiskTrendAnalyzer.analyze(current_score=0.85, previous_score=0.15, history=[0.85, 0.15, 0.85, 0.15])
    assert t_volatile.direction == RiskTrendDirection.VOLATILE
    assert t_volatile.volatility > 0.25


def test_risk_propagation_along_network():
    propagator = RiskPropagator(damping_factor=0.30)
    target = CanonicalEntity(
        entity_id="ENT-TARGET",
        entity_type="VEHICLE",
        first_observed=datetime.now(timezone.utc),
        last_observed=datetime.now(timezone.utc),
        observation_count=5,
    )
    peer = CanonicalEntity(
        entity_id="ENT-HIGH-RISK-PEER",
        entity_type="VEHICLE",
        first_observed=datetime.now(timezone.utc),
        last_observed=datetime.now(timezone.utc),
        observation_count=10,
    )

    base_risk = 0.20
    related_risks = {peer.entity_id: 0.90}
    rel_weights = {peer.entity_id: 0.80}

    res = propagator.propagate_risk(
        target_entity=target,
        base_risk_score=base_risk,
        related_entities=[peer],
        related_risks=related_risks,
        relationship_weights=rel_weights,
    )

    # Influence = 0.90 * 0.80 * 0.30 = 0.2160
    assert res["base_risk"] == 0.20
    assert res["propagated_risk"] > 0.20
    assert abs(res["delta"] - 0.216) < 1e-3
    assert len(res["propagated_factors"]) == 1
