"""
Uncertainty Estimation Engine for NETRA Phase 6.
Quantifies forecast uncertainty and constructs heuristic confidence intervals
accounting for sparse history, volatility, sensor contradictions, and regime shifts.
"""

from typing import Tuple, Optional
import logging

from config import NetraConfig, default_config, PredictionGatingConfig
from models.predictive_intelligence import ForecastInterval, TrendMetrics

logger = logging.getLogger("netra.prediction.uncertainty")


class UncertaintyEstimator:
    """
    Evaluates residual predictive uncertainty.
    Ensures that volatile, conflicting, or sparse evidence transparently widens error bounds.
    """

    def __init__(self, config: Optional[NetraConfig] = None):
        self.config = config or default_config
        self.gating: PredictionGatingConfig = self.config.prediction_gating

    def estimate_uncertainty(
        self,
        sample_count: int,
        trend: TrendMetrics,
        probability: float,
        fusion_conflict_severity: float = 0.0,
        model_agreement: float = 1.0,
        is_cold_start: bool = False,
    ) -> Tuple[float, ForecastInterval]:
        """
        Calculates normalized uncertainty factor [0.0 - 1.0] and bounds.
        """
        # Base uncertainty
        base_unc = 0.15

        # 1. History Sufficiency Penalty
        if is_cold_start or sample_count < self.gating.cold_start_threshold:
            history_penalty = 0.70
        elif sample_count <= self.gating.limited_history_threshold:
            history_penalty = 0.30

        else:
            history_penalty = max(0.0, 0.15 - (0.01 * min(15, sample_count)))

        # 2. Volatility Penalty
        vol_penalty = min(0.30, trend.volatility * 0.6)

        # 3. Source Conflict Penalty
        conflict_penalty = min(0.25, fusion_conflict_severity * 0.30)

        # 4. Regime Change Penalty
        regime_penalty = 0.20 if trend.is_regime_change else 0.0

        # 5. Model Disagreement Penalty
        agreement_penalty = max(0.0, 0.20 * (1.0 - model_agreement))

        total_unc = (
            base_unc
            + history_penalty
            + vol_penalty
            + conflict_penalty
            + regime_penalty
            + agreement_penalty
        )
        bounded_unc = round(max(0.05, min(0.95, total_unc)), 4)

        # Calculate heuristic confidence interval around probability
        half_width = bounded_unc * 0.40
        lower = round(max(0.0, probability - half_width), 4)
        upper = round(min(1.0, probability + half_width), 4)

        interval = ForecastInterval(
            lower=lower,
            upper=upper,
            interval_type="heuristic",
        )

        return bounded_unc, interval
