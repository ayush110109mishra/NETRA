"""
Entity Anomaly Engine for NETRA Entity Intelligence.
Synthesizes kinematic surges, spatial boundary breaches, novel behavior profiles,
and telemetry abnormalities into an explainable entity-level anomaly assessment.
"""

from typing import List, Optional
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import (
    CanonicalEntity,
    EntityBehaviorProfile,
    BehavioralChangeReport,
    EntityAnomalyIndicator,
    EntityAnomalyAssessment,
)


class EntityAnomalyEngine:
    """Computes entity-level anomaly rating and explains contributing indicators."""

    @staticmethod
    def assess_anomaly(
        entity: CanonicalEntity,
        baseline: EntityBehaviorProfile,
        changes: BehavioralChangeReport,
        recent_events: List[CanonicalEvent],
    ) -> EntityAnomalyAssessment:
        """Evaluate multi-indicator anomaly for the entity."""
        indicators: List[EntityAnomalyIndicator] = []

        # 1. Translate detected behavioral changes into anomaly indicators
        if changes.detected:
            for c in changes.changes:
                if c.feature == "speed":
                    ind_name = "SPEED_SURGE" if c.direction == "INCREASE" else "SPEED_ANOMALY"
                    ind_score = min(1.0, round(max(0.35, c.magnitude * 0.45), 2))
                elif c.feature == "spatial_expansion":
                    ind_name = "SPATIAL_EXPANSION"
                    ind_score = min(1.0, round(max(0.40, c.magnitude * 0.50), 2))
                elif c.feature == "event_type":
                    ind_name = "UNUSUAL_EVENT_TYPE"
                    ind_score = 0.65
                elif c.feature == "frequency":
                    ind_name = "FREQUENCY_SPIKE" if c.direction == "INCREASE" else "TEMPO_DROP"
                    ind_score = min(1.0, round(max(0.30, c.magnitude * 0.40), 2))
                else:
                    ind_name = f"BEHAVIORAL_{c.feature.upper()}"
                    ind_score = 0.40

                indicators.append(
                    EntityAnomalyIndicator(
                        indicator=ind_name,
                        score=ind_score,
                        description=c.description,
                        evidence_event_ids=c.evidence_event_ids,
                    )
                )

        # 2. Check for absolute severe telemetry thresholds in recent observations
        for e in recent_events:
            act_level = float(e.attributes.get("activity_level", 0.0))
            if act_level >= 0.85:
                # Avoid duplicate indicators
                if not any(ind.indicator == "HIGH_ACTIVITY_TELEMETRY" for ind in indicators):
                    indicators.append(
                        EntityAnomalyIndicator(
                            indicator="HIGH_ACTIVITY_TELEMETRY",
                            score=round(act_level, 2),
                            description=f"Direct sensor telemetry recorded elevated activity level ({act_level:.2f})",
                            evidence_event_ids=[e.event_id],
                        )
                    )

            speed = float(e.attributes.get("speed", 0.0))
            # Ground platform over-speed check
            if entity.entity_type.upper() in ["VEHICLE", "PATROL_UNIT"] and speed > 110.0:
                if not any(ind.indicator == "GROUND_SPEED_EXCESS" for ind in indicators):
                    indicators.append(
                        EntityAnomalyIndicator(
                            indicator="GROUND_SPEED_EXCESS",
                            score=0.85,
                            description=f"Ground unit operating at kinematic extreme ({speed:.1f} km/h)",
                            evidence_event_ids=[e.event_id],
                        )
                    )

        # 3. Overall anomaly score and category
        if not indicators:
            score = 0.05
            level = "LOW"
        else:
            # Deterministic aggregation: highest indicator score reinforced by overall changes
            max_ind = max(ind.score for ind in indicators)
            blended = max(max_ind, changes.score * 0.85)
            score = min(1.0, round(blended, 2))

            if score >= 0.80:
                level = "CRITICAL"
            elif score >= 0.60:
                level = "HIGH"
            elif score >= 0.30:
                level = "MEDIUM"
            else:
                level = "LOW"

        return EntityAnomalyAssessment(
            score=score,
            level=level,
            indicators=indicators,
        )
