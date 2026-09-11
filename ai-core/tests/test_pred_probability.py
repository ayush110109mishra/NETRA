"""
Unit tests for NETRA Phase 6 Probability Estimation.
Validates 7-factor linear formulation, strict weight summation to 1.0,
and probability bounds strictly in [0.0, 1.0].
"""

import pytest
from config import NetraConfig
from models.predictive_intelligence import TrendMetrics
from prediction.probability import ProbabilityEstimator


def test_probability_weights_sum_to_one():
    cfg = NetraConfig()
    w = cfg.prediction_weights
    total = (
        w.recurrence
        + w.trend_strength
        + w.persistence
        + w.evidence_quality
        + w.fusion_confidence
        + w.data_completeness
        + w.model_agreement
    )
    assert round(total, 6) == 1.0



def test_probability_estimation_bounds():
    estimator = ProbabilityEstimator()
    trend_high = TrendMetrics(slope=0.15, direction="RISING", strength=0.95, persistence=1.0, acceleration=0.0, volatility=0.02, is_regime_change=False)

    prob, components = estimator.estimate_probability(
        trend=trend_high,
        evidence_quality=0.95,
        fusion_confidence=0.92,
        data_completeness=1.0,
        model_agreement=1.0,
    )
    assert 0.0 <= prob <= 1.0
    assert prob > 0.80
    assert len(components) == 7

    # Inverted / weak conditions
    trend_low = TrendMetrics(slope=0.0, direction="VOLATILE", strength=0.1, persistence=0.2, acceleration=0.0, volatility=0.45, is_regime_change=True)
    prob_low, _ = estimator.estimate_probability(
        trend=trend_low,
        evidence_quality=0.20,
        fusion_confidence=0.30,
        data_completeness=0.40,
        model_agreement=0.33,
    )
    assert 0.0 <= prob_low <= 1.0
    assert prob_low < prob
