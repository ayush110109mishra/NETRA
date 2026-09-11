"""
Test suite for NETRA Phase 5 Source Normalization and Traceability.
"""

from datetime import datetime, timezone
import pytest

from fusion.normalization import SourceNormalizer


def test_normalization_coordinate_aliases():
    raw_payload = {
        "source_id": "RADAR_01",
        "lat": 34.0500,
        "lon": 74.8000,
        "alt_m": 1200.0,
        "sector": "SECTOR_NORTH",
        "timestamp": "2026-09-12T12:00:00Z",
    }
    obs = SourceNormalizer.normalize_observation(raw_payload)
    assert obs.position is not None
    assert obs.position.latitude == 34.0500
    assert obs.position.longitude == 74.8000
    assert obs.position.altitude_m == 1200.0
    assert obs.position.sector_id == "SECTOR_NORTH"
    assert any(t.field == "position.latitude" for t in obs.normalization_trace)
    assert any(t.field == "position.longitude" for t in obs.normalization_trace)


def test_normalization_velocity_units():
    # Test m/s conversion to km/h (10 m/s * 3.6 = 36.0 km/h)
    raw_mps = {
        "source_id": "OPTICAL_01",
        "velocity_mps": 10.0,
        "course": 180.0,
        "time": "2026-09-12T12:00:00Z",
    }
    obs_mps = SourceNormalizer.normalize_observation(raw_mps)
    assert obs_mps.velocity is not None
    assert obs_mps.velocity.speed_kmh == 36.0
    assert obs_mps.velocity.heading_deg == 180.0

    # Test knots conversion (20 knots * 1.852 = 37.04 km/h)
    raw_kts = {
        "source_id": "RADAR_01",
        "speed_knots": 20.0,
        "bearing": 45.0,
        "time": "2026-09-12T12:00:00Z",
    }
    obs_kts = SourceNormalizer.normalize_observation(raw_kts)
    assert obs_kts.velocity is not None
    assert obs_kts.velocity.speed_kmh == 37.04
    assert obs_kts.velocity.heading_deg == 45.0


def test_normalization_entity_hints_and_event_types():
    raw = {
        "source_id": "TELEMETRY_01",
        "track_id": "R-104",
        "event": "patrol_movement",
        "timestamp": 1789214400,  # Epoch timestamp
    }
    obs = SourceNormalizer.normalize_observation(raw)
    assert obs.entity_hint == "R-104"
    assert obs.event_type == "PATROL_MOVEMENT"
    assert obs.timestamp.tzinfo is not None
    assert obs.raw_data == raw


def test_deterministic_observation_id():
    raw1 = {"source_id": "SENSOR_A", "lat": 34.0, "lon": 74.0, "time": "2026-09-12T12:00:00Z"}
    raw2 = {"source_id": "SENSOR_A", "lat": 34.0, "lon": 74.0, "time": "2026-09-12T12:00:00Z"}
    obs1 = SourceNormalizer.normalize_observation(raw1)
    obs2 = SourceNormalizer.normalize_observation(raw2)
    assert obs1.observation_id == obs2.observation_id
    assert obs1.observation_id.startswith("OBS-")
