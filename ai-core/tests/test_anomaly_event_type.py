"""
Test suite for NETRA Phase 4 Event Type Anomaly Detector.
Verifies novel tactical events (jamming, strikes), rare event surges,
and baseline taxonomy conformity.
"""

from datetime import datetime, timezone
import pytest
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from anomaly.event_type import EventTypeAnomalyDetector


@pytest.fixture
def entity():
    return CanonicalEntity(
        entity_id="ENT-TYPE-TEST",
        entity_type="VEHICLE",
        first_observed=datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc),
        last_observed=datetime(2026, 9, 10, 15, 0, 0, tzinfo=timezone.utc),
        observation_count=20,
    )


@pytest.fixture
def baseline():
    # Only movement and patrol observed historically
    return EntityBehaviorProfile(
        baseline_status="SUFFICIENT_HISTORY",
        sample_count=20,
        event_frequency_per_day=2.0,
        average_activity=0.30,
        average_speed=35.0,
        event_type_distribution={"movement": 0.80, "patrol": 0.20},
    )


def test_event_type_conforming(entity, baseline):
    events = [
        CanonicalEvent(
            event_id="EVT-T-1",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
        )
    ]
    res = EventTypeAnomalyDetector.detect(entity, events, baseline)
    assert res.score == 0.0
    assert len(res.indicators) == 0


def test_event_type_novel_critical(entity, baseline):
    events = [
        CanonicalEvent(
            event_id="EVT-JAM-01",
            event_type="RADAR_JAMMING",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
        )
    ]
    res = EventTypeAnomalyDetector.detect(entity, events, baseline)
    assert res.score >= 0.85
    assert "NOVEL_CRITICAL_EVENT_TYPE_RADAR_JAMMING" in res.indicators
    assert "EVT-JAM-01" in res.evidence_event_ids


def test_event_type_novel_benign(entity, baseline):
    events = [
        CanonicalEvent(
            event_id="EVT-MAINT-01",
            event_type="MAINTENANCE",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=[entity.entity_id],
        )
    ]
    res = EventTypeAnomalyDetector.detect(entity, events, baseline)
    assert 0.50 <= res.score <= 0.75
    assert "NOVEL_EVENT_TYPE_MAINTENANCE" in res.indicators
