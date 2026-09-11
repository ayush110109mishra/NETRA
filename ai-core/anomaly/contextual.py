"""
Contextual Anomaly Detector for NETRA Phase 4 Anomaly Intelligence.
Evaluates entity behavior against sector environmental parameters, peer population norms,
threat alert conditions, and restricted operating domains.
"""

from typing import List, Dict, Optional, Any
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from models.anomaly_intelligence import DimensionScoreItem


class ContextualAnomalyDetector:
    """Detects contextual dissonance against sector background and operational status."""

    @staticmethod
    def detect(
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        baseline: Optional[EntityBehaviorProfile] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> DimensionScoreItem:
        """
        Evaluate contextual anomaly for entity observations.
        Returns DimensionScoreItem with normalized score [0.0 - 1.0].
        """
        if not events:
            return DimensionScoreItem(
                dimension="contextual",
                score=0.0,
                confidence=0.50,
                indicators=[],
                explanation="No recent events provided for contextual evaluation.",
                evidence_event_ids=[],
            )

        indicators: List[str] = []
        evidence_ids: List[str] = []
        scores: List[float] = []

        if not context:
            return DimensionScoreItem(
                dimension="contextual",
                score=0.0,
                confidence=0.70,
                indicators=[],
                explanation="No environmental or sector context provided; nominal context assumed.",
                evidence_event_ids=[],
            )

        # 1. Sector Calm vs Entity Hyperactivity
        sector_activity = context.get("sector_average_activity")
        if sector_activity is not None:
            # Check entity's current activity level
            entity_acts = [
                float(e.attributes.get("activity_level", 0.5))
                for e in events
                if "activity_level" in e.attributes
            ]
            if entity_acts:
                avg_act = sum(entity_acts) / len(entity_acts)
                if sector_activity < 0.20 and avg_act > 0.70:
                    scores.append(0.80)
                    indicators.append("ISOLATED_ACTIVITY_IN_CALM_SECTOR")
                    evidence_ids.extend([e.event_id for e in events])

        # 2. Sector Exclusion / Restricted Operations Zone
        is_restricted = context.get("restricted_zone_active", False)
        if is_restricted:
            scores.append(0.85)
            indicators.append("ACTIVE_RESTRICTED_ZONE_PRESENCE")
            evidence_ids.extend([e.event_id for e in events])

        # 3. Severe Weather / Terrain Constraint Breach
        environmental_hazard = context.get("environmental_hazard")
        if environmental_hazard:
            scores.append(0.70)
            indicators.append(f"HAZARDOUS_CONDITIONS_OPERATION_{str(environmental_hazard).upper()}")
            evidence_ids.extend([e.event_id for e in events])

        # 4. Sector Threat Posture Incongruity
        sector_threat = str(context.get("sector_threat_level", "")).upper()
        if sector_threat == "CRITICAL":
            scores.append(0.65)
            indicators.append("HIGH_THREAT_SECTOR_EXPOSURE")

        # 5. Aggregate dimensional score
        if not scores:
            final_score = 0.0
            explanation = "Entity behavior is consistent with sector background and contextual environment."
        else:
            final_score = min(1.0, round(max(scores), 2))
            explanation = (
                f"Contextual anomaly detected (score {final_score:.2f}) with indicators: "
                f"{', '.join(set(indicators))}."
            )

        confidence = 0.85 if context else 0.50
        unique_evidence = list(dict.fromkeys(evidence_ids))

        return DimensionScoreItem(
            dimension="contextual",
            score=final_score,
            confidence=round(confidence, 2),
            indicators=list(set(indicators)),
            explanation=explanation,
            evidence_event_ids=unique_evidence,
        )
