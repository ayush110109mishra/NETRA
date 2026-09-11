"""
Baseline Drift Analysis Engine for NETRA Intelligence Core.
Evaluates multi-tiered deviations between historical baseline, recent operational baseline,
and current observed event activity.
"""

from typing import List, Optional
from config import NetraConfig, default_config
from models.event_intelligence import CanonicalEvent, BaselineDriftResult


class BaselineDriftAnalyzer:
    """Analyzes baseline drift across operational windows."""

    def __init__(self, config: Optional[NetraConfig] = None):
        self.cfg = config or default_config

    def analyze_drift(
        self,
        events: List[CanonicalEvent],
        historical_baseline: Optional[float] = None,
        recent_baseline: Optional[float] = None,
    ) -> BaselineDriftResult:
        """
        Compute baseline drift score, trend direction, and confidence.
        """
        if not events:
            return BaselineDriftResult(
                score=0.0,
                direction="STABLE",
                confidence=0.50,
                description="No operational events provided for baseline comparison.",
            )

        # Average observed activity in current batch
        activities = [float(e.attributes.get("activity_level", 0.35)) for e in events]
        current_activity = sum(activities) / len(activities)

        # If baselines are missing, inspect first event raw attributes or use defaults
        hist = historical_baseline
        rec = recent_baseline

        if hist is None and events and events[0].raw_event:
            hist_ctx = events[0].raw_event.get("historical_context", {})
            if isinstance(hist_ctx, dict):
                hist = hist_ctx.get("previous_activity")

        # Cold-start case: No historical baseline available
        if hist is None:
            return BaselineDriftResult(
                score=0.0,
                direction="STABLE",
                confidence=0.30,
                description="Insufficient historical baseline data to determine operational drift (cold start).",
            )

        # If recent baseline not explicitly provided, use current activity as recent estimate
        if rec is None:
            rec = current_activity

        delta = rec - hist
        # Relative drift magnitude
        magnitude = abs(delta) / max(0.25, hist)
        drift_score = round(min(1.0, max(0.0, magnitude)), 2)

        if delta > 0.06:
            direction = "INCREASE"
            desc = (
                f"Sector activity exhibits an upward operational drift (+{drift_score*100:.0f}%) "
                f"from baseline {hist:.2f} to recent {rec:.2f}."
            )
        elif delta < -0.06:
            direction = "DECREASE"
            desc = (
                f"Sector activity exhibits a downward operational drift (-{drift_score*100:.0f}%) "
                f"from baseline {hist:.2f} to recent {rec:.2f}."
            )
        else:
            direction = "STABLE"
            desc = f"Operational activity remains stable relative to historical baseline ({hist:.2f} vs {rec:.2f})."

        confidence = 0.85 if len(events) >= 3 else 0.70

        return BaselineDriftResult(
            score=drift_score,
            direction=direction,
            confidence=confidence,
            description=desc,
        )
