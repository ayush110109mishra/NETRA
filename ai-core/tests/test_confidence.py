"""
Unit tests for NETRA Confidence Engine.
Verifies data completeness, historical depth, signal consistency, and uncertainty handling.
"""

import pytest
from simulation.synthetic_data import (
    SCENARIO_NORMAL,
    SCENARIO_INSUFFICIENT_HISTORY,
    SCENARIO_CONFLICTING_SIGNALS,
)
from intelligence.confidence import calculate_confidence


def test_confidence_complete_baseline():
    """Verify scenarios with complete fields and deep history receive high confidence."""
    confidence, breakdown = calculate_confidence(SCENARIO_NORMAL)
    assert 0.80 <= confidence <= 1.0
    assert breakdown.historical_baseline_depth == 1.0  # 45 historical events
    assert breakdown.signal_consistency == 1.0


def test_confidence_cold_start_insufficient_history():
    """Verify zero historical events depresses historical baseline depth and overall confidence."""
    confidence, breakdown = calculate_confidence(SCENARIO_INSUFFICIENT_HISTORY)
    # Zero history reduces baseline depth to 0.15
    assert breakdown.historical_baseline_depth == 0.15
    assert confidence < 0.60


def test_confidence_conflicting_signals():
    """Verify telemetry contradictions (high speed with zero activity/sensors) penalize consistency."""
    confidence, breakdown = calculate_confidence(SCENARIO_CONFLICTING_SIGNALS)
    assert breakdown.signal_consistency < 0.70
    assert confidence < 0.75


def test_confidence_bounded():
    """Verify confidence score is strictly bounded in [0.0, 1.0]."""
    for sc in [SCENARIO_NORMAL, SCENARIO_INSUFFICIENT_HISTORY, SCENARIO_CONFLICTING_SIGNALS]:
        conf, breakdown = calculate_confidence(sc)
        assert 0.0 <= conf <= 1.0
        assert 0.0 <= breakdown.data_completeness <= 1.0
        assert 0.0 <= breakdown.historical_baseline_depth <= 1.0
        assert 0.0 <= breakdown.signal_consistency <= 1.0
