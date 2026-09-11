"""
API Contract and Strict 50-Run Determinism Tests for NETRA Phase 5 Fusion.
Verifies all REST API endpoints under /api/v1/intelligence/fusion and bit-for-bit reproducibility.
"""

import json
from fastapi.testclient import TestClient
import pytest

from main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_api_fusion_sources(client):
    response = client.get("/api/v1/intelligence/fusion/sources")
    assert response.status_code == 200
    sources = response.json()
    assert isinstance(sources, list)
    assert len(sources) >= 8
    source_ids = [s["source_id"] for s in sources]
    assert "RADAR_01" in source_ids
    assert "RADAR_01_DUP" in source_ids
    assert "OPTICAL_01" in source_ids
    assert "TELEMETRY_01" in source_ids


def test_api_fusion_scenarios_list(client):
    response = client.get("/api/v1/intelligence/fusion/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 14
    assert "scenario_1_all_sources_agree" in data["scenarios"]
    assert "scenario_2_position_conflict" in data["scenarios"]
    assert "scenario_8_duplicate_same_source" in data["scenarios"]
    assert "scenario_10_successful_entity_resolution" in data["scenarios"]
    assert "scenario_14_mixed_quality_fusion" in data["scenarios"]


def test_api_fusion_scenario_1_execution(client):
    response = client.post("/api/v1/intelligence/fusion/scenarios/scenario_1_all_sources_agree/analyze")
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "SUCCESS"
    assert res["schema_version"] == "phase5-v1"
    assert len(res["fused_observations"]) == 1
    fo = res["fused_observations"][0]
    assert fo["entity_id"] == "ENTITY-07"
    assert fo["independent_source_count"] == 3
    assert fo["agreement_score"] >= 0.85
    assert fo["fusion_confidence"] >= 0.85
    assert len(res["conflicts"]) == 0
    assert len(res["evidence_ledger"]) >= 1


def test_api_fusion_scenario_2_position_conflict(client):
    response = client.post("/api/v1/intelligence/fusion/scenarios/scenario_2_position_conflict/analyze")
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "SUCCESS"
    assert len(res["conflicts"]) >= 1
    c = res["conflicts"][0]
    assert c["conflict_type"] == "POSITION"
    assert "RADAR_01" in c["claims"]
    assert "SENSOR_B" in c["claims"]


def test_api_fusion_scenario_8_duplicate_feed(client):
    response = client.post("/api/v1/intelligence/fusion/scenarios/scenario_8_duplicate_same_source/analyze")
    assert response.status_code == 200
    res = response.json()
    fo = res["fused_observations"][0]
    # Retransmission must not increase independent count
    assert fo["independent_source_count"] == 1
    assert res["corroboration"]["duplicate_source_count"] == 1


def test_api_fusion_scenario_10_entity_resolution(client):
    response = client.post("/api/v1/intelligence/fusion/scenarios/scenario_10_successful_entity_resolution/analyze")
    assert response.status_code == 200
    res = response.json()
    fo = res["fused_observations"][0]
    assert fo["entity_id"] == "ENTITY-07"


def test_api_entity_fused_intelligence(client):
    # Execute analysis first so entity cache has data
    client.post("/api/v1/intelligence/fusion/scenarios/scenario_1_all_sources_agree/analyze")

    response = client.get("/api/v1/intelligence/entities/ENTITY-07/fused-intelligence")
    assert response.status_code == 200
    profile = response.json()
    assert profile["entity_id"] == "ENTITY-07"
    assert len(profile["fused_observations"]) >= 1
    assert len(profile["supporting_sources"]) >= 1
    assert 0.0 <= profile["confidence"] <= 1.0


def test_api_fusion_conflicts_endpoint(client):
    # Trigger conflict scenario
    client.post("/api/v1/intelligence/fusion/scenarios/scenario_2_position_conflict/analyze")

    response = client.get("/api/v1/intelligence/fusion/conflicts")
    assert response.status_code == 200
    conflicts = response.json()
    assert isinstance(conflicts, list)
    assert len(conflicts) >= 1


def test_api_strict_50_run_determinism(client):
    """
    CRITICAL REQUIREMENT (Section 27):
    Execute the same multi-source fusion analysis 50 times.
    All 50 outputs must be bit-for-bit identical with zero drift.
    """
    first_response_json = None

    for run_idx in range(50):
        response = client.post("/api/v1/intelligence/fusion/scenarios/scenario_14_mixed_quality_fusion/analyze")
        assert response.status_code == 200
        data = response.json()
        # Wall clock execution duration differs by microseconds; pop it before bit-for-bit check
        if data.get("phase4_anomaly_assessment") and "metadata" in data["phase4_anomaly_assessment"]:
            data["phase4_anomaly_assessment"]["metadata"].pop("processing_duration_ms", None)
        current_dump = json.dumps(data, sort_keys=True)

        if first_response_json is None:
            first_response_json = current_dump
        else:
            assert current_dump == first_response_json, f"Determinism violation detected at run {run_idx + 1}/50!"

