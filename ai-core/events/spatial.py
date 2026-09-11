"""
Spatial Intelligence Engine for NETRA Intelligence Core.
Reuses pure-Python Haversine distance from models/geo.py.
Computes spatial proximity scores, evaluates SAME_LOCATION boundaries,
and calculates geographic cluster extents (bounding boxes and centroids).
"""

from typing import Tuple, List, Dict, Optional, Any
from config import NetraConfig, default_config
from models.common import Coordinates, RelationshipType
from models.geo import haversine_distance_km


class SpatialIntelligence:
    """Deterministic spatial intelligence engine."""

    def __init__(self, config: Optional[NetraConfig] = None):
        self.cfg = config or default_config

    def calculate_spatial_score(
        self,
        loc1: Coordinates,
        loc2: Coordinates,
        max_proximity_km: Optional[float] = None,
    ) -> Tuple[float, float, float]:
        """
        Calculate distance, normalized spatial score, and confidence.
        Returns: (distance_km, score [0.0 - 1.0], confidence [0.0 - 1.0])
        """
        max_dist = max_proximity_km or self.cfg.spatial.proximity_km
        distance_km = haversine_distance_km(loc1, loc2)

        if distance_km > max_dist:
            return round(distance_km, 3), 0.0, 0.0

        # Linear decay across proximity threshold
        score = max(0.0, min(1.0, 1.0 - (distance_km / max_dist)))
        # High confidence for close observations
        confidence = max(0.50, min(1.0, 0.95 - (distance_km / max_dist) * 0.25))

        return round(distance_km, 3), round(score, 4), round(confidence, 4)

    def is_same_location(
        self,
        loc1: Coordinates,
        loc2: Coordinates,
        threshold_km: Optional[float] = None,
    ) -> Tuple[bool, float]:
        """
        Check if two coordinates represent the same immediate tactical location.
        Default threshold: 0.20 km (200 meters).
        """
        limit = threshold_km or self.cfg.spatial.same_location_km
        dist = haversine_distance_km(loc1, loc2)

        if dist <= limit:
            confidence = round(max(0.70, 1.0 - (dist / limit) * 0.25), 2)
            return True, confidence

        return False, 0.0

    def compute_spatial_extent(self, coordinates: List[Coordinates]) -> Dict[str, Any]:
        """
        Compute spatial bounding box, centroid, and bounding radius for a group of coordinates.
        """
        if not coordinates:
            return {}

        lats = [c.latitude for c in coordinates]
        lons = [c.longitude for c in coordinates]

        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)

        centroid_lat = sum(lats) / len(lats)
        centroid_lon = sum(lons) / len(lons)
        centroid = Coordinates(latitude=centroid_lat, longitude=centroid_lon)

        # Compute max radius from centroid
        max_radius_km = max(haversine_distance_km(centroid, c) for c in coordinates)

        return {
            "min_latitude": round(min_lat, 6),
            "max_latitude": round(max_lat, 6),
            "min_longitude": round(min_lon, 6),
            "max_longitude": round(max_lon, 6),
            "centroid_latitude": round(centroid_lat, 6),
            "centroid_longitude": round(centroid_lon, 6),
            "bounding_radius_km": round(max_radius_km, 3),
        }
