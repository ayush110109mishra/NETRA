"""
Temporal Intelligence Engine for NETRA Intelligence Core.
Analyzes time-deltas, temporal proximity, sequential progression (A -> B -> C),
event bursts, and periodic recurrence.
"""

from datetime import datetime
from typing import Tuple, List, Dict, Optional, Any
from config import NetraConfig, default_config
from models.event_intelligence import CanonicalEvent
from models.geo import haversine_distance_km


class TemporalIntelligence:
    """Deterministic temporal analysis engine."""

    def __init__(self, config: Optional[NetraConfig] = None):
        self.cfg = config or default_config

    def calculate_temporal_score(
        self,
        t1: datetime,
        t2: datetime,
        window_seconds: Optional[float] = None,
    ) -> Tuple[float, float, float]:
        """
        Calculate normalized temporal proximity score and confidence.
        Returns: (time_delta_seconds, score [0.0 - 1.0], confidence [0.0 - 1.0])
        """
        window = window_seconds or self.cfg.temporal.proximity_window_seconds
        time_delta = abs((t1 - t2).total_seconds())

        if time_delta > window:
            return time_delta, 0.0, 0.0

        # Linear decay across configured window
        score = max(0.0, min(1.0, 1.0 - (time_delta / window)))
        confidence = max(0.50, min(1.0, 0.95 - (time_delta / window) * 0.30))

        return time_delta, round(score, 4), round(confidence, 4)

    def is_sequential(
        self,
        e1: CanonicalEvent,
        e2: CanonicalEvent,
        window_seconds: Optional[float] = None,
    ) -> Tuple[bool, float]:
        """
        Check if e2 directly follows e1 in time within the sequence window.
        Returns: (is_sequential, confidence)
        """
        window = window_seconds or self.cfg.temporal.sequence_window_seconds
        delta = (e2.timestamp - e1.timestamp).total_seconds()

        # Must occur after e1 and within sequence window
        if 0 < delta <= window:
            shared_entities = set(e1.entity_ids).intersection(set(e2.entity_ids))
            if shared_entities:
                conf = round(0.95 - (delta / window) * 0.15, 2)
                return True, conf

            # Without shared entity, must at least share proximate space
            dist = haversine_distance_km(e1.location, e2.location)
            if dist <= self.cfg.spatial.proximity_km:
                conf = round(0.70 - (delta / window) * 0.20, 2)
                return True, conf

        return False, 0.0

    def detect_bursts(
        self,
        events: List[CanonicalEvent],
        window_seconds: Optional[float] = None,
        min_events: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Detect temporal bursts: clusters of >= min_events occurring within burst_window_seconds.
        """
        window = window_seconds or self.cfg.temporal.burst_window_seconds
        threshold = min_events or self.cfg.temporal.burst_min_events

        if len(events) < threshold:
            return []

        sorted_events = sorted(events, key=lambda e: e.timestamp)
        bursts: List[Dict[str, Any]] = []
        i = 0

        while i < len(sorted_events):
            start_event = sorted_events[i]
            cluster = [start_event]

            for j in range(i + 1, len(sorted_events)):
                diff = (sorted_events[j].timestamp - start_event.timestamp).total_seconds()
                if diff <= window:
                    cluster.append(sorted_events[j])
                else:
                    break

            if len(cluster) >= threshold:
                burst_ids = [e.event_id for e in cluster]
                if not any(set(burst_ids).issubset(set(b["event_ids"])) for b in bursts):
                    bursts.append({
                        "event_ids": burst_ids,
                        "event_count": len(cluster),
                        "start_time": cluster[0].timestamp,
                        "end_time": cluster[-1].timestamp,
                        "duration_seconds": (cluster[-1].timestamp - cluster[0].timestamp).total_seconds(),
                    })
            i += 1

        return bursts

    def detect_recurrence(
        self,
        events: List[CanonicalEvent],
        tolerance_seconds: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Detect periodic interval recurrence across a sequence of events.
        """
        if len(events) < 3:
            return None

        tolerance = tolerance_seconds or self.cfg.temporal.periodic_tolerance_seconds
        sorted_events = sorted(events, key=lambda e: e.timestamp)

        intervals = [
            (sorted_events[i+1].timestamp - sorted_events[i].timestamp).total_seconds()
            for i in range(len(sorted_events) - 1)
        ]

        if not intervals or any(iv <= 0 for iv in intervals):
            return None

        avg_interval = sum(intervals) / len(intervals)
        if all(abs(iv - avg_interval) <= tolerance for iv in intervals):
            return {
                "detected": True,
                "interval_seconds": round(avg_interval, 1),
                "event_count": len(sorted_events),
                "confidence": round(max(0.65, 0.95 - (max(abs(iv - avg_interval) for iv in intervals) / tolerance) * 0.3), 2),
            }

        return None
