"""
Test suite for NETRA Phase 5 Spatial Alignment.
"""

import pytest

from fusion.normalization import SourceNormalizer
from fusion.spatial_alignment import SpatialAligner
from models.fusion_intelligence import SpatialAlignmentLevel


def test_spatial_agreement_exact():
    obs1 = SourceNormalizer.normalize_observation({
        "source_id": "RADAR_01",
        "latitude": 34.0500,
        "longitude": 74.8000,
        "position_uncertainty_km": 0.10,
    })
    obs2 = SourceNormalizer.normalize_observation({
        "source_id": "OPTICAL_01",
        "latitude": 34.0502,
        "longitude": 74.8002,
        "position_uncertainty_km": 0.05,
    })

    aligner = SpatialAligner()
    res = aligner.align(obs1, obs2)
    assert res.alignment_level == SpatialAlignmentLevel.AGREEMENT
    assert res.distance_km < 0.10
    assert res.spatial_compatibility_score >= 0.85


def test_spatial_partial_agreement_uncertainty_overlap():
    obs1 = SourceNormalizer.normalize_observation({
        "source_id": "RADAR_01",
        "latitude": 34.0500,
        "longitude": 74.8000,
        "position_uncertainty_km": 1.0,
    })
    obs2 = SourceNormalizer.normalize_observation({
        "source_id": "SIGNAL_01",
        "latitude": 34.0600,
        "longitude": 74.8100,
        "position_uncertainty_km": 1.5,
    })

    aligner = SpatialAligner()
    res = aligner.align(obs1, obs2)
    assert res.alignment_level in (SpatialAlignmentLevel.AGREEMENT, SpatialAlignmentLevel.PARTIAL_AGREEMENT)
    assert res.uncertainty_overlap is True
    assert res.spatial_compatibility_score >= 0.50


def test_spatial_conflict_divergent():
    obs1 = SourceNormalizer.normalize_observation({
        "source_id": "RADAR_01",
        "latitude": 34.0500,
        "longitude": 74.8000,
        "position_uncertainty_km": 0.10,
    })
    obs2 = SourceNormalizer.normalize_observation({
        "source_id": "SENSOR_B",
        "latitude": 34.4000,
        "longitude": 75.1500,
        "position_uncertainty_km": 0.20,
    })

    aligner = SpatialAligner()
    res = aligner.align(obs1, obs2)
    assert res.alignment_level == SpatialAlignmentLevel.CONFLICT
    assert res.distance_km > 25.0
    assert res.spatial_compatibility_score <= 0.30
    assert "CONFLICT" in res.explanation
