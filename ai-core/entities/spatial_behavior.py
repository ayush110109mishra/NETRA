"""
Spatial behavior analyzer for NETRA Entity Intelligence.
Extracts geographic centroid, operational bounding radius, spatial concentration index,
and sector associations from canonical events.
"""

from typing import List
from models.common import Coordinates
from models.geo import haversine_distance_km
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import EntitySpatialBehavior


class SpatialBehaviorAnalyzer:
    """Computes spatial behavioral footprint and concentration metrics for an entity."""

    @staticmethod
    def analyze(events: List[CanonicalEvent]) -> EntitySpatialBehavior:
        """Analyze spatial patterns across an entity's event history."""
        if not events:
            return EntitySpatialBehavior(
                centroid=Coordinates(latitude=0.0, longitude=0.0),
                bounding_radius_km=0.0,
                spatial_concentration=1.0,
                frequent_sectors=[],
            )

        # 1. Compute Centroid
        mean_lat = sum(e.location.latitude for e in events) / len(events)
        mean_lon = sum(e.location.longitude for e in events) / len(events)
        centroid = Coordinates(
            latitude=round(mean_lat, 4),
            longitude=round(mean_lon, 4),
        )

        # 2. Compute Bounding Radius (maximum distance from centroid)
        distances = [haversine_distance_km(centroid, e.location) for e in events]
        bounding_radius_km = round(max(distances), 2) if distances else 0.0

        # 3. Spatial Concentration Index [0.0 - 1.0]
        # Higher score means tightly clustered; lower means widely dispersed
        if bounding_radius_km <= 0.1:
            concentration = 1.0
        else:
            concentration = round(max(0.0, min(1.0, 1.0 / (1.0 + (bounding_radius_km / 10.0)))), 2)

        # 4. Identify Frequent Operational Sectors
        sectors = set()
        for e in events:
            if e.location.sector_id:
                sectors.add(e.location.sector_id)
        
        sorted_sectors = sorted(list(sectors))

        return EntitySpatialBehavior(
            centroid=centroid,
            bounding_radius_km=bounding_radius_km,
            spatial_concentration=concentration,
            frequent_sectors=sorted_sectors,
        )
