"""
Anomaly Attribution Engine for NETRA Phase 4 Anomaly Intelligence.
Provides explainable mathematical attribution of anomaly drivers,
ranking dimensions by exact mathematical contribution (score * weight).
"""

from typing import Dict, List, Optional
from config import AnomalyDimensionWeights, default_config
from models.anomaly_intelligence import (
    DimensionScoreItem,
    AnomalyAttributionFactor,
    AnomalyAttribution,
)


class AnomalyAttributor:
    """Computes mathematically consistent factor attribution for detected anomalies."""

    def __init__(self, weights: Optional[AnomalyDimensionWeights] = None):
        self.weights = weights or default_config.anomaly_weights

    def attribute(
        self,
        dimension_scores: Dict[str, DimensionScoreItem],
    ) -> AnomalyAttribution:
        """
        Calculates mathematical contribution for all dimensions,
        identifies the primary driver, and ranks top contributing factors.
        """
        w_map = {
            "temporal": self.weights.temporal,
            "spatial": self.weights.spatial,
            "kinematic": self.weights.kinematic,
            "frequency": self.weights.frequency,
            "event_type": self.weights.event_type,
            "behavioral": self.weights.behavioral,
            "relational": self.weights.relational,
            "contextual": self.weights.contextual,
        }

        factors: List[AnomalyAttributionFactor] = []

        for dim, weight in w_map.items():
            item = dimension_scores.get(dim)
            raw_score = item.score if item else 0.0
            contribution = round(raw_score * weight, 4)
            description = (
                item.explanation
                if (item and item.explanation)
                else f"Nominal {dim} behavior."
            )

            factors.append(
                AnomalyAttributionFactor(
                    factor=dim,
                    score=raw_score,
                    weight=weight,
                    contribution=contribution,
                    description=description,
                )
            )

        # Sort descending by contribution, then by raw score
        factors.sort(key=lambda x: (x.contribution, x.score), reverse=True)

        primary_dim = factors[0].factor if factors else "none"

        return AnomalyAttribution(
            primary_dimension=primary_dim,
            top_factors=factors,
        )
