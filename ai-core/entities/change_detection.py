"""
Behavioral Change Detector for NETRA Entity Intelligence.
Identifies shifts from established baselines in kinematics (speed), operational geography
(spatial expansion), event types (novel behaviors), and operational tempo (frequency surge/drop).
"""

from typing import List, Optional
from config import EntityConfig, default_config
from models.geo import haversine_distance_km
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import (
    CanonicalEntity,
    EntityBehaviorProfile,
    BehavioralChangeItem,
    BehavioralChangeReport,
)


class BehavioralChangeDetector:
    """Detects shifts from established normal baselines for an entity."""

    def __init__(self, config: Optional[EntityConfig] = None):
        self.config = config or default_config.entity

    def detect_changes(
        self,
        entity: CanonicalEntity,
        baseline: EntityBehaviorProfile,
        all_events: List[CanonicalEvent],
    ) -> BehavioralChangeReport:
        """Evaluate recent telemetry against established baseline."""
        # Cold start gate: never report behavioral deviation without sufficient baseline
        if baseline.baseline_status == "INSUFFICIENT_HISTORY" or len(all_events) < self.config.min_observations_for_baseline:
            return BehavioralChangeReport(detected=False, score=0.0, changes=[])

        sorted_events = sorted(all_events, key=lambda x: x.timestamp)
        latest_time = sorted_events[-1].timestamp
        window_hours = self.config.recent_analysis_window_hours

        # Partition recent events within recent_analysis_window_hours of latest event
        recent_events = [
            e for e in sorted_events
            if (latest_time - e.timestamp).total_seconds() <= window_hours * 3600.0
        ]
        if not recent_events:
            recent_events = [sorted_events[-1]]

        # Historical events prior to the recent window
        historical_events = [e for e in sorted_events if e not in recent_events]
        historical_types = {e.event_type for e in historical_events} if historical_events else set()

        changes: List[BehavioralChangeItem] = []

        # 1. Kinematic Shift (Speed)
        recent_speeds = [float(e.attributes.get("speed", 0.0)) for e in recent_events]
        recent_avg_speed = sum(recent_speeds) / len(recent_speeds)

        if historical_events:
            hist_speeds = [float(e.attributes.get("speed", 0.0)) for e in historical_events]
            ref_speed = sum(hist_speeds) / len(hist_speeds) if hist_speeds else baseline.average_speed
        else:
            ref_speed = baseline.average_speed

        if ref_speed > 0:
            speed_ratio = recent_avg_speed / ref_speed
            if speed_ratio >= 1.5:
                mag = round(speed_ratio - 1.0, 2)
                changes.append(
                    BehavioralChangeItem(
                        feature="speed",
                        direction="INCREASE",
                        magnitude=mag,
                        description=f"Recent speed ({recent_avg_speed:.1f} km/h) exceeds baseline ({ref_speed:.1f} km/h) by {mag * 100:.0f}%",
                        evidence_event_ids=[e.event_id for e in recent_events if float(e.attributes.get("speed", 0.0)) > ref_speed],
                    )
                )
            elif speed_ratio <= 0.5:
                mag = round(1.0 - speed_ratio, 2)
                changes.append(
                    BehavioralChangeItem(
                        feature="speed",
                        direction="DECREASE",
                        magnitude=mag,
                        description=f"Recent speed ({recent_avg_speed:.1f} km/h) dropped below baseline ({ref_speed:.1f} km/h) by {mag * 100:.0f}%",
                        evidence_event_ids=[e.event_id for e in recent_events],
                    )
                )
        elif recent_avg_speed >= 25.0:
            mag = round(recent_avg_speed / 20.0, 2)
            changes.append(
                BehavioralChangeItem(
                    feature="speed",
                    direction="INCREASE",
                    magnitude=mag,
                    description=f"Entity accelerated from stationary baseline to {recent_avg_speed:.1f} km/h",
                    evidence_event_ids=[e.event_id for e in recent_events],
                )
            )

        # 2. Spatial Expansion
        if historical_events:
            hist_mean_lat = sum(e.location.latitude for e in historical_events) / len(historical_events)
            hist_mean_lon = sum(e.location.longitude for e in historical_events) / len(historical_events)
            from models.common import Coordinates
            ref_centroid = Coordinates(latitude=round(hist_mean_lat, 4), longitude=round(hist_mean_lon, 4))
            hist_dists = [haversine_distance_km(ref_centroid, e.location) for e in historical_events]
            base_radius = max(5.0, max(hist_dists) if hist_dists else 0.0)
        else:
            ref_centroid = baseline.spatial.centroid
            base_radius = max(5.0, baseline.spatial.bounding_radius_km)

        distances = [
            haversine_distance_km(ref_centroid, e.location)
            for e in recent_events
        ]
        max_recent_dist = max(distances) if distances else 0.0
        expansion_ratio = max_recent_dist / base_radius

        if expansion_ratio >= self.config.spatial_expansion_threshold_ratio:
            mag = round(expansion_ratio - 1.0, 2)
            ev_ids = [
                e.event_id for e, d in zip(recent_events, distances)
                if d > base_radius
            ]
            changes.append(
                BehavioralChangeItem(
                    feature="spatial_expansion",
                    direction="INCREASE",
                    magnitude=mag,
                    description=(
                        f"Entity operating {max_recent_dist:.1f} km from baseline centroid, "
                        f"exceeding bounding radius ({base_radius:.1f} km) by {mag * 100:.0f}%"
                    ),
                    evidence_event_ids=ev_ids or [recent_events[-1].event_id],
                )
            )

        # 3. Novel Event Types
        if historical_types:
            new_types = {e.event_type for e in recent_events if e.event_type not in historical_types}
            if new_types:
                sorted_new = sorted(list(new_types))
                ev_ids = [e.event_id for e in recent_events if e.event_type in new_types]
                changes.append(
                    BehavioralChangeItem(
                        feature="event_type",
                        direction="NEW",
                        magnitude=1.0,
                        description=f"Entity exhibited novel event type(s) not in baseline history: {', '.join(sorted_new)}",
                        evidence_event_ids=ev_ids,
                    )
                )

        # 4. Operational Tempo / Frequency Shift
        recent_count = len(recent_events)
        if historical_events:
            hist_span_days = max(0.5, (historical_events[-1].timestamp - historical_events[0].timestamp).total_seconds() / 86400.0)
            ref_freq = len(historical_events) / hist_span_days
        else:
            ref_freq = baseline.event_frequency_per_day

        if ref_freq > 0:
            freq_ratio = recent_count / ref_freq
            if freq_ratio >= 2.0:
                mag = round(freq_ratio - 1.0, 2)
                changes.append(
                    BehavioralChangeItem(
                        feature="frequency",
                        direction="INCREASE",
                        magnitude=mag,
                        description=f"Recent event rate ({recent_count} events/24h) surged past baseline ({ref_freq:.1f}/day)",
                        evidence_event_ids=[e.event_id for e in recent_events],
                    )
                )
            elif freq_ratio <= 0.4 and len(all_events) >= 5:
                mag = round(1.0 - freq_ratio, 2)
                changes.append(
                    BehavioralChangeItem(
                        feature="frequency",
                        direction="DECREASE",
                        magnitude=mag,
                        description=f"Recent event rate dropped significantly below baseline ({ref_freq:.1f}/day)",
                        evidence_event_ids=[e.event_id for e in recent_events],
                    )
                )

        # Compute overall change score
        detected = len(changes) > 0
        if detected:
            raw_score = sum(min(0.4, c.magnitude * 0.25) for c in changes)
            score = round(min(1.0, max(0.20, raw_score)), 2)
        else:
            score = 0.0

        return BehavioralChangeReport(
            detected=detected,
            score=score,
            changes=changes,
        )
