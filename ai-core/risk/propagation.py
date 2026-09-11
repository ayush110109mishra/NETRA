"""
Risk Propagation Engine for NETRA Phase 4 Risk Intelligence.
Simulates analytical risk propagation across entity network graphs,
shared operational clusters, and tactical relationships.
"""

from typing import Dict, List, Any, Optional
from models.entity_intelligence import CanonicalEntity


class RiskPropagator:
    """Propagates analytical risk along relational edges and co-occurrence clusters."""

    def __init__(self, damping_factor: float = 0.30):
        self.damping_factor = damping_factor

    def propagate_risk(
        self,
        target_entity: CanonicalEntity,
        base_risk_score: float,
        related_entities: List[CanonicalEntity],
        related_risks: Dict[str, float],
        relationship_weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate propagated indirect risk from connected high-risk entities.
        Returns propagated risk score and factor details.
        """
        if not related_entities or not related_risks:
            return {
                "base_risk": round(base_risk_score, 4),
                "propagated_risk": round(base_risk_score, 4),
                "delta": 0.0,
                "propagated_factors": [],
            }

        rel_weights = relationship_weights or {}
        indirect_deltas: List[float] = []
        factors: List[Dict[str, Any]] = []

        for peer in related_entities:
            peer_id = peer.entity_id
            peer_risk = related_risks.get(peer_id, 0.0)
            edge_weight = rel_weights.get(peer_id, 0.50)

            if peer_risk > 0.40:
                # Calculate indirect propagated influence
                influence = round(peer_risk * edge_weight * self.damping_factor, 4)
                indirect_deltas.append(influence)
                factors.append({
                    "source_entity_id": peer_id,
                    "source_risk": round(peer_risk, 4),
                    "relationship_weight": round(edge_weight, 4),
                    "influence": influence,
                })

        total_propagation = min(0.35, sum(indirect_deltas))
        effective_risk = min(1.0, round(base_risk_score + total_propagation, 4))

        return {
            "base_risk": round(base_risk_score, 4),
            "propagated_risk": effective_risk,
            "delta": round(effective_risk - base_risk_score, 4),
            "propagated_factors": factors,
        }
