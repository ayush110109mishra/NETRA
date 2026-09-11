"""
Unit tests for NETRA Phase 6 Uncertainty and Interval Estimation.
Validates residual uncertainty calculation, cold start capping, volatility penalty,
conflict penalties, and confidence interval bounds containment.
"""

import pytest
from models.predictive_intelligence import TrendMetrics
from prediction.uncertainty import UncertaintyEstimator


def test_uncertainty_cold_start():
    est = UncertaintyEstimator()
    trend = TrendMetrics(slope=0.0, direction="STABLE", strength=0.0, persistence=1.0, acceleration=0.0, volatility=0.0, is_regime_change=False)

    unc, interval = est.estimate_uncertainty(
        sample_count=2,
        trend=trend,
        probability=0.50,
        is_cold_start=True,
    )
    assert unc >= 0.85
    assert 0.0 <= interval.lower <= interval.upper <= 1.0
    assert interval.interval_type == "heuristic"


def test_uncertainty_sample_depth_and_stability():
    est = UncertaintyEstimator()
    trend_stable = TrendMetrics(slope=0.01, direction="STABLE", strength=0.1, persistence=0.95, acceleration=0.0, volatility=0.02, is_regime_change=False)

    unc_high_sample, int_high = est.estimate_uncertainty(
        sample_count=25,
        trend=trend_stable,
        probability=0.75,
        fusion_conflict_severity=0.0,
        model_agreement=1.0,
    )

    unc_low_sample, int_low = est.estimate_uncertainty(
        sample_count=4,
        trend=trend_stable,
        probability=0.75,
        fusion_conflict_severity=0.0,
        model_agreement=1.0,
    )

    assert unc_high_sample < unc_low_sample
    assert (int_high.upper - int_high.lower) < (int_low.upper - int_low.lower)


def test_uncertainty_sensor_conflict_penalty():
    est = UncertaintyEstimator()
    trend = TrendMetrics(slope=0.0, direction="STABLE", strength=0.1, persistence=0.9, acceleration=0.0, volatility=0.05, is_regime_change=False)

    unc_no_conflict, _ = est.estimate_uncertainty(sample_count=10, trend=trend, probability=0.6, fusion_conflict_severity=0.0)
    unc_conflict, _ = est.estimate_uncertainty(sample_count=10, trend=trend, probability=0.6, fusion_conflict_severity=0.8)

    assert unc_conflict > unc_no_conflict
