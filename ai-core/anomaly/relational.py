"""
Relational Anomaly Detector for NETRA Phase 4 Anomaly Intelligence.
Analyzes network topology changes, unexpected co-occurrences, new cluster affiliations,
and association with high-risk entities.
"""

from typing import List, Dict, Optional, Any
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from models.anomaly_intelligence import DimensionScoreItem


class RelationalAnomalyDetector:
    """Detects relational deviations, rendezvous, new clusterings, and network shifts."""

    @staticmethod
    def detect(
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        baseline: Optional[EntityBehaviorProfile] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> DimensionScoreItem:
        """
        Evaluate relational anomaly for entity observations.
        Returns DimensionScoreItem with normalized score [0.0 - 1.0].
        """
        if not events:
            return DimensionScoreItem(
                dimension="relational",
                score=0.0,
                confidence=0.50,
                indicators=[],
                explanation="No recent events provided for relational evaluation.",
                evidence_event_ids=[],
            )

        indicators: List[str] = []
        evidence_ids: List[str] = []
        scores: List[float] = []

        known_network = set(
            getattr(entity, "associated_entity_ids", None)
            or entity.attributes.get("associated_entity_ids", [])
        )

        # 1. New associations observed in current events
        observed_peers: set = set()
        for e in events:
            # Check target entity
            target = e.attributes.get("target_entity_id")
            if target and target != entity.entity_id:
                observed_peers.add(target)
                if target not in known_network:
                    evidence_ids.append(e.event_id)

            # Check co-observed entities list
            co_entities = e.attributes.get("co_observed_entities", [])
            if isinstance(co_entities, list):
                for ce in co_entities:
                    if ce != entity.entity_id:
                        observed_peers.add(ce)
                        if ce not in known_network:
                            evidence_ids.append(e.event_id)

            # Check cluster affiliation
            cluster_id = e.attributes.get("cluster_id")
            if cluster_id:
                indicators.append("NEW_CLUSTER_AFFILIATION")
                scores.append(0.55)
                evidence_ids.append(e.event_id)

        # Association Surge (rendezvous with 3+ new entities)
        new_peers = observed_peers - known_network
        if len(new_peers) >= 3:
            scores.append(0.80)
            indicators.append("ASSOCIATION_SURGE_RENDEZVOUS")
        elif len(new_peers) >= 1:
            scores.append(0.50)
            indicators.append("NEW_UNTRACKED_PEER_ASSOCIATION")

        # 2. Check association with high-risk peers via context
        if context and "high_risk_entities" in context:
            high_risk_pool = set(context["high_risk_entities"])
            intersecting_high_risk = observed_peers.intersection(high_risk_pool)
            if intersecting_high_risk:
                scores.append(0.85)
                indicators.append("HIGH_RISK_PEER_CORRELATION")

        # 3. Aggregate dimensional score
        if not scores:
            final_score = 0.0
            explanation = "Relational topology aligns with established baseline network."
        else:
            final_score = min(1.0, round(max(scores), 2))
            explanation = (
                f"Relational anomaly detected (score {final_score:.2f}) with indicators: "
                f"{', '.join(set(indicators))}."
            )

        confidence = 0.85
        if not known_network:
            confidence = 0.60

        unique_evidence = list(dict.fromkeys(evidence_ids))

        return DimensionScoreItem(
            dimension="relational",
            score=final_score,
            confidence=round(confidence, 2),
            indicators=list(set(indicators)),
            explanation=explanation,
            evidence_event_ids=unique_evidence,
        )
