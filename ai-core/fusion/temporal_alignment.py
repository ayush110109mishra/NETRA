"""
Temporal Alignment Engine for NETRA Phase 5.
Evaluates inter-observation temporal proximity, handles sensor clock skew,
detects stale telemetry, and enforces configurable fusion time windows.
"""

from datetime import datetime, timezone
import math
from typing import Optional
import logging

from config import NetraConfig, default_config, TemporalAlignmentConfig
from models.fusion_intelligence import CanonicalObservation, TemporalAlignmentResult

logger = logging.getLogger("netra.fusion.temporal")


class TemporalAligner:
    """
    Deterministic temporal alignment and compatibility evaluator.
    Prevents fusing non-synchronous events across distant time intervals.
    """

    def __init__(self, config: Optional[NetraConfig] = None):
        self.config = config or default_config
        self.params: TemporalAlignmentConfig = self.config.temporal_alignment

    def align(
        self,
        obs1: CanonicalObservation,
        obs2: CanonicalObservation,
        reference_time: Optional[datetime] = None,
    ) -> TemporalAlignmentResult:
        """
        Computes temporal delta, checks fusion window compatibility,
        and assigns an explainable compatibility score.
        """
        delta_sec = abs((obs1.timestamp - obs2.timestamp).total_seconds())
        ref_time = reference_time or max(obs1.timestamp, obs2.timestamp)
        if ref_time.tzinfo is None:
            ref_time = ref_time.replace(tzinfo=timezone.utc)

        # Check staleness against reference time
        age1 = abs((ref_time - obs1.timestamp).total_seconds())
        age2 = abs((ref_time - obs2.timestamp).total_seconds())
        is_stale = (age1 > self.params.stale_observation_threshold_seconds) or (
            age2 > self.params.stale_observation_threshold_seconds
        )

        is_compatible = delta_sec <= self.params.max_fusion_window_seconds

        # Compute compatibility score
        if delta_sec <= self.params.clock_skew_tolerance_seconds:
            # Near-perfect alignment / clock skew tolerance
            score = 1.0
            explanation = f"Exact/skew alignment (delta={delta_sec:.1f}s <= {self.params.clock_skew_tolerance_seconds}s)"
        elif delta_sec <= self.params.near_alignment_window_seconds:
            # Linear decay from 1.0 down to 0.85
            ratio = (delta_sec - self.params.clock_skew_tolerance_seconds) / max(
                1.0, (self.params.near_alignment_window_seconds - self.params.clock_skew_tolerance_seconds)
            )
            score = 1.0 - (0.15 * ratio)
            explanation = f"High temporal compatibility (delta={delta_sec:.1f}s <= {self.params.near_alignment_window_seconds}s)"
        elif delta_sec <= self.params.max_fusion_window_seconds:
            # Linear decay from 0.85 down to 0.20
            ratio = (delta_sec - self.params.near_alignment_window_seconds) / max(
                1.0, (self.params.max_fusion_window_seconds - self.params.near_alignment_window_seconds)
            )
            score = 0.85 - (0.65 * ratio)
            explanation = f"Moderate temporal compatibility within fusion window (delta={delta_sec:.1f}s)"
        else:
            score = 0.0
            explanation = (
                f"Temporal incompatibility: delta={delta_sec:.1f}s exceeds "
                f"max fusion window {self.params.max_fusion_window_seconds}s"
            )

        if is_stale:
            score = max(0.0, score * 0.5)
            explanation += " [STALE TELEMETRY DETECTED]"

        bounded_score = round(max(0.0, min(1.0, score)), 4)

        return TemporalAlignmentResult(
            obs1_id=obs1.observation_id,
            obs2_id=obs2.observation_id,
            delta_seconds=round(delta_sec, 2),
            compatibility_score=bounded_score,
            is_compatible=is_compatible,
            is_stale=is_stale,
            explanation=explanation,
        )

    def is_stale_observation(
        self,
        obs: CanonicalObservation,
        reference_time: Optional[datetime] = None,
    ) -> bool:
        """Determines if a single observation exceeds the staleness threshold."""
        ref = reference_time or datetime.now(timezone.utc)
        if ref.tzinfo is None:
            ref = ref.replace(tzinfo=timezone.utc)
        age = abs((ref - obs.timestamp).total_seconds())
        return age > self.params.stale_observation_threshold_seconds
