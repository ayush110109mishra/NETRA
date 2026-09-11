"""
Test suite for NETRA Phase 4 Anomaly Attribution Engine.
Verifies mathematical consistency (contribution = score * weight),
ranking order of driving factors, and primary dimension identification.
"""

import pytest
from config import AnomalyDimensionWeights
from models.anomaly_intelligence import DimensionScoreItem
from anomaly.attribution import AnomalyAttributor


def test_attribution_exact_mathematical_consistency():
    weights = AnomalyDimensionWeights(
        temporal=0.12,
        spatial=0.18,
        kinematic=0.18,
        frequency=0.12,
        event_type=0.10,
        behavioral=0.12,
        relational=0.10,
        contextual=0.08,
    )
    attributor = AnomalyAttributor(weights=weights)

    dim_scores = {
        "temporal": DimensionScoreItem(dimension="temporal", score=0.20, explanation=""),
        "spatial": DimensionScoreItem(dimension="spatial", score=0.85, explanation="Far boundary breach"),
        "kinematic": DimensionScoreItem(dimension="kinematic", score=0.90, explanation="Speed spike 140 km/h"),
        "frequency": DimensionScoreItem(dimension="frequency", score=0.10, explanation=""),
        "event_type": DimensionScoreItem(dimension="event_type", score=0.0, explanation=""),
        "behavioral": DimensionScoreItem(dimension="behavioral", score=0.30, explanation=""),
        "relational": DimensionScoreItem(dimension="relational", score=0.0, explanation=""),
        "contextual": DimensionScoreItem(dimension="contextual", score=0.0, explanation=""),
    }

    attribution = attributor.attribute(dim_scores)

    # Check top factors
    assert len(attribution.top_factors) == 8
    # Kinematic: score 0.90 * weight 0.18 = 0.1620
    # Spatial: score 0.85 * weight 0.18 = 0.1530
    assert attribution.primary_dimension == "kinematic"
    assert attribution.top_factors[0].factor == "kinematic"
    assert attribution.top_factors[1].factor == "spatial"

    # Mathematical consistency across all factors
    for factor in attribution.top_factors:
        expected_contribution = round(factor.score * factor.weight, 4)
        assert abs(factor.contribution - expected_contribution) < 1e-4

    # Ranking descending by contribution
    contributions = [f.contribution for f in attribution.top_factors]
    assert contributions == sorted(contributions, reverse=True)
