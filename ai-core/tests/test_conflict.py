"""
Test suite for NETRA Phase 5 Conflict Detection and Contradiction Preservation.
"""

from datetime import datetime, timezone
import pytest

from fusion.normalization import SourceNormalizer
from fusion.conflict import ConflictDetector
from models.fusion_intelligence import ConflictType, ConflictStatus


def test_position_conflict_preservation():
    obs1 = SourceNormalizer.normalize_observation({
        "source_id": "RADAR_01",
        "latitude": 34.0500,
        "longitude": 74.8000,
        "entity_hint": "ENTITY-07",
    })
    obs2 = SourceNormalizer.normalize_observation({
        "source_id": "SENSOR_B",
        "latitude": 34.4000,
        "longitude": 75.1500,
        "entity_hint": "ENTITY-07",
    })

    detector = ConflictDetector()
    conflicts = detector.detect_conflicts([obs1, obs2])
    assert len(conflicts) >= 1
    pos_conf = next(c for c in conflicts if c.conflict_type == ConflictType.POSITION)
    assert pos_conf.conflict_type == ConflictType.POSITION
    # Both source claims must be preserved!
    assert "RADAR_01" in pos_conf.claims
    assert "SENSOR_B" in pos_conf.claims
    assert pos_conf.claims["RADAR_01"]["latitude"] == 34.0500
    assert pos_conf.claims["SENSOR_B"]["latitude"] == 34.4000
    # RADAR_01 (rel 0.90) vs SENSOR_B (rel 0.50) -> diff 0.40 >= 0.25 -> RESOLVED favoring RADAR_01
    assert pos_conf.status == ConflictStatus.RESOLVED
    assert pos_conf.resolved_claim is not None


def test_velocity_conflict():
    obs1 = SourceNormalizer.normalize_observation({
        "source_id": "RADAR_01",
        "speed_kmh": 30.0,
        "heading_deg": 10.0,
    })
    obs2 = SourceNormalizer.normalize_observation({
        "source_id": "SENSOR_A",
        "speed_kmh": 140.0,
        "heading_deg": 190.0,
    })

    detector = ConflictDetector()
    conflicts = detector.detect_conflicts([obs1, obs2])
    assert len(conflicts) >= 1
    vel_conf = next(c for c in conflicts if c.conflict_type == ConflictType.VELOCITY)
    assert vel_conf.conflict_type == ConflictType.VELOCITY
    assert "RADAR_01" in vel_conf.claims
    assert "SENSOR_A" in vel_conf.claims


def test_event_type_conflict():
    obs1 = SourceNormalizer.normalize_observation({
        "source_id": "RADAR_01",
        "event_type": "ROUTINE_PATROL",
    })
    obs2 = SourceNormalizer.normalize_observation({
        "source_id": "SIGNAL_01",
        "event_type": "RADAR_JAMMING_ATTACK",
    })

    detector = ConflictDetector()
    conflicts = detector.detect_conflicts([obs1, obs2])
    assert len(conflicts) >= 1
    type_conf = next(c for c in conflicts if c.conflict_type == ConflictType.EVENT_TYPE)
    assert "ROUTINE_PATROL" in type_conf.claims["RADAR_01"]["event_type"]
    assert "RADAR_JAMMING_ATTACK" in type_conf.claims["SIGNAL_01"]["event_type"]
