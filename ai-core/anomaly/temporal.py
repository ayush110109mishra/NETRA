"""
Temporal Anomaly Detector for NETRA Phase 4 Anomaly Intelligence.
Analyzes event timestamp patterns against entity operational baselines,
detecting unexpected operational hours, off-schedule bursts, and inter-event gap anomalies.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from models.anomaly_intelligence import DimensionScoreItem


class TemporalAnomalyDetector:
    """Detects temporal deviations, off-hour activity, and temporal bursts."""

    @staticmethod
    def detect(
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        baseline: Optional[EntityBehaviorProfile] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> DimensionScoreItem:
        """
        Evaluate temporal anomaly for entity observations.
        Returns DimensionScoreItem with normalized score [0.0 - 1.0].
        """
        if not events:
            return DimensionScoreItem(
                dimension="temporal",
                score=0.0,
                confidence=0.50,
                indicators=[],
                explanation="No recent events provided for temporal evaluation.",
                evidence_event_ids=[],
            )

        indicators: List[str] = []
        evidence_ids: List[str] = []
        scores: List[float] = []

        # 1. Hour of Day Deviation vs Baseline Distribution
        if baseline and baseline.temporal and baseline.temporal.hourly_distribution:
            dist = baseline.temporal.hourly_distribution
            total_historical = sum(dist.values())

            if total_historical >= 3:
                off_hour_events: List[CanonicalEvent] = []
                for e in events:
                    hour_key = e.timestamp.hour
                    # Support both int and str keys in dict
                    hist_count = dist.get(hour_key, dist.get(str(hour_key), 0))
                    prob = hist_count / float(total_historical)
                    
                    if prob < 0.03:
                        off_hour_events.append(e)

                if off_hour_events:
                    off_ratio = len(off_hour_events) / float(len(events))
                    # Score scales with proportion of off-schedule events
                    hour_dev_score = min(1.0, round(0.40 + (off_ratio * 0.50), 2))
                    scores.append(hour_dev_score)
                    indicators.append("UNEXPECTED_OPERATIONAL_HOURS")
                    evidence_ids.extend([e.event_id for e in off_hour_events])

        # 2. Inter-Event Gap & Temporal Burst Detection
        if len(events) >= 3:
            sorted_events = sorted(events, key=lambda x: x.timestamp)
            gaps_seconds = [
                (sorted_events[i + 1].timestamp - sorted_events[i].timestamp).total_seconds()
                for i in range(len(sorted_events) - 1)
            ]

            # Burst: 3+ events within 5 minutes (300 seconds)
            min_gap = min(gaps_seconds)
            total_span = (sorted_events[-1].timestamp - sorted_events[0].timestamp).total_seconds()
            
            if total_span <= 300.0 and len(events) >= 3:
                burst_score = 0.85
                scores.append(burst_score)
                indicators.append("TEMPORAL_BURST")
                evidence_ids.extend([e.event_id for e in sorted_events])
            elif min_gap < 60.0:
                burst_score = 0.70
                scores.append(burst_score)
                indicators.append("RAPID_INTERVAL_CADENCE")
                evidence_ids.extend([e.event_id for e in sorted_events[:2]])

        # 3. Aggregate dimensional score
        if not scores:
            final_score = 0.0
            explanation = "Temporal distribution matches expected operational baseline."
        else:
            final_score = min(1.0, round(max(scores), 2))
            explanation = (
                f"Temporal anomaly detected (score {final_score:.2f}) with indicators: "
                f"{', '.join(indicators)}."
            )

        # Confidence: higher with more events and sufficient baseline history
        confidence = 0.85
        if not baseline or baseline.baseline_status == "INSUFFICIENT_HISTORY":
            confidence = min(confidence, 0.45)
        if len(events) < 3:
            confidence = min(confidence, 0.60)

        # Deduplicate evidence event IDs preserving order
        unique_evidence = list(dict.fromkeys(evidence_ids))

        return DimensionScoreItem(
            dimension="temporal",
            score=final_score,
            confidence=round(confidence, 2),
            indicators=indicators,
            explanation=explanation,
            evidence_event_ids=unique_evidence,
        )
