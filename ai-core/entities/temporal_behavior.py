"""
Temporal behavior analyzer for NETRA Entity Intelligence.
Analyzes hourly activity distribution, peak active hours, and inter-event intervals.
"""

from typing import List, Dict
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import EntityTemporalBehavior


class TemporalBehaviorAnalyzer:
    """Computes temporal cadence and distribution for an entity."""

    @staticmethod
    def analyze(events: List[CanonicalEvent]) -> EntityTemporalBehavior:
        """Analyze temporal patterns across an entity's event history."""
        if not events:
            return EntityTemporalBehavior(
                peak_activity_hour=0,
                average_inter_event_minutes=0.0,
                hourly_distribution={h: 0.0 for h in range(24)},
            )

        # 1. Hourly distribution [0-23]
        hour_counts: Dict[int, int] = {h: 0 for h in range(24)}
        for e in events:
            hour_counts[e.timestamp.hour] = hour_counts.get(e.timestamp.hour, 0) + 1

        total_events = len(events)
        hourly_distribution: Dict[int, float] = {
            h: round(count / total_events, 4) for h, count in hour_counts.items()
        }

        # 2. Peak activity hour (highest count, deterministic lowest hour on tie)
        peak_hour = max(range(24), key=lambda h: (hour_counts[h], -h))

        # 3. Average inter-event interval in minutes
        if len(events) <= 1:
            avg_inter_event = 0.0
        else:
            sorted_events = sorted(events, key=lambda x: x.timestamp)
            deltas = [
                (sorted_events[i + 1].timestamp - sorted_events[i].timestamp).total_seconds() / 60.0
                for i in range(len(sorted_events) - 1)
            ]
            avg_inter_event = round(sum(deltas) / len(deltas), 2)

        return EntityTemporalBehavior(
            peak_activity_hour=peak_hour,
            average_inter_event_minutes=avg_inter_event,
            hourly_distribution=hourly_distribution,
        )
