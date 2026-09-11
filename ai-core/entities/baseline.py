"""
Behavioral Baseline Engine for NETRA Entity Intelligence.
Computes multi-dimensional operational baselines including cold-start handling,
frequency, activity, speed, spatial, temporal, and event type distributions.
"""

from typing import List, Dict, Optional
from collections import Counter
from config import EntityConfig, default_config
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from entities.spatial_behavior import SpatialBehaviorAnalyzer
from entities.temporal_behavior import TemporalBehaviorAnalyzer


class BehavioralBaselineEngine:
    """Computes behavioral baselines from historical synthetic telemetry."""

    def __init__(self, config: Optional[EntityConfig] = None):
        self.config = config or default_config.entity

    def compute_baseline(
        self,
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
    ) -> EntityBehaviorProfile:
        """Compute normal synthetic baseline for the entity."""
        sample_count = len(events)
        is_cold_start = sample_count < self.config.min_observations_for_baseline
        baseline_status = "INSUFFICIENT_HISTORY" if is_cold_start else "SUFFICIENT_HISTORY"

        if sample_count == 0:
            spatial = SpatialBehaviorAnalyzer.analyze([])
            temporal = TemporalBehaviorAnalyzer.analyze([])
            return EntityBehaviorProfile(
                baseline_status="INSUFFICIENT_HISTORY",
                sample_count=0,
                event_frequency_per_day=0.0,
                average_activity=0.0,
                average_speed=0.0,
                spatial=spatial,
                temporal=temporal,
                event_type_distribution={},
            )

        # 1. Frequency calculation (events per day)
        time_span_seconds = max(0.0, (entity.last_observed - entity.first_observed).total_seconds())
        active_days = max(1.0, time_span_seconds / 86400.0)
        event_frequency_per_day = round(sample_count / active_days, 2)

        # 2. Average activity level [0.0 - 1.0]
        activity_levels = [
            float(e.attributes.get("activity_level", 0.5))
            for e in events
        ]
        average_activity = round(sum(activity_levels) / len(activity_levels), 2)

        # 3. Average speed (km/h)
        speeds = [
            float(e.attributes.get("speed", 0.0))
            for e in events
        ]
        average_speed = round(sum(speeds) / len(speeds), 2)

        # 4. Spatial and Temporal baseline behaviors
        spatial = SpatialBehaviorAnalyzer.analyze(events)
        temporal = TemporalBehaviorAnalyzer.analyze(events)

        # 5. Event type distribution
        type_counts = Counter(e.event_type for e in events)
        event_type_distribution: Dict[str, float] = {
            t: round(count / sample_count, 3)
            for t, count in type_counts.items()
        }

        return EntityBehaviorProfile(
            baseline_status=baseline_status,
            sample_count=sample_count,
            event_frequency_per_day=event_frequency_per_day,
            average_activity=average_activity,
            average_speed=average_speed,
            spatial=spatial,
            temporal=temporal,
            event_type_distribution=event_type_distribution,
        )
