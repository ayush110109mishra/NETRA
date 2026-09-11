"""
Spatial Alignment Engine for NETRA Phase 5.
Evaluates geospatial agreement between multi-sensor observations using
pure-Python Haversine distance and sensor uncertainty boundary overlaps.
"""

from typing import Optional
import logging

from config import NetraConfig, default_config, SpatialAlignmentConfig
from models.geo import haversine_distance_km
from models.fusion_intelligence import (
    CanonicalObservation,
    SpatialAlignmentLevel,
    SpatialAlignmentResult,
)

logger = logging.getLogger("netra.fusion.spatial")


class SpatialAligner:
    """
    Evaluates spatial consistency across independent sensor observations.
    Distinguishes full agreement, partial agreement with uncertainty overlap,
    and material spatial contradictions.
    """

    def __init__(self, config: Optional[NetraConfig] = None):
        self.config = config or default_config
        self.params: SpatialAlignmentConfig = self.config.spatial_alignment

    def align(
        self,
        obs1: CanonicalObservation,
        obs2: CanonicalObservation,
    ) -> SpatialAlignmentResult:
        """
        Computes great circle distance, checks uncertainty boundaries,
        and classifies spatial compatibility level.
        """
        if not obs1.position or not obs2.position:
            # Missing coordinates in one or both observations
            return SpatialAlignmentResult(
                obs1_id=obs1.observation_id,
                obs2_id=obs2.observation_id,
                distance_km=0.0,
                alignment_level=SpatialAlignmentLevel.PARTIAL_AGREEMENT,
                spatial_compatibility_score=0.50,
                uncertainty_overlap=False,
                explanation="One or both observations lack geospatial coordinates; indeterminate spatial alignment.",
            )

        dist_km = haversine_distance_km(obs1.position, obs2.position)
        combined_uncertainty = (obs1.position_uncertainty_km or 0.10) + (obs2.position_uncertainty_km or 0.10)
        uncertainty_overlap = dist_km <= combined_uncertainty

        # Classification
        if dist_km <= self.params.agreement_max_distance_km or dist_km <= combined_uncertainty:
            level = SpatialAlignmentLevel.AGREEMENT
            # Score 0.85 - 1.0
            ratio = dist_km / max(0.001, max(self.params.agreement_max_distance_km, combined_uncertainty))
            score = 1.0 - (0.15 * min(1.0, ratio))
            explanation = (
                f"Spatial agreement: distance {dist_km:.2f}km within tolerance "
                f"(threshold={self.params.agreement_max_distance_km}km, combined uncertainty={combined_uncertainty:.2f}km)"
            )
        elif dist_km <= self.params.partial_agreement_max_distance_km or uncertainty_overlap:
            level = SpatialAlignmentLevel.PARTIAL_AGREEMENT
            # Score 0.35 - 0.85
            span = max(0.001, self.params.partial_agreement_max_distance_km - self.params.agreement_max_distance_km)
            ratio = (dist_km - self.params.agreement_max_distance_km) / span
            score = 0.85 - (0.50 * min(1.0, max(0.0, ratio)))
            explanation = (
                f"Partial spatial agreement: distance {dist_km:.2f}km "
                f"(uncertainty overlap={uncertainty_overlap})"
            )
        else:
            level = SpatialAlignmentLevel.CONFLICT
            # Score < 0.35
            excess = dist_km - self.params.partial_agreement_max_distance_km
            score = max(0.0, 0.30 - (0.02 * excess))
            explanation = (
                f"SPATIAL CONFLICT: Reported locations differ by {dist_km:.2f}km, "
                f"exceeding conflict threshold {self.params.conflict_min_distance_km}km"
            )

        bounded_score = round(max(0.0, min(1.0, score)), 4)

        return SpatialAlignmentResult(
            obs1_id=obs1.observation_id,
            obs2_id=obs2.observation_id,
            distance_km=round(dist_km, 3),
            alignment_level=level,
            spatial_compatibility_score=bounded_score,
            uncertainty_overlap=uncertainty_overlap,
            explanation=explanation,
        )
