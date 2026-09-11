"""
Anomaly Trend Analyzer for NETRA Phase 4 Anomaly Intelligence.
Computes score deltas, rate of change across observation windows,
and directional trajectory (INCREASE, DECREASE, STABLE, UNKNOWN).
"""

from typing import Optional
from models.anomaly_intelligence import TrendDirection, AnomalyTrend


class AnomalyTrendAnalyzer:
    """Evaluates the rate and direction of anomaly progression over time."""

    @staticmethod
    def analyze(
        current_score: float,
        previous_score: Optional[float] = None,
        time_delta_hours: Optional[float] = None,
    ) -> AnomalyTrend:
        """
        Evaluate trend progression between consecutive evaluation windows.
        """
        if previous_score is None:
            return AnomalyTrend(
                previous=None,
                current=round(current_score, 4),
                delta=0.0,
                rate_of_change=0.0,
                direction=TrendDirection.UNKNOWN,
            )

        delta = round(current_score - previous_score, 4)

        if time_delta_hours and time_delta_hours > 0:
            rate_of_change = round(delta / time_delta_hours, 4)
        else:
            rate_of_change = delta

        # Directional classification
        if delta > 0.05:
            direction = TrendDirection.INCREASE
        elif delta < -0.05:
            direction = TrendDirection.DECREASE
        else:
            direction = TrendDirection.STABLE

        return AnomalyTrend(
            previous=round(previous_score, 4),
            current=round(current_score, 4),
            delta=delta,
            rate_of_change=rate_of_change,
            direction=direction,
        )
