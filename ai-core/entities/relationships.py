"""
Deterministic entity relationship detection.
Evaluates explicit spatial proximity, temporal overlap, and tactical platform similarity.
"""

from typing import List, Optional
from datetime import datetime
from models.common import RelationshipType, Coordinates
from models.input import EntityInput, ContextEntityInput
from models.output import RelatedEntityOutput
from models.geo import haversine_distance_km


def detect_entity_relationships(
    primary_entity: EntityInput,
    primary_location: Coordinates,
    primary_timestamp: datetime,
    context_entities: Optional[List[ContextEntityInput]],
    spatial_threshold_km: float = 15.0,
    temporal_threshold_seconds: float = 3600.0,
) -> List[RelatedEntityOutput]:
    """
    Detect deterministic relationships between the primary entity and context entities.
    """
    if not context_entities:
        return []

    results: List[RelatedEntityOutput] = []

    for ce in context_entities:
        if ce.entity_id == primary_entity.entity_id:
            continue  # Skip self

        # 1. Spatial proximity check
        if ce.location is not None:
            dist = haversine_distance_km(primary_location, ce.location)
            if dist <= spatial_threshold_km:
                confidence = round(max(0.55, 0.95 - (dist / spatial_threshold_km) * 0.4), 2)
                results.append(
                    RelatedEntityOutput(
                        entity_id=ce.entity_id,
                        relationship=RelationshipType.SPATIAL_PROXIMITY,
                        confidence=confidence,
                        details=f"Entity active within {dist:.2f} km in sector",
                    )
                )
                continue

        # 2. Temporal association check
        if ce.last_seen is not None:
            time_diff = abs((primary_timestamp - ce.last_seen).total_seconds())
            if time_diff <= temporal_threshold_seconds:
                confidence = round(max(0.5, 0.80 - (time_diff / temporal_threshold_seconds) * 0.3), 2)
                results.append(
                    RelatedEntityOutput(
                        entity_id=ce.entity_id,
                        relationship=RelationshipType.TEMPORAL_ASSOCIATION,
                        confidence=confidence,
                        details=f"Concurrent activity within {int(time_diff / 60)} minutes",
                    )
                )
                continue

        # 3. Similar type check
        if ce.entity_type.lower() == primary_entity.entity_type.lower():
            results.append(
                RelatedEntityOutput(
                    entity_id=ce.entity_id,
                    relationship=RelationshipType.SIMILAR_TYPE,
                    confidence=0.60,
                    details=f"Matching platform category ({ce.entity_type})",
                )
            )

    return results
