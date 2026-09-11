"""
Test suite for NETRA Phase 5 Temporal Alignment.
"""

from datetime import datetime, timezone, timedelta
import pytest

from fusion.normalization import SourceNormalizer
from fusion.temporal_alignment import TemporalAligner


def test_clock_skew_tolerance():
    t0 = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    obs1 = SourceNormalizer.normalize_observation({"source_id": "RADAR_01", "timestamp": t0})
    obs2 = SourceNormalizer.normalize_observation({"source_id": "OPTICAL_01", "timestamp": t0 + timedelta(seconds=3)})

    aligner = TemporalAligner()
    res = aligner.align(obs1, obs2)
    assert res.is_compatible is True
    assert res.delta_seconds == 3.0
    assert res.compatibility_score == 1.0  # Within 10s clock skew tolerance


def test_near_alignment_and_window():
    t0 = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    obs1 = SourceNormalizer.normalize_observation({"source_id": "RADAR_01", "timestamp": t0})
    obs2 = SourceNormalizer.normalize_observation({"source_id": "OPTICAL_01", "timestamp": t0 + timedelta(seconds=45)})

    aligner = TemporalAligner()
    res = aligner.align(obs1, obs2)
    assert res.is_compatible is True
    assert 0.85 <= res.compatibility_score < 1.0


def test_incompatible_temporal_distance():
    t0 = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    obs1 = SourceNormalizer.normalize_observation({"source_id": "RADAR_01", "timestamp": t0})
    # 10 minutes apart (> 300s window)
    obs2 = SourceNormalizer.normalize_observation({"source_id": "OPTICAL_01", "timestamp": t0 + timedelta(minutes=10)})

    aligner = TemporalAligner()
    res = aligner.align(obs1, obs2)
    assert res.is_compatible is False
    assert res.compatibility_score == 0.0


def test_stale_observation_penalty():
    t0 = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    obs1 = SourceNormalizer.normalize_observation({"source_id": "RADAR_01", "timestamp": t0})
    # 2 hours old
    obs2 = SourceNormalizer.normalize_observation({"source_id": "SENSOR_B", "timestamp": t0 - timedelta(hours=2)})

    aligner = TemporalAligner()
    res = aligner.align(obs1, obs2, reference_time=t0)
    assert res.is_stale is True
    assert res.compatibility_score <= 0.50
