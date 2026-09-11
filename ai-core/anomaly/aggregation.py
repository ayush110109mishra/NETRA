"""
Multi-Dimensional Anomaly Aggregator for NETRA Phase 4 Anomaly Intelligence.
Combines 8 analytical dimensions into an explainable aggregate anomaly score,
applies controlled cross-dimensional synergy, and maps to categorical anomaly levels.
"""

from typing import Dict, Tuple, Optional
from config import (
    AnomalyDimensionWeights,
    AnomalyClassificationThresholds,
    default_config,
)
from models.anomaly_intelligence import (
    AnomalyLevel,
    DimensionScoreItem,
    MultiDimensionalScores,
)


class AnomalyAggregator:
    """Combines 8-dimensional scores into a calibrated overall score."""

    def __init__(
        self,
        weights: Optional[AnomalyDimensionWeights] = None,
        thresholds: Optional[AnomalyClassificationThresholds] = None,
    ):
        self.weights = weights or default_config.anomaly_weights
        self.thresholds = thresholds or default_config.anomaly_thresholds

    def aggregate(
        self,
        dimension_scores: Dict[str, DimensionScoreItem],
    ) -> Tuple[float, AnomalyLevel, MultiDimensionalScores]:
        """
        Aggregate dimensional scores using deterministic weights and synergy.
        Returns (aggregate_score, categorical_level, multi_dim_scores_vector).
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

        dim_scores = MultiDimensionalScores(
            temporal=dimension_scores.get("temporal", DimensionScoreItem(dimension="temporal", score=0.0, explanation="")).score,
            spatial=dimension_scores.get("spatial", DimensionScoreItem(dimension="spatial", score=0.0, explanation="")).score,
            kinematic=dimension_scores.get("kinematic", DimensionScoreItem(dimension="kinematic", score=0.0, explanation="")).score,
            frequency=dimension_scores.get("frequency", DimensionScoreItem(dimension="frequency", score=0.0, explanation="")).score,
            event_type=dimension_scores.get("event_type", DimensionScoreItem(dimension="event_type", score=0.0, explanation="")).score,
            behavioral=dimension_scores.get("behavioral", DimensionScoreItem(dimension="behavioral", score=0.0, explanation="")).score,
            relational=dimension_scores.get("relational", DimensionScoreItem(dimension="relational", score=0.0, explanation="")).score,
            contextual=dimension_scores.get("contextual", DimensionScoreItem(dimension="contextual", score=0.0, explanation="")).score,
        )

        # 1. Linear weighted base combination
        raw_weighted = (
            dim_scores.temporal * w_map["temporal"]
            + dim_scores.spatial * w_map["spatial"]
            + dim_scores.kinematic * w_map["kinematic"]
            + dim_scores.frequency * w_map["frequency"]
            + dim_scores.event_type * w_map["event_type"]
            + dim_scores.behavioral * w_map["behavioral"]
            + dim_scores.relational * w_map["relational"]
            + dim_scores.contextual * w_map["contextual"]
        )

        # 2. Multi-dimensional synergy adjustment
        # If 3 or more independent dimensions show elevated anomalies (>= 0.50),
        # apply bounded synergy bonus
        elevated_count = sum(
            1
            for s in [
                dim_scores.temporal,
                dim_scores.spatial,
                dim_scores.kinematic,
                dim_scores.frequency,
                dim_scores.event_type,
                dim_scores.behavioral,
                dim_scores.relational,
                dim_scores.contextual,
            ]
            if s >= 0.50
        )

        synergy = 0.0
        if elevated_count >= 3:
            synergy = min(0.15, 0.04 * (elevated_count - 2))

        final_score = min(1.0, round(raw_weighted + synergy, 4))

        # 3. Categorical classification
        if final_score <= self.thresholds.nominal_max:
            level = AnomalyLevel.NOMINAL
        elif final_score <= self.thresholds.low_max:
            level = AnomalyLevel.LOW
        elif final_score <= self.thresholds.moderate_max:
            level = AnomalyLevel.MODERATE
        elif final_score <= self.thresholds.high_max:
            level = AnomalyLevel.HIGH
        else:
            level = AnomalyLevel.CRITICAL

        return final_score, level, dim_scores
