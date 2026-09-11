"""
Test suite for NETRA Phase 4 Explainable Risk Aggregator (phase4-v1).
Verifies 7-factor risk model:
Risk = 0.20*Event + 0.15*Dev + 0.25*Anom + 0.15*Cluster + 0.10*Persist + 0.10*Trend + 0.05*Evidence,
weights sum to 1.0, factor mathematical consistency, and hysteresis state machine.
"""

from datetime import datetime, timezone
import pytest
from config import Phase4RiskWeights, HysteresisConfig
from models.common import RiskLevel, Coordinates
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from models.anomaly_intelligence import (
    AnomalySummary,
    AnomalyLevel,
    AnomalyPersistenceState,
    AnomalyConfirmationLevel,
    AnomalyLifecycle,
    AnomalyTrend,
    AnomalyPersistence,
    TrendDirection,
)
from models.risk_intelligence import RiskState
from risk.aggregation import Phase4RiskAggregator


def test_phase4_risk_weights_sum_to_one():
    w = Phase4RiskWeights()
    w.validate()
    total = (
        w.event_risk
        + w.behavioral_deviation
        + w.anomaly_score
        + w.cluster_context
        + w.anomaly_persistence
        + w.anomaly_trend
        + w.evidence_quality
    )
    assert abs(total - 1.0) < 1e-6


def test_phase4_risk_aggregation_formula():
    aggregator = Phase4RiskAggregator()
    entity = CanonicalEntity(
        entity_id="ENT-R4-TEST",
        entity_type="VEHICLE",
        first_observed=datetime.now(timezone.utc),
        last_observed=datetime.now(timezone.utc),
        observation_count=10,
    )
    events = [
        CanonicalEvent(
            event_id="EVT-1",
            event_type="movement",
            timestamp=datetime.now(timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
            attributes={"activity_level": 0.50},
        )
    ]
    summary = AnomalySummary(
        score=0.80,
        level=AnomalyLevel.HIGH,
        state=AnomalyPersistenceState.PERSISTENT,
        confirmation=AnomalyConfirmationLevel.CORROBORATED,
        lifecycle=AnomalyLifecycle.ACTIVE,
    )
    trend = AnomalyTrend(
        current=0.80,
        previous=0.50,
        delta=0.30,
        rate_of_change=0.30,
        direction=TrendDirection.INCREASE,
    )
    persistence = AnomalyPersistence(
        state=AnomalyPersistenceState.PERSISTENT,
        elevated_windows=3,
        consecutive_windows=3,
        peak_score=0.80,
        average_score=0.70,
    )

    profile = aggregator.compute_risk(
        entity=entity,
        events=events,
        anomaly_summary=summary,
        anomaly_trend=trend,
        anomaly_persistence=persistence,
    )

    assert profile.model_version == "phase4-v1"
    assert len(profile.factors) == 7

    # Validate each factor contribution = score * weight
    total_expected = 0.0
    for factor in profile.factors:
        expected_c = round(factor.score * factor.weight, 4)
        assert abs(factor.contribution - expected_c) < 1e-4
        total_expected += factor.contribution

    assert abs(profile.score - round(total_expected, 4)) < 1e-4
    assert profile.level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]


def test_hysteresis_state_transitions():
    aggregator = Phase4RiskAggregator(hysteresis=HysteresisConfig(buffer=0.03))

    # Test going up: threshold 0.30 + 0.03 = 0.33
    s1 = aggregator._determine_hysteresis_state(current_risk=0.32, previous_state=RiskState.NORMAL)
    assert s1 == RiskState.NORMAL  # 0.32 < 0.33 buffer
    s2 = aggregator._determine_hysteresis_state(current_risk=0.34, previous_state=RiskState.NORMAL)
    assert s2 == RiskState.ELEVATED  # 0.34 >= 0.33

    # Test dropping down: threshold 0.30 - 0.03 = 0.27
    s3 = aggregator._determine_hysteresis_state(current_risk=0.28, previous_state=RiskState.ELEVATED)
    assert s3 == RiskState.ELEVATED  # 0.28 >= 0.27
    s4 = aggregator._determine_hysteresis_state(current_risk=0.26, previous_state=RiskState.ELEVATED)
    assert s4 == RiskState.NORMAL  # 0.26 < 0.27
