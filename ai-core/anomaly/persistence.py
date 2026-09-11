"""
Anomaly Persistence Analyzer for NETRA Phase 4 Anomaly Intelligence.
Evaluates persistence states across historical windows:
TRANSIENT, PERSISTENT, RECURRING, ESCALATING, DECLINING.
"""

from typing import List, Optional
from config import PersistenceConfig, default_config
from models.anomaly_intelligence import (
    AnomalyPersistenceState,
    AnomalyPersistence,
    AnomalyTrend,
    TrendDirection,
)


class AnomalyPersistenceAnalyzer:
    """Evaluates multi-window persistence and temporal recurrence of anomalies."""

    def __init__(self, config: Optional[PersistenceConfig] = None):
        self.config = config or default_config.persistence

    def analyze(
        self,
        history_scores: List[float],
        trend: AnomalyTrend,
    ) -> AnomalyPersistence:
        """
        Assess persistence state, elevated window counts, peak, and mean score.
        """
        if not history_scores:
            return AnomalyPersistence(
                state=AnomalyPersistenceState.TRANSIENT,
                elevated_windows=0,
                consecutive_windows=0,
                peak_score=0.0,
                average_score=0.0,
            )

        current_score = history_scores[-1]
        elevated_windows = sum(1 for s in history_scores if s >= 0.25)
        peak_score = round(max(history_scores), 4)
        average_score = round(sum(history_scores) / len(history_scores), 4)

        # Count consecutive elevated windows at the tail of history
        consecutive_windows = 0
        for s in reversed(history_scores):
            if s >= 0.25:
                consecutive_windows += 1
            else:
                break

        # State assessment logic
        if current_score < 0.25:
            if peak_score >= 0.50 and len(history_scores) > 1:
                state = AnomalyPersistenceState.DECLINING
            else:
                state = AnomalyPersistenceState.TRANSIENT
        else:
            # Current score is elevated (>= 0.25)
            if consecutive_windows >= 2 and (
                trend.rate_of_change >= self.config.escalating_rate_threshold
                or (trend.direction == TrendDirection.INCREASE and current_score >= 0.70)
            ):
                state = AnomalyPersistenceState.ESCALATING
            elif (
                trend.rate_of_change <= self.config.declining_rate_threshold
                or (trend.direction == TrendDirection.DECREASE and current_score < 0.50)
            ):
                state = AnomalyPersistenceState.DECLINING
            elif consecutive_windows >= self.config.persistent_min_windows:
                state = AnomalyPersistenceState.PERSISTENT
            elif elevated_windows >= 2 and consecutive_windows == 1:
                state = AnomalyPersistenceState.RECURRING
            else:
                state = AnomalyPersistenceState.TRANSIENT

        return AnomalyPersistence(
            state=state,
            elevated_windows=elevated_windows,
            consecutive_windows=consecutive_windows,
            peak_score=peak_score,
            average_score=average_score,
        )
