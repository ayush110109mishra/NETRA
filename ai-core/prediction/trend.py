"""
Trend and Regime Change Detection Engine for NETRA Phase 6.
Calculates least-squares linear slopes, directionality, trend strength, persistence,
volatility, second-order acceleration, and detects operational regime shifts.
"""

import math
from typing import List, Optional, Tuple
import logging

from config import NetraConfig, default_config, PredictionGatingConfig
from models.predictive_intelligence import TemporalStateSequence, TrendMetrics

logger = logging.getLogger("netra.prediction.trend")


class TrendEngine:
    """
    Evaluates multi-point time-series trajectory and stability.
    Prevents single-spike false positives and identifies operational regime changes.
    """

    def __init__(self, config: Optional[NetraConfig] = None):
        self.config = config or default_config
        self.gating: PredictionGatingConfig = self.config.prediction_gating

    def analyze_trend(self, sequence: TemporalStateSequence) -> TrendMetrics:
        """
        Computes comprehensive trend metrics across a TemporalStateSequence.
        """
        points = sequence.points
        n = len(points)

        if n < 2:
            return TrendMetrics(
                slope=0.0,
                direction="STABLE",
                strength=0.0,
                persistence=1.0,
                acceleration=0.0,
                volatility=0.0,
                is_regime_change=False,
            )

        values = [p.value for p in points]

        # 1. Standard Deviation Volatility
        mean_val = sum(values) / n
        var = sum((v - mean_val) ** 2 for v in values) / n
        volatility = math.sqrt(var)

        # 2. Linear Regression Slope
        # Use normalized indices x = 0, 1, ..., n-1
        xs = list(range(n))
        x_mean = (n - 1) / 2.0
        numerator = sum((xs[i] - x_mean) * (values[i] - mean_val) for i in range(n))
        denominator = sum((xs[i] - x_mean) ** 2 for i in range(n))
        slope = (numerator / denominator) if denominator > 0 else 0.0

        # Correlation coefficient (r) for trend strength
        x_var = sum((x - x_mean) ** 2 for x in xs) / n
        std_x = math.sqrt(x_var) if x_var > 0 else 1.0
        std_y = volatility if volatility > 0 else 1.0
        r = (numerator / (n * std_x * std_y)) if (std_x * std_y > 0) else 0.0
        strength = min(1.0, abs(r))


        # 3. Persistence Ratio (fraction of steps moving in direction of slope)
        if n >= 2:
            steps = [values[i] - values[i - 1] for i in range(1, n)]
            if slope > 0.01:
                concordant = sum(1 for s in steps if s >= -0.02)
            elif slope < -0.01:
                concordant = sum(1 for s in steps if s <= 0.02)
            else:
                concordant = sum(1 for s in steps if abs(s) <= 0.10)
            persistence = concordant / len(steps)
        else:
            persistence = 1.0

        # 4. Acceleration (slope difference between first and second half)
        acceleration = 0.0
        is_regime_change = False
        if n >= 4:
            mid = n // 2
            first_half = values[:mid]
            second_half = values[mid:]

            def calc_half_slope(half_vals: List[float]) -> float:
                hn = len(half_vals)
                if hn < 2:
                    return 0.0
                h_mean = sum(half_vals) / hn
                hx_mean = (hn - 1) / 2.0
                h_num = sum((i - hx_mean) * (half_vals[i] - h_mean) for i in range(hn))
                h_den = sum((i - hx_mean) ** 2 for i in range(hn))
                return (h_num / h_den) if h_den > 0 else 0.0

            slope1 = calc_half_slope(first_half)
            slope2 = calc_half_slope(second_half)
            acceleration = round(slope2 - slope1, 4)

            # Regime Change Detection: significant divergence between earlier baseline and recent trend
            if abs(acceleration) >= self.gating.regime_change_slope_delta:
                is_regime_change = True

        # 5. Trend Direction Classification
        if volatility >= self.gating.volatility_threshold and persistence < 0.60:
            direction = "VOLATILE"
        elif slope >= 0.03:
            direction = "RISING"
        elif slope <= -0.03:
            direction = "FALLING"
        else:
            direction = "STABLE"

        return TrendMetrics(
            slope=round(slope, 4),
            direction=direction,
            strength=round(max(0.0, min(1.0, strength)), 4),
            persistence=round(max(0.0, min(1.0, persistence)), 4),
            acceleration=acceleration,
            volatility=round(max(0.0, min(1.0, volatility)), 4),
            is_regime_change=is_regime_change,
        )
