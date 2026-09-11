"""
Event Deduplication Engine for NETRA Intelligence Core.
Detects exact duplicates and near-duplicates across synthetic telemetry feeds.
Marks events with explicit audit reasoning and confidence without deletion.
"""

from typing import List, Optional
from config import NetraConfig, default_config
from models.event_intelligence import CanonicalEvent, DuplicateAnalysisResult
from models.geo import haversine_distance_km


class EventDeduplicator:
    """Deterministic event deduplication engine."""

    def __init__(self, config: Optional[NetraConfig] = None):
        self.cfg = config or default_config

    def analyze_duplicates(self, events: List[CanonicalEvent]) -> List[DuplicateAnalysisResult]:
        """
        Analyze a batch of canonical events for exact and near-duplicates.
        Returns a list of DuplicateAnalysisResult matching each event.
        """
        if not self.cfg.deduplication.enabled or not events:
            return [
                DuplicateAnalysisResult(event_id=e.event_id, is_duplicate=False)
                for e in events
            ]

        results: List[DuplicateAnalysisResult] = []
        seen_events: List[CanonicalEvent] = []
        exact_time_lim = self.cfg.deduplication.exact_time_window_seconds
        near_time_lim = self.cfg.deduplication.near_time_window_seconds
        exact_dist_lim = self.cfg.deduplication.exact_distance_km
        near_dist_lim = self.cfg.deduplication.near_distance_km

        for current in events:
            found_dup = False

            for original in seen_events:
                # Check 1: Exact Event ID duplicate
                if current.event_id == original.event_id:
                    results.append(
                        DuplicateAnalysisResult(
                            event_id=current.event_id,
                            is_duplicate=True,
                            duplicate_of=original.event_id,
                            confidence=1.0,
                            reasons=["identical_event_id"],
                        )
                    )
                    found_dup = True
                    break

                # Check entity overlap
                shared_entities = set(current.entity_ids).intersection(set(original.entity_ids))
                same_type = (current.event_type.upper() == original.event_type.upper())
                time_delta = abs((current.timestamp - original.timestamp).total_seconds())
                distance = haversine_distance_km(current.location, original.location)

                # Check 2: Exact Duplicate Telemetry
                # Same entity + same event type + dist <= 50m + time <= 5s
                if shared_entities and same_type and distance <= exact_dist_lim and time_delta <= exact_time_lim:
                    reasons = ["same_entity", "same_location", "near_identical_timestamp", "same_event_type"]
                    results.append(
                        DuplicateAnalysisResult(
                            event_id=current.event_id,
                            is_duplicate=True,
                            duplicate_of=original.event_id,
                            confidence=0.98,
                            reasons=reasons,
                        )
                    )
                    found_dup = True
                    break

                # Check 3: Near Duplicate Telemetry
                # Same entity + same event type + dist <= 200m + time <= 60s + similar speed
                if shared_entities and same_type and distance <= near_dist_lim and time_delta <= near_time_lim:
                    reasons = ["same_entity", "near_location", "proximate_timestamp", "same_event_type"]
                    curr_spd = current.attributes.get("speed", 0.0)
                    orig_spd = original.attributes.get("speed", 0.0)
                    if abs(curr_spd - orig_spd) <= 5.0:
                        reasons.append("matching_telemetry_signature")

                    results.append(
                        DuplicateAnalysisResult(
                            event_id=current.event_id,
                            is_duplicate=True,
                            duplicate_of=original.event_id,
                            confidence=0.88,
                            reasons=reasons,
                        )
                    )
                    found_dup = True
                    break

            if not found_dup:
                results.append(
                    DuplicateAnalysisResult(
                        event_id=current.event_id,
                        is_duplicate=False,
                        confidence=1.0,
                    )
                )
                seen_events.append(current)

        return results
