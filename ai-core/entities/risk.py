"""
Entity Risk Engine for NETRA Entity Intelligence.
Computes multi-factor explainable risk scores for entities using weighted contributions
from event severity, behavioral deviations, anomaly ratings, and cluster context.
"""

from typing import List, Optional
from config import NetraConfig, default_config
from models.common import RiskLevel, SeverityLevel
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import (
    CanonicalEntity,
    BehavioralChangeReport,
    EntityAnomalyAssessment,
    EntityClusterMembership,
    EntityRiskFactor,
    EntityRiskProfile,
)


class EntityRiskEngine:
    """Computes explainable analytical risk for an entity."""

    def __init__(self, config: Optional[NetraConfig] = None):
        self.config = config or default_config
        self.weights = self.config.entity_risk_weights

    def compute_risk(
        self,
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        changes: BehavioralChangeReport,
        anomaly: EntityAnomalyAssessment,
        clusters: List[EntityClusterMembership],
    ) -> EntityRiskProfile:
        """Compute aggregate risk score and factor breakdown."""
        # 1. Event Severity Risk Component [0.0 - 1.0]
        if events:
            event_risks = [self._evaluate_event_risk(e) for e in events]
            event_risk_score = round(max(event_risks), 2)
        else:
            event_risk_score = 0.20

        # 2. Behavioral Deviation Component [0.0 - 1.0]
        behavioral_score = round(changes.score, 2)

        # 3. Anomaly Score Component [0.0 - 1.0]
        anomaly_score = round(anomaly.score, 2)

        # 4. Cluster Context Component [0.0 - 1.0]
        if clusters:
            max_cohesion = max(c.cohesion for c in clusters)
            cluster_score = round(min(1.0, 0.30 + 0.60 * max_cohesion), 2)
        else:
            cluster_score = 0.10

        # Weighted aggregate calculation
        raw_score = (
            event_risk_score * self.weights.event_risk
            + behavioral_score * self.weights.behavioral_deviation
            + anomaly_score * self.weights.anomaly_score
            + cluster_score * self.weights.cluster_context
        )
        final_score = round(min(1.0, max(0.0, raw_score)), 2)

        # Categorical Risk Level
        if final_score >= 0.75:
            level = RiskLevel.CRITICAL
        elif final_score >= 0.55:
            level = RiskLevel.HIGH
        elif final_score >= 0.35:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        # Explainable Factor Contributions
        factors = [
            EntityRiskFactor(
                factor="EVENT_SEVERITY_RISK",
                contribution=round(event_risk_score * self.weights.event_risk, 3),
                description=f"Direct event severity risk: {event_risk_score:.2f} across {len(events)} synthetic events",
            ),
            EntityRiskFactor(
                factor="BEHAVIORAL_DEVIATION",
                contribution=round(behavioral_score * self.weights.behavioral_deviation, 3),
                description=f"Behavioral shift score: {behavioral_score:.2f} ({len(changes.changes)} detected shifts)",
            ),
            EntityRiskFactor(
                factor="ANOMALY_INDEX",
                contribution=round(anomaly_score * self.weights.anomaly_score, 3),
                description=f"Synthetic anomaly rating: {anomaly_score:.2f} ({anomaly.level})",
            ),
            EntityRiskFactor(
                factor="CLUSTER_CONTEXT",
                contribution=round(cluster_score * self.weights.cluster_context, 3),
                description=f"Participation context across {len(clusters)} tactical cluster(s)",
            ),
        ]

        return EntityRiskProfile(
            score=final_score,
            level=level,
            factors=factors,
            risk_model_version="phase3-v1",
        )

    @staticmethod
    def _evaluate_event_risk(event: CanonicalEvent) -> float:
        """Estimate single event risk contribution."""
        # Check explicit priority hint or severity attribute
        sev = event.attributes.get("priority_hint") or event.attributes.get("severity")
        if sev:
            sev_str = str(sev).upper()
            if "CRITICAL" in sev_str:
                return 1.0
            if "HIGH" in sev_str:
                return 0.75
            if "MEDIUM" in sev_str:
                return 0.50
            if "LOW" in sev_str:
                return 0.25
            if "INFO" in sev_str:
                return 0.10

        # High risk event types
        high_risk_types = {"patrol_deviation", "airspace_violation", "hostile_lock", "sensor_spoofing"}
        if any(t in event.event_type.lower() for t in high_risk_types):
            return 0.80

        # Fallback to activity level
        act = float(event.attributes.get("activity_level", 0.3))
        return round(min(1.0, 0.20 + 0.60 * act), 2)
