"""
Probability Estimation Engine for NETRA Phase 6.
Constructs evidence-backed forecast probability from recurrence, trend strength,
persistence, evidence quality, fusion confidence, and model agreement.
"""

from typing import Dict, Optional, Tuple
import logging

from config import NetraConfig, default_config, PredictionWeights
from models.predictive_intelligence import TrendMetrics

logger = logging.getLogger("netra.prediction.probability")


class ProbabilityEstimator:
    """
    Computes explainable, deterministic forecast probability.
    Never fabricates ungrounded probabilities; ties estimates to concrete evidence signals.
    """

    def __init__(self, config: Optional[NetraConfig] = None):
        self.config = config or default_config
        self.weights: PredictionWeights = self.config.prediction_weights

    def estimate_probability(
        self,
        trend: TrendMetrics,
        evidence_quality: float = 0.80,
        fusion_confidence: float = 0.75,
        data_completeness: float = 0.90,
        model_agreement: float = 1.0,
        recurrence_factor: Optional[float] = None,
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculates normalized forecast probability and factor breakdown.
        """
        rec = recurrence_factor if recurrence_factor is not None else ((trend.persistence * 0.7) + (trend.strength * 0.3))
        rec = max(0.0, min(1.0, rec))

        w = self.weights
        prob = (
            (w.recurrence * rec)
            + (w.trend_strength * trend.strength)
            + (w.persistence * trend.persistence)
            + (w.evidence_quality * max(0.0, min(1.0, evidence_quality)))
            + (w.fusion_confidence * max(0.0, min(1.0, fusion_confidence)))
            + (w.data_completeness * max(0.0, min(1.0, data_completeness)))
            + (w.model_agreement * max(0.0, min(1.0, model_agreement)))
        )

        bounded_prob = round(max(0.0, min(1.0, prob)), 4)

        factors = {
            "recurrence": round(rec, 4),
            "trend_strength": round(trend.strength, 4),
            "persistence": round(trend.persistence, 4),
            "evidence_quality": round(evidence_quality, 4),
            "fusion_confidence": round(fusion_confidence, 4),
            "data_completeness": round(data_completeness, 4),
            "model_agreement": round(model_agreement, 4),
        }

        return bounded_prob, factors
