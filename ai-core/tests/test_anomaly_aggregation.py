"""
Test suite for NETRA Phase 4 Multi-Dimensional Anomaly Aggregator.
Verifies linear weighted summation, cross-dimensional synergy bonus (>=3 elevated dimensions),
and categorical level threshold mappings.
"""

import pytest
from config import AnomalyDimensionWeights, AnomalyClassificationThresholds
from models.anomaly_intelligence import (
    AnomalyLevel,
    DimensionScoreItem,
)
from anomaly.aggregation import AnomalyAggregator


def test_weights_sum_to_one():
    w = AnomalyDimensionWeights()
    w.validate()
    total = (
        w.temporal
        + w.spatial
        + w.kinematic
        + w.frequency
        + w.event_type
        + w.behavioral
        + w.relational
        + w.contextual
    )
    assert abs(total - 1.0) < 1e-6


def test_aggregation_nominal():
    aggregator = AnomalyAggregator()
    dim_scores = {
        dim: DimensionScoreItem(dimension=dim, score=0.0, explanation="")
        for dim in [
            "temporal",
            "spatial",
            "kinematic",
            "frequency",
            "event_type",
            "behavioral",
            "relational",
            "contextual",
        ]
    }
    score, level, multi_dim = aggregator.aggregate(dim_scores)
    assert score == 0.0
    assert level == AnomalyLevel.NOMINAL
    assert multi_dim.temporal == 0.0


def test_aggregation_single_dimension_linear():
    # Only kinematic elevated to 1.0 (weight = 0.18), no synergy
    aggregator = AnomalyAggregator()
    dim_scores = {
        dim: DimensionScoreItem(dimension=dim, score=0.0, explanation="")
        for dim in [
            "temporal",
            "spatial",
            "kinematic",
            "frequency",
            "event_type",
            "behavioral",
            "relational",
            "contextual",
        ]
    }
    dim_scores["kinematic"] = DimensionScoreItem(dimension="kinematic", score=1.0, explanation="")
    score, level, _ = aggregator.aggregate(dim_scores)
    assert abs(score - 0.18) < 1e-4
    assert level == AnomalyLevel.NOMINAL


def test_aggregation_multi_dimensional_synergy():
    # 3 dimensions elevated >= 0.50 (spatial 0.8, kinematic 0.8, event_type 0.8)
    aggregator = AnomalyAggregator()
    dim_scores = {
        dim: DimensionScoreItem(dimension=dim, score=0.0, explanation="")
        for dim in [
            "temporal",
            "spatial",
            "kinematic",
            "frequency",
            "event_type",
            "behavioral",
            "relational",
            "contextual",
        ]
    }
    dim_scores["spatial"] = DimensionScoreItem(dimension="spatial", score=0.8, explanation="")
    dim_scores["kinematic"] = DimensionScoreItem(dimension="kinematic", score=0.8, explanation="")
    dim_scores["event_type"] = DimensionScoreItem(dimension="event_type", score=0.8, explanation="")

    base_expected = (0.8 * 0.18) + (0.8 * 0.18) + (0.8 * 0.10)  # 0.144 + 0.144 + 0.08 = 0.368
    # 3 elevated -> synergy = 0.04
    score, level, _ = aggregator.aggregate(dim_scores)
    assert score > base_expected
    assert abs(score - (base_expected + 0.04)) < 1e-3
    assert level == AnomalyLevel.LOW or level == AnomalyLevel.MODERATE


def test_aggregation_critical_level():
    aggregator = AnomalyAggregator()
    dim_scores = {
        dim: DimensionScoreItem(dimension=dim, score=0.95, explanation="")
        for dim in [
            "temporal",
            "spatial",
            "kinematic",
            "frequency",
            "event_type",
            "behavioral",
            "relational",
            "contextual",
        ]
    }
    score, level, _ = aggregator.aggregate(dim_scores)
    assert score >= 0.90
    assert level == AnomalyLevel.CRITICAL
