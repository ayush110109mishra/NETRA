"""
Integration and API tests for NETRA Event Intelligence Engine (Phase 2).
Tests master multi-event analysis, API endpoints, scenario execution,
and verifies 50 consecutive runs of identical input produce bit-for-bit identical outputs.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from simulation.synthetic_data import (
    MULTI_SCENARIO_STRONG_CORRELATION,
    MULTI_SCENARIO_TEMPORAL_CLUSTER,
    MULTI_SCENARIO_DUPLICATES,
    MULTI_SCENARIO_FALSE_CORRELATION,
    MULTI_SCENARIOS_MAP,
)
from intelligence.event_intelligence import EventIntelligenceEngine

client = TestClient(app)


def test_engine_analyze_strong_correlation():
    """Verify end-to-end multi-event pipeline on strongly correlated scenario."""
    engine = EventIntelligenceEngine()
    response = engine.analyze_events(MULTI_SCENARIO_STRONG_CORRELATION)

    assert response.event_count == 3
    assert len(response.normalized_events) == 3
    assert len(response.correlations) > 0
    # Strong scenario must yield at least one cluster
    assert len(response.clusters) >= 1
    # Check structured assessment
    assert response.assessment.summary
    assert len(response.assessment.observed) > 0
    assert len(response.assessment.inferred) > 0
    assert len(response.assessment.uncertain) > 0


def test_engine_analyze_duplicates():
    """Verify deduplication marks duplicates without deletion in master response."""
    engine = EventIntelligenceEngine()
    response = engine.analyze_events(MULTI_SCENARIO_DUPLICATES)
    dup_results = response.duplicates
    assert len(dup_results) == 3
    assert dup_results[0].is_duplicate is False
    assert dup_results[1].is_duplicate is True
    assert dup_results[2].is_duplicate is True


def test_api_multi_event_analyze():
    """Verify POST /api/v1/intelligence/events/analyze returns 200 and typed schema."""
    payload = MULTI_SCENARIO_TEMPORAL_CLUSTER.model_dump(mode="json")
    res = client.post("/api/v1/intelligence/events/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "analysis_id" in data
    assert data["event_count"] == 4
    assert "clusters" in data
    assert "correlations" in data
    assert "assessment" in data
    assert "observed" in data["assessment"]
    assert "inferred" in data["assessment"]
    assert "uncertain" in data["assessment"]


def test_api_multi_event_scenarios():
    """Verify listing and executing Phase 2 synthetic scenarios via API."""
    res_list = client.get("/api/v1/intelligence/events/scenarios")
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert "scenarios" in list_data
    assert "strong_correlation" in list_data["scenarios"]
    assert "false_correlation" in list_data["scenarios"]

    # Execute valid scenario
    res_exec = client.post("/api/v1/intelligence/events/scenarios/strong_correlation/analyze")
    assert res_exec.status_code == 200
    assert res_exec.json()["event_count"] == 3

    # Execute invalid scenario
    res_invalid = client.post("/api/v1/intelligence/events/scenarios/invalid_key/analyze")
    assert res_invalid.status_code == 404


def test_strict_multi_event_determinism():
    """
    CRITICAL DETERMINISM REQUIREMENT (Section 27):
    Verify 50 consecutive runs of identical multi-event input produce bit-for-bit identical outputs.
    """
    engine = EventIntelligenceEngine()
    baseline = engine.analyze_events(MULTI_SCENARIO_STRONG_CORRELATION)

    for i in range(50):
        run = engine.analyze_events(MULTI_SCENARIO_STRONG_CORRELATION)
        assert run.analysis_id == baseline.analysis_id, f"Analysis ID differed at run {i}"
        assert run.event_count == baseline.event_count
        assert len(run.correlations) == len(baseline.correlations)
        for c1, c2 in zip(run.correlations, baseline.correlations):
            assert c1.correlation_score == c2.correlation_score
            assert c1.strength == c2.strength
            assert c1.relationships == c2.relationships
            assert c1.confidence == c2.confidence
        assert len(run.clusters) == len(baseline.clusters)
        for cl1, cl2 in zip(run.clusters, baseline.clusters):
            assert cl1.cluster_id == cl2.cluster_id
            assert cl1.cohesion_score == cl2.cohesion_score
            assert cl1.event_ids == cl2.event_ids
        assert run.baseline_drift == baseline.baseline_drift
        assert run.assessment == baseline.assessment
