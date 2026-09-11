"""
Event Type Anomaly Detector for NETRA Phase 4 Anomaly Intelligence.
Detects novel tactical event types, rare category surges, and behavioral taxonomy deviations.
"""

from typing import List, Dict, Optional, Any
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from models.anomaly_intelligence import DimensionScoreItem

CRITICAL_EVENT_TYPES = {
    "MISSILE_LAUNCH",
    "AIR_STRIKE",
    "RADAR_JAMMING",
    "ELECTRONIC_ATTACK",
    "BORDER_BREACH",
    "BORDER_CROSSING",
    "WEAPON_FIRING",
    "AIR_INCURSION",
    "HOSTILE_ENGAGEMENT",
}


class EventTypeAnomalyDetector:
    """Detects deviations in event taxonomy, novel capabilities, and rare event surges."""

    @staticmethod
    def detect(
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        baseline: Optional[EntityBehaviorProfile] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> DimensionScoreItem:
        """
        Evaluate event type taxonomy anomaly for entity observations.
        Returns DimensionScoreItem with normalized score [0.0 - 1.0].
        """
        if not events:
            return DimensionScoreItem(
                dimension="event_type",
                score=0.0,
                confidence=0.50,
                indicators=[],
                explanation="No recent events provided for event type evaluation.",
                evidence_event_ids=[],
            )

        indicators: List[str] = []
        evidence_ids: List[str] = []
        scores: List[float] = []

        base_types = baseline.event_type_distribution if baseline else {}

        novel_events: List[CanonicalEvent] = []
        rare_events: List[CanonicalEvent] = []

        for e in events:
            ev_type = e.event_type
            historical_prop = base_types.get(ev_type, 0.0)

            # Novel event type check
            if base_types and historical_prop == 0.0:
                novel_events.append(e)
                if ev_type.upper() in CRITICAL_EVENT_TYPES:
                    scores.append(0.90)
                    indicators.append(f"NOVEL_CRITICAL_EVENT_TYPE_{ev_type.upper()}")
                else:
                    scores.append(0.65)
                    indicators.append(f"NOVEL_EVENT_TYPE_{ev_type.upper()}")
                evidence_ids.append(e.event_id)

            # Rare event type surge (historically < 5%, now repeated)
            elif base_types and historical_prop < 0.05:
                rare_events.append(e)

        if rare_events and len(rare_events) >= 2:
            scores.append(0.70)
            indicators.append("RARE_EVENT_TYPE_SURGE")
            evidence_ids.extend([e.event_id for e in rare_events])

        # 3. Aggregate dimensional score
        if not scores:
            final_score = 0.0
            explanation = "Observed event types conform to historical operational baseline."
        else:
            final_score = min(1.0, round(max(scores), 2))
            explanation = (
                f"Event type anomaly detected (score {final_score:.2f}) with indicators: "
                f"{', '.join(set(indicators))}."
            )

        confidence = 0.90
        if not baseline or baseline.baseline_status == "INSUFFICIENT_HISTORY":
            confidence = min(confidence, 0.45)

        unique_evidence = list(dict.fromkeys(evidence_ids))

        return DimensionScoreItem(
            dimension="event_type",
            score=final_score,
            confidence=round(confidence, 2),
            indicators=list(set(indicators)),
            explanation=explanation,
            evidence_event_ids=unique_evidence,
        )
