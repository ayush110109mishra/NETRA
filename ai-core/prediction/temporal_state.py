"""
Temporal State Representation Engine for NETRA Phase 6.
Constructs ordered temporal state sequences from irregular synthetic event telemetry,
computes sampling regularity, and tracks state evolution over time.
"""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional
import logging

from models.event_intelligence import CanonicalEvent
from models.predictive_intelligence import (
    TemporalStatePoint,
    TemporalStateSequence,
)

logger = logging.getLogger("netra.prediction.temporal_state")


class TemporalStateManager:
    """
    Transforms raw and canonical observations into an irregular time-series sequence.
    Handles irregular observation intervals, burst clustering, and gaps.
    """

    @classmethod
    def build_sequence(
        cls,
        entity_id: str,
        events: List[CanonicalEvent],
        metric_key: str = "activity_level",
    ) -> TemporalStateSequence:
        """
        Builds a chronological TemporalStateSequence for a target metric.
        """
        if not events:
            return TemporalStateSequence(
                entity_id=entity_id,
                points=[],
                sample_count=0,
                sampling_regularity=1.0,
            )

        sorted_events = sorted(events, key=lambda e: e.timestamp)
        points: List[TemporalStatePoint] = []

        for ev in sorted_events:
            val = float(ev.attributes.get(metric_key, 0.5))
            # Derive categorical state label
            if val <= 0.25:
                state_lbl = "LOW"
            elif val <= 0.60:
                state_lbl = "NOMINAL"
            elif val <= 0.85:
                state_lbl = "ELEVATED"
            else:
                state_lbl = "CRITICAL"

            points.append(TemporalStatePoint(
                timestamp=ev.timestamp,
                value=round(val, 4),
                state=state_lbl,
                metadata={
                    "event_id": ev.event_id,
                    "event_type": ev.event_type,
                    "speed": ev.attributes.get("speed"),
                },
            ))

        # Compute sampling regularity (interval standard deviation vs mean)
        regularity = 1.0
        if len(points) >= 3:
            deltas = [
                (points[i].timestamp - points[i - 1].timestamp).total_seconds()
                for i in range(1, len(points))
            ]
            mean_delta = sum(deltas) / len(deltas)
            if mean_delta > 0:
                variance = sum((d - mean_delta) ** 2 for d in deltas) / len(deltas)
                std_dev = math.sqrt(variance)
                coeff_var = std_dev / mean_delta
                # Higher coefficient of variation = less regular
                regularity = max(0.0, min(1.0, 1.0 / (1.0 + coeff_var)))

        return TemporalStateSequence(
            entity_id=entity_id,
            points=points,
            sample_count=len(points),
            sampling_regularity=round(regularity, 4),
        )
