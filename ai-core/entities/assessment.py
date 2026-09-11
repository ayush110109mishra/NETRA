"""
Four-Tier Assessment Generator for NETRA Entity Intelligence.
Strictly separates statements into [OBSERVED], [INFERRED], [PREDICTED], and [UNCERTAIN]
to prevent epistemic boundary leaks in military intelligence analysis.
"""

from typing import List, Optional
from models.entity_intelligence import (
    CanonicalEntity,
    EntityProfile,
    EntityBehaviorProfile,
    BehavioralChangeReport,
    EntityAnomalyAssessment,
    EntityRiskProfile,
    EntityConfidenceProfile,
    EntityRelationshipEdge,
    EntityClusterMembership,
    FourTierAssessment,
)


class EntityAssessmentGenerator:
    """Generates rigorous four-tier operational intelligence assessment."""

    @staticmethod
    def generate(
        entity: CanonicalEntity,
        profile: EntityProfile,
        behavior: EntityBehaviorProfile,
        changes: BehavioralChangeReport,
        anomalies: EntityAnomalyAssessment,
        risk: EntityRiskProfile,
        confidence: EntityConfidenceProfile,
        relationships: List[EntityRelationshipEdge],
        clusters: List[EntityClusterMembership],
    ) -> FourTierAssessment:
        """Construct structured FourTierAssessment."""
        # 1. Summary
        summary = (
            f"Entity {entity.entity_id} ({entity.entity_type}, {entity.status.value}) evaluated across "
            f"{profile.unique_locations_count} operational location(s) with {profile.dominant_event_type} "
            f"as dominant activity. Assessed at {risk.level.value} risk ({risk.score:.2f}) with "
            f"{confidence.level} confidence ({confidence.score:.2f})."
        )

        # 2. [OBSERVED] Facts directly present in synthetic event logs
        observed: List[str] = [
            f"Recorded {entity.event_count} synthetic event(s) spanning {profile.active_duration_hours:.1f} operational hours.",
            f"Geographic centroid located at ({behavior.spatial.centroid.latitude:.4f}, {behavior.spatial.centroid.longitude:.4f}) with historical bounding radius of {behavior.spatial.bounding_radius_km:.1f} km.",
            f"Dominant synthetic operational taxonomy: {profile.dominant_event_type}.",
        ]
        if changes.detected:
            shift_features = [c.feature for c in changes.changes]
            observed.append(f"Recorded recent behavioral deviations across: {', '.join(shift_features)}.")
        if confidence.contradictions:
            observed.append(f"Recorded {len(confidence.contradictions)} telemetric contradiction(s) across reporting sensors.")

        # 3. [INFERRED] Model-derived analytical conclusions
        inferred: List[str] = [
            f"Behavioral baseline assessed as {behavior.baseline_status} (cadence: {behavior.event_frequency_per_day:.1f} events/day, mean velocity: {behavior.average_speed:.1f} km/h).",
            f"Anomaly index evaluated at {anomalies.score:.2f} ({anomalies.level}) based on {len(anomalies.indicators)} active indicator(s).",
            f"Risk profile assessed at {risk.score:.2f} ({risk.level.value}) with top contributing factor: {risk.factors[0].factor}.",
        ]
        if relationships:
            strongest = relationships[0]
            inferred.append(
                f"Relational graph connects to {len(relationships)} entity/entities; strongest link with {strongest.entity_id} ({strongest.relationship_type.value}, score: {strongest.score:.2f})."
            )
        if clusters:
            inferred.append(f"Participates in {len(clusters)} tactical activity cluster(s) with max cohesion {max(c.cohesion for c in clusters):.2f}.")

        # 4. [PREDICTED] Analytical projections based on models and periodicity
        predicted: List[str] = []
        if anomalies.level in ["CRITICAL", "HIGH"]:
            predicted.append("Kinematic divergence indicates elevated escalation potential if platform maintains current vector.")
        else:
            predicted.append(f"Anticipated to maintain operational posture within standard bounding radius ({behavior.spatial.bounding_radius_km:.1f} km).")

        expected_window_hours = max(0.5, round(behavior.temporal.average_inter_event_minutes / 60.0, 1))
        predicted.append(f"Next synthetic event contact window estimated within ~{expected_window_hours:.1f} hour(s) based on established cadence.")

        # 5. [UNCERTAIN] Explicit epistemic warnings, gaps, and non-causal guardrails
        uncertain: List[str] = [
            "Correlation indicates evidence-backed association but does NOT establish causal coordination or command hierarchy.",
            "All intelligence data is derived from synthetic simulation environments for algorithmic validation.",
        ]
        if behavior.baseline_status == "INSUFFICIENT_HISTORY":
            uncertain.append("Baseline history contains fewer than 3 events (Cold-Start condition); analytical projections carry reduced certainty.")
        if confidence.contradictions:
            uncertain.append("Sensor contradiction detected; telemetry inputs require independent cross-verification before mission action.")

        return FourTierAssessment(
            summary=summary,
            observed=observed,
            inferred=inferred,
            predicted=predicted,
            uncertain=uncertain,
        )
