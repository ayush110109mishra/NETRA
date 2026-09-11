"""
Model Agreement and Forecast Calibration Engine for NETRA Phase 6.
Evaluates multi-strategy consensus, tracks synthetic forecast accuracy,
and measures directional fidelity.
"""

from typing import Dict, List, Optional, Tuple
import logging

from models.predictive_intelligence import (
    ForecastEvaluationItem,
    ForecastEvaluationResponse,
)

logger = logging.getLogger("netra.prediction.calibration")


class ModelCalibrator:
    """
    Measures ensemble agreement across candidate strategies and logs
    synthetic forecast validation metrics (MAE and directional accuracy).
    """

    _evaluation_records: List[ForecastEvaluationItem] = []

    @classmethod
    def calculate_model_agreement(cls, candidate_forecasts: Dict[str, str]) -> float:
        """
        Measures agreement ratio across candidate strategies.
        If all agree -> 1.0, majority -> 0.70, all diverge -> 0.35.
        """
        if not candidate_forecasts:
            return 1.0

        states = list(candidate_forecasts.values())
        if len(states) <= 1:
            return 1.0

        from collections import Counter
        counts = Counter(states)
        most_common_count = counts.most_common(1)[0][1]

        if most_common_count == len(states):
            return 1.0
        elif most_common_count >= 2:
            return 0.70
        else:
            return 0.35

    @classmethod
    def record_evaluation(
        cls,
        prediction_id: str,
        target: str,
        forecast_state: str,
        actual_state: str,
        absolute_error: float = 0.0,
    ) -> ForecastEvaluationItem:
        """Logs comparison between synthetic forecast and observed synthetic outcome."""
        # Check directional correctness
        is_dir_correct = (
            forecast_state == actual_state
            or (forecast_state in ("INCREASING", "RISING", "ESCALATING") and actual_state in ("INCREASING", "RISING", "ESCALATING"))
            or (forecast_state in ("DECREASING", "FALLING", "RESOLVING") and actual_state in ("DECREASING", "FALLING", "RESOLVING"))
            or (forecast_state in ("STABLE", "NORMAL") and actual_state in ("STABLE", "NORMAL"))
        )

        item = ForecastEvaluationItem(
            prediction_id=prediction_id,
            target=target,
            forecast_state=forecast_state,
            actual_state=actual_state,
            is_directionally_correct=is_dir_correct,
            absolute_error=round(max(0.0, absolute_error), 4),
        )
        cls._evaluation_records.append(item)
        return item

    @classmethod
    def get_evaluation_metrics(cls) -> ForecastEvaluationResponse:
        """Computes aggregate evaluation summary across logged synthetic forecasts."""
        records = cls._evaluation_records
        if not records:
            return ForecastEvaluationResponse(
                total_evaluated=0,
                mean_absolute_error=0.0,
                directional_accuracy=1.0,
                evaluations=[],
            )

        mae = sum(r.absolute_error for r in records) / len(records)
        dir_acc = sum(1 for r in records if r.is_directionally_correct) / len(records)

        return ForecastEvaluationResponse(
            total_evaluated=len(records),
            mean_absolute_error=round(mae, 4),
            directional_accuracy=round(dir_acc, 4),
            evaluations=records[-50:],  # Return recent 50 evaluations
        )
