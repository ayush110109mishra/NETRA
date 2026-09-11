"""
Test suite for NETRA Phase 4 Relational Anomaly Detector.
Verifies network topology changes, rendezvous surges, cluster affiliation,
and association with high-risk peers.
"""

from datetime import datetime, timezone
import pytest
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from anomaly.relational import RelationalAnomalyDetector


@pytest.fixture
def base_entity():
    return CanonicalEntity(
        entity_id="ENT-RELA-PRIMARY",
        entity_type="VEHICLE",
        first_observed=datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc),
        last_observed=datetime(2026, 9, 10, 15, 0, 0, tzinfo=timezone.utc),
        observation_count=20,
        attributes={"associated_entity_ids": ["ENT-FRIENDLY-01"]},
    )


def test_relational_nominal(base_entity):
    events = [
        CanonicalEvent(
            event_id="EVT-R-1",
            event_type="patrol",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[base_entity.entity_id],
            attributes={"target_entity_id": "ENT-FRIENDLY-01"},
        )
    ]
    res = RelationalAnomalyDetector.detect(base_entity, events)
    assert res.score == 0.0


def test_relational_rendezvous_surge(base_entity):
    # Associating with 4 new unknown peers
    events = [
        CanonicalEvent(
            event_id="EVT-R-RENDEZVOUS",
            event_type="patrol",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[base_entity.entity_id],
            attributes={
                "co_observed_entities": [
                    "ENT-UNKNOWN-1",
                    "ENT-UNKNOWN-2",
                    "ENT-UNKNOWN-3",
                    "ENT-UNKNOWN-4",
                ]
            },
        )
    ]
    res = RelationalAnomalyDetector.detect(base_entity, events)
    assert res.score >= 0.75
    assert "ASSOCIATION_SURGE_RENDEZVOUS" in res.indicators
    assert "EVT-R-RENDEZVOUS" in res.evidence_event_ids


def test_relational_high_risk_peer_correlation(base_entity):
    events = [
        CanonicalEvent(
            event_id="EVT-R-THREAT",
            event_type="patrol",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[base_entity.entity_id],
            attributes={"target_entity_id": "ENT-HOSTILE-HQ"},
        )
    ]
    context = {"high_risk_entities": ["ENT-HOSTILE-HQ"]}
    res = RelationalAnomalyDetector.detect(base_entity, events, context=context)
    assert res.score >= 0.80
    assert "HIGH_RISK_PEER_CORRELATION" in res.indicators
