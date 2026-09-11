"""
Tests for Entity Risk Engine in NETRA.
"""

from datetime import datetime, timezone, timedelta
from models.common import RiskLevel, Coordinates
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import (
    CanonicalEntity,
    BehavioralChangeReport,
    EntityAnomalyAssessment,
    EntityClusterMembership,
)
from entities.risk import EntityRiskEngine
from config import NetraConfig, EntityRiskWeights

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)


def test_entity_risk_weights_validation():
    valid_weights = EntityRiskWeights(
        event_risk=0.30,
        behavioral_deviation=0.25,
        anomaly_score=0.25,
        cluster_context=0.20,
    )
    valid_weights.validate()


def test_entity_risk_score_and_factors():
    cfg = NetraConfig()
    engine = EntityRiskEngine(cfg)

    entity = CanonicalEntity(
        entity_id="ENTITY-RISK-01",
        entity_type="VEHICLE",
        first_observed=BASE_TIME - timedelta(hours=24),
        last_observed=BASE_TIME,
    )
    events = [
        CanonicalEvent(
            event_id="EVT-1",
            event_type="movement",
            timestamp=BASE_TIME,
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["ENTITY-RISK-01"],
            attributes={"activity_level": 0.40, "priority_hint": "MEDIUM"},
        )
    ]
    changes = BehavioralChangeReport(detected=False, score=0.0, changes=[])
    anomaly = EntityAnomalyAssessment(score=0.10, level="LOW", indicators=[])
    clusters = [
        EntityClusterMembership(cluster_id="CLUS-1", event_count=3, cohesion=0.85, confidence=0.90)
    ]

    profile = engine.compute_risk(entity, events, changes, anomaly, clusters)

    assert 0.0 <= profile.score <= 1.0
    assert profile.level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
    assert len(profile.factors) == 4

    # Factors match weights and explainability
    total_contrib = sum(f.contribution for f in profile.factors)
    assert abs(total_contrib - profile.score) < 0.05
