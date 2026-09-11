"""
Pure Python geospatial utility functions for distance and proximity.
Deterministic, dependency-free implementation of Haversine distance.
"""

import math
from .common import Coordinates


def haversine_distance_km(coord1: Coordinates, coord2: Coordinates) -> float:
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees).
    """
    lat1, lon1 = coord1.latitude, coord1.longitude
    lat2, lon2 = coord2.latitude, coord2.longitude

    # Convert decimal degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    # Clamp for numerical stability
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    earth_radius_km = 6371.0
    return earth_radius_km * c
