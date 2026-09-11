"""
Tests for Entity Timeline Builder in NETRA.
"""

from datetime import datetime, timezone, timedelta
from models.common import Coordinates, SeverityLevel
from models.event_intelligence import CanonicalEvent
from entities.timeline import EntityTimelineBuilder

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)


def test_timeline_chronological_ordering_and_filters():
    events = [
        CanonicalEvent(
            event_id="EVT-01",
            event_type="movement",
            timestamp=BASE_TIME - timedelta(hours=3),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["ENT-1"],
            attributes={"severity": "LOW"},
        ),
        CanonicalEvent(
            event_id="EVT-02",
            event_type="patrol_deviation",
            timestamp=BASE_TIME - timedelta(hours=2),
            location=Coordinates(latitude=26.86, longitude=80.96),
            entity_ids=["ENT-1"],
            attributes={"severity": "HIGH"},
        ),
        CanonicalEvent(
            event_id="EVT-03",
            event_type="movement",
            timestamp=BASE_TIME - timedelta(hours=1),
            location=Coordinates(latitude=26.87, longitude=80.97),
            entity_ids=["ENT-1"],
            attributes={"severity": "LOW"},
        ),
    ]

    # Default reverse=True (most recent first)
    timeline = EntityTimelineBuilder.build_timeline(events)
    assert len(timeline) == 3
    assert timeline[0].event_id == "EVT-03"
    assert timeline[2].event_id == "EVT-01"

    # Filter by event_type
    filtered_type = EntityTimelineBuilder.build_timeline(events, event_type="patrol_deviation")
    assert len(filtered_type) == 1
    assert filtered_type[0].event_id == "EVT-02"
    assert filtered_type[0].severity == SeverityLevel.HIGH

    # Filter by limit
    limited = EntityTimelineBuilder.build_timeline(events, limit=2)
    assert len(limited) == 2
    assert limited[0].event_id == "EVT-03"
    assert limited[1].event_id == "EVT-02"
