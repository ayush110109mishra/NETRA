"""
Entity Profile Aggregator for NETRA Entity Intelligence.
Synthesizes high-level descriptive profile metrics for an entity.
"""

from typing import List
from collections import Counter
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityProfile


class EntityProfileAggregator:
    """Aggregates descriptive profile metrics for an entity."""

    @staticmethod
    def aggregate(
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        associated_entities_count: int = 0,
        associated_clusters_count: int = 0,
    ) -> EntityProfile:
        """Construct descriptive EntityProfile."""
        # 1. Active duration in hours
        duration_seconds = max(0.0, (entity.last_observed - entity.first_observed).total_seconds())
        active_hours = round(duration_seconds / 3600.0, 2)

        # 2. Unique locations count
        unique_locs = {
            (round(e.location.latitude, 4), round(e.location.longitude, 4))
            for e in events
        }
        unique_locations_count = max(1, len(unique_locs)) if events else 1

        # 3. Dominant event type
        if events:
            type_counts = Counter(e.event_type for e in events)
            # Deterministic: highest count, alphabetical key on tie
            dominant_event_type = sorted(
                type_counts.keys(),
                key=lambda k: (-type_counts[k], k)
            )[0]
        else:
            dominant_event_type = "UNKNOWN"

        return EntityProfile(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            active_duration_hours=active_hours,
            unique_locations_count=unique_locations_count,
            dominant_event_type=dominant_event_type,
            associated_entities_count=associated_entities_count,
            associated_clusters_count=associated_clusters_count,
        )
