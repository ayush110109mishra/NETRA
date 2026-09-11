"""
Frequency Anomaly Detector for NETRA Phase 4 Anomaly Intelligence.
Measures event density, rate of observation, burst volume, and abnormal
cadence shifts against historical baseline event frequencies.
"""

from typing import List, Dict, Optional, Any
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from models.anomaly_intelligence import DimensionScoreItem


class FrequencyAnomalyDetector:
    """Detects event volume surges, rapid firing rates, and cadence anomalies."""

    @staticmethod
    def detect(
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        baseline: Optional[EntityBehaviorProfile] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> DimensionScoreItem:
        """
        Evaluate frequency anomaly for entity observations.
        Returns DimensionScoreItem with normalized score [0.0 - 1.0].
        """
        if not events:
            return DimensionScoreItem(
                dimension="frequency",
                score=0.0,
                confidence=0.50,
                indicators=[],
                explanation="No recent events provided for frequency evaluation.",
                evidence_event_ids=[],
            )

        indicators: List[str] = []
        evidence_ids: List[str] = [e.event_id for e in events]
        scores: List[float] = []

        count = len(events)
        base_rate = (
            baseline.event_frequency_per_day
            if (baseline and baseline.event_frequency_per_day > 0)
            else 2.0
        )

        # 1. Calculate observed rate
        if count >= 2:
            sorted_events = sorted(events, key=lambda x: x.timestamp)
            span_seconds = max(1.0, (sorted_events[-1].timestamp - sorted_events[0].timestamp).total_seconds())
            span_days = max(0.04, span_seconds / 86400.0)  # at least ~1 hr normalized window
            observed_rate = count / span_days
            ratio = observed_rate / max(0.5, base_rate)

            if ratio >= 6.0 and count >= 4:
                score = min(1.0, round(0.80 + (ratio - 6.0) * 0.03, 2))
                scores.append(score)
                indicators.append("FREQUENCY_SURGE")
            elif ratio >= 3.0 and count >= 3:
                score = min(0.80, round(0.55 + (ratio - 3.0) * 0.08, 2))
                scores.append(score)
                indicators.append("ELEVATED_EVENT_CADENCE")
            elif ratio >= 2.0 and count >= 3:
                score = min(0.55, round(0.35 + (ratio - 2.0) * 0.15, 2))
                scores.append(score)
                indicators.append("CADENCE_INCREASE")

            # High density burst: 5+ events in under 15 minutes (900 seconds)
            if count >= 5 and span_seconds <= 900.0:
                scores.append(0.85)
                indicators.append("HIGH_DENSITY_BURST")

        # 2. Activity collapse / silence when high baseline expected
        elif count == 1 and base_rate >= 20.0:
            scores.append(0.40)
            indicators.append("ABNORMAL_ACTIVITY_DROP")

        # 3. Aggregate dimensional score
        if not scores:
            final_score = 0.0
            explanation = "Event frequency aligns with historical operational baseline."
        else:
            final_score = min(1.0, round(max(scores), 2))
            explanation = (
                f"Frequency anomaly detected (score {final_score:.2f}) with indicators: "
                f"{', '.join(set(indicators))}."
            )

        confidence = 0.85
        if not baseline or baseline.baseline_status == "INSUFFICIENT_HISTORY":
            confidence = min(confidence, 0.55)

        unique_evidence = list(dict.fromkeys(evidence_ids))

        return DimensionScoreItem(
            dimension="frequency",
            score=final_score,
            confidence=round(confidence, 2),
            indicators=list(set(indicators)),
            explanation=explanation,
            evidence_event_ids=unique_evidence,
        )
