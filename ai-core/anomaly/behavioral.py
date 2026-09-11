"""
Behavioral Anomaly Detector for NETRA Phase 4 Anomaly Intelligence.
Assesses composite behavioral drift, activity level surges, operational posture changes,
and multi-feature baseline divergence.
"""

from typing import List, Dict, Optional, Any
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from models.anomaly_intelligence import DimensionScoreItem


class BehavioralAnomalyDetector:
    """Detects composite behavioral drift and operational posture divergence."""

    @staticmethod
    def detect(
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        baseline: Optional[EntityBehaviorProfile] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> DimensionScoreItem:
        """
        Evaluate behavioral anomaly for entity observations.
        Returns DimensionScoreItem with normalized score [0.0 - 1.0].
        """
        if not events:
            return DimensionScoreItem(
                dimension="behavioral",
                score=0.0,
                confidence=0.50,
                indicators=[],
                explanation="No recent events provided for behavioral evaluation.",
                evidence_event_ids=[],
            )

        indicators: List[str] = []
        evidence_ids: List[str] = []
        scores: List[float] = []

        base_activity = baseline.average_activity if baseline else 0.5

        # 1. Activity Level Telemetry Drift
        activity_levels: List[float] = []
        for e in events:
            raw_act = e.attributes.get("activity_level")
            if raw_act is not None:
                try:
                    act = float(raw_act)
                    activity_levels.append(act)
                    if act >= 0.85:
                        indicators.append("HIGH_ACTIVITY_TELEMETRY")
                        evidence_ids.append(e.event_id)
                except (ValueError, TypeError):
                    pass

        if activity_levels:
            avg_curr_act = sum(activity_levels) / len(activity_levels)
            act_delta = abs(avg_curr_act - base_activity)

            if avg_curr_act >= 0.85:
                scores.append(round(avg_curr_act, 2))
                indicators.append("PEAK_ACTIVITY_EXCURSION")
            elif act_delta >= 0.40:
                scores.append(min(0.80, round(0.40 + act_delta * 0.8, 2)))
                indicators.append("ACTIVITY_PROFILE_DRIFT")

        # 2. Operational Posture / Alert Status Shift
        for e in events:
            op_status = str(e.attributes.get("operational_status", "")).upper()
            if op_status in ["ALERT", "HOSTILE_ENGAGED", "COMBAT_READY", "EMERGENCY"]:
                scores.append(0.85)
                indicators.append(f"POSTURE_ESCALATION_{op_status}")
                evidence_ids.append(e.event_id)

        # 3. Aggregate dimensional score
        if not scores:
            final_score = 0.0
            explanation = "Behavioral telemetry conforms to historical baseline profile."
        else:
            final_score = min(1.0, round(max(scores), 2))
            explanation = (
                f"Behavioral anomaly detected (score {final_score:.2f}) with indicators: "
                f"{', '.join(set(indicators))}."
            )

        confidence = 0.85
        if not baseline or baseline.baseline_status == "INSUFFICIENT_HISTORY":
            confidence = min(confidence, 0.50)

        unique_evidence = list(dict.fromkeys(evidence_ids))

        return DimensionScoreItem(
            dimension="behavioral",
            score=final_score,
            confidence=round(confidence, 2),
            indicators=list(set(indicators)),
            explanation=explanation,
            evidence_event_ids=unique_evidence,
        )
