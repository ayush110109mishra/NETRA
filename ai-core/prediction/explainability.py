"""
Prediction Explainability Engine for NETRA Phase 6.
Generates structured narrative justifications, lists supporting and limiting factors,
defines invalidation conditions, and maintains 5-tier epistemic ledgers.
"""

from typing import Any, Dict, List, Optional, Tuple
import logging

from models.predictive_intelligence import (
    FeatureItem,
    ForecastHorizon,
    PredictiveAssessment,
    PredictionExplanation,
    PredictiveForecast,
    PredictiveTarget,
    TrendMetrics,
)

logger = logging.getLogger("netra.prediction.explainability")


class PredictionExplainer:
    """
    Constructs explainability dossiers answering: Why?, What supports it?,
    What weakens it?, and What invalidates it?
    """

    @classmethod
    def explain_forecast(
        cls,
        forecast: PredictiveForecast,
        trend: TrendMetrics,
        features: List[FeatureItem],
        observed_events_count: int,
        conflicts_count: int = 0,
    ) -> Tuple[PredictionExplanation, PredictiveAssessment]:
        """
        Builds PredictionExplanation and five-tier PredictiveAssessment.
        """
        target_name = forecast.target.value
        f_state = forecast.forecast_state
        horizon_name = forecast.horizon.value.lower()

        # 1. Narrative Assessment
        narrative = (
            f"Analytical forecast indicates {target_name} is projected as '{f_state}' "
            f"over the {horizon_name} horizon (probability={forecast.probability:.2f}, "
            f"confidence={forecast.confidence:.2f}, uncertainty={forecast.uncertainty:.2f})."
        )

        # 2. Supporting Factors
        supporting: List[str] = []
        if trend.strength >= 0.50:
            supporting.append(f"Strong directional momentum (slope={trend.slope:+.3f}, strength={trend.strength:.2f})")
        if trend.persistence >= 0.70:
            supporting.append(f"High trend consistency ({trend.persistence:.0%} concordant steps)")
        if forecast.model_agreement >= 0.85:
            supporting.append("Unanimous agreement across candidate forecasting strategies")

        for feat in features:
            if feat.feature_name == "fusion_independent_sources" and feat.value >= 2:
                supporting.append(f"Multi-source independent sensor corroboration ({int(feat.value)} sources)")
            elif feat.feature_name == "anomaly_persistence_factor" and feat.value >= 0.80:
                supporting.append("Historical anomaly persistence confirming operational deviation")

        if not supporting:
            supporting.append("Telemetry continuation consistent with historical inertia")

        # 3. Limiting Factors
        limiting: List[str] = []
        if forecast.data_sufficiency.value == "INSUFFICIENT":
            limiting.append("Cold-start data gating: fewer than 3 historical observations available")
        elif forecast.data_sufficiency.value == "LIMITED":
            limiting.append("Limited sample depth (3-5 observations) dampening certainty")

        if trend.volatility >= 0.25:
            limiting.append(f"Elevated metric volatility ({trend.volatility:.2f}) introduces trajectory jitter")

        if trend.is_regime_change:
            limiting.append("Detected operational regime shift: recent trajectory diverges from baseline")

        if conflicts_count > 0:
            limiting.append(f"Inter-source contradiction present ({conflicts_count} active conflict records)")

        if forecast.model_agreement < 0.70:
            limiting.append("Ensemble strategy divergence between trend extrapolation and inertia baseline")

        # 4. Invalidation Conditions
        invalidation: List[str] = [
            f"Abrupt metric inversion exceeding delta 0.25 within next observation cycle",
            f"Prolonged sensor dropout or missing telemetry beyond {horizon_name} horizon",
            f"Introduction of uncorroborated single-sensor conflict contradicting {f_state} trajectory",
        ]

        # 5. Feature Importance
        feat_importance: Dict[str, float] = {}
        for feat in features:
            feat_importance[feat.feature_name] = round(feat.normalized_value, 4)

        explanation = PredictionExplanation(
            assessment=narrative,
            supporting_factors=supporting,
            limiting_factors=limiting,
            invalidation_conditions=invalidation,
            feature_importance=feat_importance,
        )

        # 6. Epistemic Five-Tier Assessment
        observed_items = [
            f"Processed {observed_events_count} chronological event observation(s) across target entity."
        ]
        fused_items = [
            f"Corroborated evidence synthesized with model agreement factor {forecast.model_agreement:.2f}."
        ]
        inferred_items = [
            f"Trend trajectory identified as {trend.direction} (slope={trend.slope:+.3f}, persistence={trend.persistence:.2f})."
        ]
        if trend.is_regime_change:
            inferred_items.append("Regime change detected: operational behavior breaking prior baseline.")

        predicted_items = [
            f"Forecast [{target_name}]: {f_state} over {horizon_name} horizon with probability {forecast.probability:.2f} (interval [{forecast.interval.lower:.2f} - {forecast.interval.upper:.2f}])."
        ]
        uncertain_items = limiting

        epistemic_ledger = {
            "OBSERVED": observed_items,
            "FUSED": fused_items,
            "INFERRED": inferred_items,
            "PREDICTED": predicted_items,
            "UNCERTAIN": uncertain_items,
        }

        assessment = PredictiveAssessment(
            summary=narrative,
            observed=observed_items,
            fused=fused_items,
            inferred=inferred_items,
            predicted=predicted_items,
            uncertain=uncertain_items,
            epistemic_ledger=epistemic_ledger,
        )

        return explanation, assessment
