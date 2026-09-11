"""
Determinism verification tests for NETRA Intelligence Core.
Verifies that 50 consecutive runs of identical inputs produce bit-for-bit identical outputs.
"""

import pytest
from intelligence.engine import analyze_intelligence
from simulation.synthetic_data import (
    SCENARIO_NORMAL,
    SCENARIO_ANOMALOUS,
    SCENARIO_HIGH_RISK_CORRELATED,
)


def test_strict_determinism_normal():
    """Verify SCENARIO_NORMAL produces 100% reproducible results over 50 iterations."""
    baseline = analyze_intelligence(SCENARIO_NORMAL)

    for i in range(50):
        run = analyze_intelligence(SCENARIO_NORMAL)
        assert run.analysis_id == baseline.analysis_id, f"Analysis ID differed at run {i}"
        assert run.classification == baseline.classification
        assert run.severity == baseline.severity
        assert run.risk.score == baseline.risk.score
        assert run.risk.level == baseline.risk.level
        assert len(run.risk.factors) == len(baseline.risk.factors)
        for f1, f2 in zip(run.risk.factors, baseline.risk.factors):
            assert f1.factor == f2.factor
            assert f1.weight == f2.weight
            assert f1.contribution == f2.contribution
        assert run.confidence == baseline.confidence
        assert run.related_entities == baseline.related_entities
        assert run.related_events == baseline.related_events
        assert run.assessment == baseline.assessment
        assert run.indicators == baseline.indicators


def test_strict_determinism_anomalous():
    """Verify SCENARIO_ANOMALOUS produces 100% reproducible results over 50 iterations."""
    baseline = analyze_intelligence(SCENARIO_ANOMALOUS)

    for i in range(50):
        run = analyze_intelligence(SCENARIO_ANOMALOUS)
        assert run.analysis_id == baseline.analysis_id
        assert run.classification == baseline.classification
        assert run.severity == baseline.severity
        assert run.risk.score == baseline.risk.score
        assert run.confidence == baseline.confidence
        assert run.assessment == baseline.assessment


def test_strict_determinism_high_risk():
    """Verify SCENARIO_HIGH_RISK_CORRELATED produces 100% reproducible results over 50 iterations."""
    baseline = analyze_intelligence(SCENARIO_HIGH_RISK_CORRELATED)

    for i in range(50):
        run = analyze_intelligence(SCENARIO_HIGH_RISK_CORRELATED)
        assert run.analysis_id == baseline.analysis_id
        assert run.classification == baseline.classification
        assert run.risk.score == baseline.risk.score
        assert run.assessment == baseline.assessment
