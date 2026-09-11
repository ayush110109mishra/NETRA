"""
Unit tests for NETRA Phase 6 Prediction Explainability Engine.
Validates generation of narrative assessments, supporting and limiting factor lists,
invalidation conditions, and the 5-tier epistemic ledger.
"""

import pytest
from models.predictive_intelligence import (
    DataSufficiency,
    FeatureItem,
    ForecastHorizon,
    ForecastInterval,
    ForecastLifecycleState,
    PredictiveForecast,
    PredictiveTarget,
    TrendMetrics,
)
from prediction.explainability import PredictionExplainer


def test_explainability_dossier_and_five_tier_assessment():
    forecast = PredictiveForecast(
        target=PredictiveTarget.ACTIVITY_STATE,
        current_state="NOMINAL",
        forecast_state="INCREASING",
        horizon=ForecastHorizon.SHORT,
        probability=0.82,
        confidence=0.85,
        uncertainty=0.18,
        interval=ForecastInterval(lower=0.74, upper=0.90, interval_type="heuristic"),
        model_agreement=1.0,
        strategy_used="TrendForecastStrategy",
        data_sufficiency=DataSufficiency.SUFFICIENT,
        lifecycle_state=ForecastLifecycleState.ACTIVE,
    )

    trend = TrendMetrics(
        slope=0.12,
        direction="RISING",
        strength=0.88,
        persistence=1.0,
        acceleration=0.0,
        volatility=0.04,
        is_regime_change=False,
    )

    features = [
        FeatureItem(
            feature_name="temporal_event_frequency",
            value=6.0,
            normalized_value=0.6,
            derived_from=["E1", "E2"],
            source_evidence=["S1"],
        ),
        FeatureItem(
            feature_name="fusion_independent_sources",
            value=3.0,
            normalized_value=0.75,
            derived_from=["E1"],
            source_evidence=["S1", "S2", "S3"],
        ),
    ]

    explanation, assessment = PredictionExplainer.explain_forecast(
        forecast=forecast,
        trend=trend,
        features=features,
        observed_events_count=8,
        conflicts_count=0,
    )

    # Validate explanation structure
    assert "INCREASING" in explanation.assessment
    assert len(explanation.supporting_factors) > 0
    assert len(explanation.invalidation_conditions) > 0
    assert "temporal_event_frequency" in explanation.feature_importance

    # Validate 5-tier epistemic ledger
    ledger = assessment.epistemic_ledger
    assert "OBSERVED" in ledger
    assert "FUSED" in ledger
    assert "INFERRED" in ledger
    assert "PREDICTED" in ledger
    assert "UNCERTAIN" in ledger

    assert len(assessment.observed) > 0
    assert len(assessment.predicted) > 0
