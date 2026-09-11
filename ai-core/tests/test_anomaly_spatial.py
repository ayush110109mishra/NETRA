"""
Test suite for NETRA Phase 4 Spatial Anomaly Detector.
Verifies boundary excursions, centroid distance deviations, sector relocations,
and spatial teleportation jumps.
"""

from datetime import datetime, timezone, timedelta
import pytest
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import (
    CanonicalEntity,
    EntityBehaviorProfile,
    EntitySpatialBehavior,
)
from anomaly.spatial import SpatialAnomalyDetector


@pytest.fixture
def base_entity():
    return CanonicalEntity(
        entity_id="ENT-SPAT-TEST",
        entity_type="VEHICLE",
        first_observed=datetime(2026, 9, 1, 10, 0, 0, tzinfo=timezone.utc),
        last_observed=datetime(2026, 9, 10, 15, 0, 0, tzinfo=timezone.utc),
        observation_count=25,
        attributes={"registered_sector": "SECTOR_ALPHA"},
    )


@pytest.fixture
def localized_baseline():
    # Centroid at 26.85, 80.95 with 5 km historical dispersion
    return EntityBehaviorProfile(
        baseline_status="SUFFICIENT_HISTORY",
        sample_count=25,
        event_frequency_per_day=3.0,
        average_activity=0.30,
        average_speed=35.0,
        spatial=EntitySpatialBehavior(
            centroid=Coordinates(latitude=26.8500, longitude=80.9500),
            bounding_radius_km=5.0,
            spatial_concentration=0.8,
            frequent_sectors=["SECTOR_ALPHA"],
        ),
    )


def test_spatial_nominal_boundary(base_entity, localized_baseline):
    # Within 2 km of centroid
    events = [
        CanonicalEvent(
            event_id="EVT-S-NORM",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.8520, longitude=80.9520, sector_id="SECTOR_ALPHA"),
            entity_ids=[base_entity.entity_id],
        )
    ]
    res = SpatialAnomalyDetector.detect(base_entity, events, localized_baseline)
    assert res.score == 0.0
    assert len(res.indicators) == 0


def test_spatial_severe_breach(base_entity, localized_baseline):
    # Operating ~60 km away (27.40, 81.40) vs 5 km dispersion
    events = [
        CanonicalEvent(
            event_id="EVT-S-BREACH-01",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=27.4000, longitude=81.4000, sector_id="SECTOR_ALPHA"),
            entity_ids=[base_entity.entity_id],
        )
    ]
    res = SpatialAnomalyDetector.detect(base_entity, events, localized_baseline)
    assert res.score >= 0.70
    assert "SEVERE_SPATIAL_BREACH" in res.indicators or "SPATIAL_EXPANSION" in res.indicators
    assert "EVT-S-BREACH-01" in res.evidence_event_ids


def test_spatial_sector_relocation(base_entity, localized_baseline):
    # Entity registered to SECTOR_ALPHA, but observed in SECTOR_ZULU
    events = [
        CanonicalEvent(
            event_id="EVT-S-SECTOR",
            event_type="movement",
            timestamp=datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc),
            location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_ZULU"),
            entity_ids=[base_entity.entity_id],
            attributes={"sector": "SECTOR_ZULU"},
        )
    ]
    res = SpatialAnomalyDetector.detect(base_entity, events, localized_baseline)
    assert "UNEXPECTED_SECTOR_RELOCATION" in res.indicators
    assert res.score >= 0.75


def test_spatial_unrealistic_displacement_jump(base_entity, localized_baseline):
    # Ground platform moving 80 km in 5 minutes (implied ~960 km/h)
    t0 = datetime(2026, 9, 11, 12, 0, 0, tzinfo=timezone.utc)
    events = [
        CanonicalEvent(
            event_id="EVT-JUMP-1",
            event_type="movement",
            timestamp=t0,
            location=Coordinates(latitude=26.8500, longitude=80.9500),
            entity_ids=[base_entity.entity_id],
        ),
        CanonicalEvent(
            event_id="EVT-JUMP-2",
            event_type="movement",
            timestamp=t0 + timedelta(minutes=5),
            location=Coordinates(latitude=27.5500, longitude=81.6500),
            entity_ids=[base_entity.entity_id],
        ),
    ]
    res = SpatialAnomalyDetector.detect(base_entity, events, localized_baseline)
    assert "UNREALISTIC_SPATIAL_DISPLACEMENT" in res.indicators
    assert res.score >= 0.85
