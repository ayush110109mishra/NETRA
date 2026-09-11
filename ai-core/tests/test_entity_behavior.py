"""
Tests for Spatial and Temporal Behavior Analyzers.
"""

from datetime import datetime, timezone, timedelta
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent
from entities.spatial_behavior import SpatialBehaviorAnalyzer
from entities.temporal_behavior import TemporalBehaviorAnalyzer

BASE_TIME = datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc)


def test_spatial_behavior_centroid_and_radius():
    events = [
        CanonicalEvent(
            event_id="EVT-1",
            event_type="movement",
            timestamp=BASE_TIME,
            location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_ALPHA"),
            entity_ids=["E1"],
        ),
        CanonicalEvent(
            event_id="EVT-2",
            event_type="movement",
            timestamp=BASE_TIME + timedelta(hours=1),
            location=Coordinates(latitude=26.8600, longitude=80.9500, sector_id="SECTOR_ALPHA"),
            entity_ids=["E1"],
        ),
        CanonicalEvent(
            event_id="EVT-3",
            event_type="movement",
            timestamp=BASE_TIME + timedelta(hours=2),
            location=Coordinates(latitude=26.8700, longitude=80.9500, sector_id="SECTOR_ALPHA"),
            entity_ids=["E1"],
        ),
    ]

    spatial = SpatialBehaviorAnalyzer.analyze(events)

    # Centroid should be the mean: latitude 26.8600, longitude 80.9500
    assert abs(spatial.centroid.latitude - 26.8600) < 1e-3
    assert abs(spatial.centroid.longitude - 80.9500) < 1e-3
    assert spatial.bounding_radius_km > 0.0
    assert 0.0 <= spatial.spatial_concentration <= 1.0
    assert "SECTOR_ALPHA" in spatial.frequent_sectors


def test_temporal_behavior_distribution_and_peak():
    # 3 events at 10:00, 10:30, 11:30 UTC
    events = [
        CanonicalEvent(
            event_id="EVT-1",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 10, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["E1"],
        ),
        CanonicalEvent(
            event_id="EVT-2",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 10, 30, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["E1"],
        ),
        CanonicalEvent(
            event_id="EVT-3",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 11, 30, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.85, longitude=80.95),
            entity_ids=["E1"],
        ),
    ]

    temporal = TemporalBehaviorAnalyzer.analyze(events)

    # Hour 10 has 2 events (66.7%), Hour 11 has 1 event (33.3%)
    assert temporal.peak_activity_hour == 10
    assert temporal.hourly_distribution[10] > temporal.hourly_distribution[11]
    # Gaps: 30 min, 60 min -> Average: 45 min
    assert temporal.average_inter_event_minutes == 45.0
