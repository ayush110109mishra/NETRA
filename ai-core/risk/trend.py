"""
Risk Trend Engine for NETRA Phase 4 Risk Intelligence.
Calculates risk trajectory, delta, volatility metrics, and directional progression.
"""

import math
from typing import List, Optional
from models.risk_intelligence import (
    RiskTrendDirection,
    RiskTrendProfile,
)


class RiskTrendAnalyzer:
    """Computes analytical risk trends and score volatility across historical windows."""

    @staticmethod
    def analyze(
        current_score: float,
        previous_score: Optional[float] = None,
        history: Optional[List[float]] = None,
    ) -> RiskTrendProfile:
        """
        Evaluate risk trend, rate of change, and historical volatility.
        """
        if previous_score is None:
            return RiskTrendProfile(
                direction=RiskTrendDirection.UNKNOWN,
                delta=0.0,
                volatility=0.0,
                previous_score=None,
                current_score=round(current_score, 4),
            )

        delta = round(current_score - previous_score, 4)

        # Volatility: standard deviation of recent risk scores
        hist = list(history) if history else []
        if not hist or hist[-1] != current_score:
            hist.append(current_score)

        if len(hist) >= 3:
            mean = sum(hist) / len(hist)
            variance = sum((x - mean) ** 2 for x in hist) / len(hist)
            volatility = round(math.sqrt(variance), 4)
        else:
            volatility = 0.0

        # Directional classification
        if volatility > 0.25:
            direction = RiskTrendDirection.VOLATILE
        elif delta > 0.05:
            direction = RiskTrendDirection.RISING
        elif delta < -0.05:
            direction = RiskTrendDirection.FALLING
        else:
            direction = RiskTrendDirection.STABLE

        return RiskTrendProfile(
            direction=direction,
            delta=delta,
            volatility=volatility,
            previous_score=round(previous_score, 4),
            current_score=round(current_score, 4),
        )
