"""
Test suite for NETRA Phase 4 Contextual Anomaly Detector.
Verifies environmental dissonance, isolated hyperactivity in calm sectors,
and operations inside active restricted zones.
"""

from datetime import datetime, timezone
import pytest
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity
from anomaly.contextual import ContextualAnomalyDetector


@pytest.fixture
def entity():
    return CanonicalEntity(
        entity_id="ENT-CTXT-TEST",
        entity_type="VEHICLE",
        first_observed=datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc),
        last_observed=datetime(2026, 9, 10, 15, 0, 0, tzinfo=timezone.utc),
        observation_count=20,
    )


def test_contextual_nominal(entity):
    events = [
        CanonicalEvent(
            event_id="EVT-C-1",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
        )
    ]
    res = ContextualAnomalyDetector.detect(entity, events, context=None)
    assert res.score == 0.0


def test_contextual_isolated_activity_in_calm_sector(entity):
    events = [
        CanonicalEvent(
            event_id="EVT-C-HIGHACT",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
            attributes={"activity_level": 0.85},
        )
    ]
    context = {"sector_average_activity": 0.08}
    res = ContextualAnomalyDetector.detect(entity, events, context=context)
    assert res.score >= 0.75
    assert "ISOLATED_ACTIVITY_IN_CALM_SECTOR" in res.indicators


def test_contextual_restricted_zone_breach(entity):
    events = [
        CanonicalEvent(
            event_id="EVT-C-RESTRICTED",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
        )
    ]
    context = {"restricted_zone_active": True}
    res = ContextualAnomalyDetector.detect(entity, events, context=context)
    assert res.score >= 0.80
    assert "ACTIVE_RESTRICTED_ZONE_PRESENCE" in res.indicators
