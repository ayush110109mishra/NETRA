"""
Unit tests for Spatial Intelligence Engine.
Tests Haversine proximity, SAME_LOCATION boundary, distant decoupling, and spatial extent calculations.
"""

import pytest
from models.common import Coordinates
from events.spatial import SpatialIntelligence

LOC1 = Coordinates(latitude=26.8467, longitude=80.9462)
# ~50 meters away
LOC_VERY_CLOSE = Coordinates(latitude=26.8470, longitude=80.9464)
# ~5 km away
LOC_PROXIMATE = Coordinates(latitude=26.8800, longitude=80.9800)
# ~120 km away
LOC_DISTANT = Coordinates(latitude=27.9000, longitude=81.9000)


def test_spatial_proximity_scoring():
    """Verify close coordinates receive high scores and distant coordinates receive 0.0."""
    spatial = SpatialIntelligence()

    # Close coordinates (~50m)
    dist, score, conf = spatial.calculate_spatial_score(LOC1, LOC_VERY_CLOSE, max_proximity_km=15.0)
    assert dist < 0.1
    assert score >= 0.95
    assert conf >= 0.90

    # Distant coordinates (> 100km)
    dist2, score2, conf2 = spatial.calculate_spatial_score(LOC1, LOC_DISTANT, max_proximity_km=15.0)
    assert dist2 > 100.0
    assert score2 == 0.0
    assert conf2 == 0.0


def test_is_same_location():
    """Verify points within 200m are classified as SAME_LOCATION."""
    spatial = SpatialIntelligence()
    is_same, conf = spatial.is_same_location(LOC1, LOC_VERY_CLOSE, threshold_km=0.20)
    assert is_same is True
    assert conf >= 0.70

    is_same_far, _ = spatial.is_same_location(LOC1, LOC_PROXIMATE, threshold_km=0.20)
    assert is_same_far is False


def test_compute_spatial_extent():
    """Verify cluster bounding box, centroid, and bounding radius."""
    spatial = SpatialIntelligence()
    coords = [LOC1, LOC_VERY_CLOSE, LOC_PROXIMATE]
    extent = spatial.compute_spatial_extent(coords)

    assert "min_latitude" in extent
    assert "max_latitude" in extent
    assert "centroid_latitude" in extent
    assert "bounding_radius_km" in extent
    assert extent["min_latitude"] <= extent["max_latitude"]
    assert extent["bounding_radius_km"] > 0.0
