"""
Kinematic Anomaly Detector for NETRA Phase 4 Anomaly Intelligence.
Detects extreme velocity surges, platform-incompatible speeds, rapid acceleration,
and deviations from historical kinematic envelopes.
"""

from typing import List, Dict, Optional, Any
from models.common import Coordinates
from models.geo import haversine_distance_km
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from models.anomaly_intelligence import DimensionScoreItem


class KinematicAnomalyDetector:
    """Detects kinematic anomalies, speed surges, and velocity envelope breaches."""

    @staticmethod
    def detect(
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        baseline: Optional[EntityBehaviorProfile] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> DimensionScoreItem:
        """
        Evaluate kinematic anomaly for entity observations.
        Returns DimensionScoreItem with normalized score [0.0 - 1.0].
        """
        if not events:
            return DimensionScoreItem(
                dimension="kinematic",
                score=0.0,
                confidence=0.50,
                indicators=[],
                explanation="No recent events provided for kinematic evaluation.",
                evidence_event_ids=[],
            )

        indicators: List[str] = []
        evidence_ids: List[str] = []
        scores: List[float] = []

        ent_type = (entity.entity_type or "UNKNOWN").upper()
        # Fallback to event attributes if entity type is UNKNOWN
        if ent_type == "UNKNOWN" and events:
            for ev in events:
                if "entity_type" in ev.attributes:
                    ent_type = str(ev.attributes["entity_type"]).upper()
                    break

        is_ground = ent_type in ["VEHICLE", "PATROL_UNIT", "GROUND_FORCE", "CONVOY", "UNKNOWN"]
        is_naval = ent_type in ["VESSEL", "SUBMARINE", "WARSHIP", "PATROL_BOAT"]
        is_air = ent_type in ["AIRCRAFT", "DRONE", "UAV", "FIGHTER", "JET"]

        base_speed = baseline.average_speed if (baseline and baseline.average_speed > 0) else 0.0

        # 1. Attribute-reported speeds
        for e in events:
            raw_speed = e.attributes.get("speed")
            if raw_speed is None:
                raw_speed = e.attributes.get("speed_kmh")

            if raw_speed is not None:
                try:
                    speed = float(raw_speed)
                except (ValueError, TypeError):
                    continue

                # Ground platform overspeed (or unknown non-air platform overspeed)
                if not is_air and not is_naval and speed > 110.0:
                    scores.append(min(1.0, round(0.70 + (speed - 110.0) * 0.005, 2)))
                    indicators.append("GROUND_SPEED_EXCESS")
                    evidence_ids.append(e.event_id)

                # Naval overspeed
                elif is_naval and speed > 70.0:
                    scores.append(0.85)
                    indicators.append("NAVAL_SPEED_EXCESS")
                    evidence_ids.append(e.event_id)

                # Baseline deviation
                if base_speed > 5.0 and speed >= (2.5 * base_speed) and speed > 40.0:
                    ratio = speed / base_speed
                    surge_score = min(1.0, round(0.50 + (ratio - 2.5) * 0.15, 2))
                    scores.append(surge_score)
                    indicators.append("KINEMATIC_SPEED_SPIKE")
                    evidence_ids.append(e.event_id)

        # 2. Implied speed between consecutive coordinates
        if len(events) >= 2:
            sorted_events = sorted(events, key=lambda x: x.timestamp)
            for i in range(len(sorted_events) - 1):
                e1, e2 = sorted_events[i], sorted_events[i + 1]
                dt_seconds = (e2.timestamp - e1.timestamp).total_seconds()
                if 1.0 <= dt_seconds <= 7200.0:
                    dist_km = haversine_distance_km(e1.coordinates, e2.coordinates)
                    implied_speed = dist_km / (dt_seconds / 3600.0)

                    if is_ground and implied_speed > 120.0:
                        scores.append(0.85)
                        indicators.append("IMPLIED_GROUND_OVERSPEED")
                        evidence_ids.extend([e1.event_id, e2.event_id])
                    elif base_speed > 10.0 and implied_speed > (3.0 * base_speed):
                        scores.append(0.80)
                        indicators.append("KINEMATIC_VELOCITY_SURGE")
                        evidence_ids.extend([e1.event_id, e2.event_id])

        # 3. Aggregate dimensional score
        if not scores:
            final_score = 0.0
            explanation = "Kinematic profile within nominal operational parameters."
        else:
            final_score = min(1.0, round(max(scores), 2))
            explanation = (
                f"Kinematic anomaly detected (score {final_score:.2f}) with indicators: "
                f"{', '.join(set(indicators))}."
            )

        confidence = 0.90
        if not baseline or baseline.baseline_status == "INSUFFICIENT_HISTORY":
            confidence = min(confidence, 0.50)
        if not evidence_ids:
            confidence = 0.80

        unique_evidence = list(dict.fromkeys(evidence_ids))

        return DimensionScoreItem(
            dimension="kinematic",
            score=final_score,
            confidence=round(confidence, 2),
            indicators=list(set(indicators)),
            explanation=explanation,
            evidence_event_ids=unique_evidence,
        )
