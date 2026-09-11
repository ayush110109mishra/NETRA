"""
Integration and API test suite for NETRA Phase 4 Anomaly & Risk Intelligence.
Tests all Phase 4 endpoints, scenarios, sector indices, hotspots,
and verifies strict 50-run bit-for-bit determinism.
"""

from fastapi.testclient import TestClient
from main import app
from simulation.synthetic_data import get_anomaly_scenario

client = TestClient(app)


def test_api_list_anomaly_scenarios():
    response = client.get("/api/v1/intelligence/anomalies/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 14
    assert "scenario_1_normal" in data["scenarios"]
    assert "scenario_2_kinematic_spike" in data["scenarios"]
    assert "scenario_7_multi_dimensional" in data["scenarios"]


def test_api_run_anomaly_scenario():
    response = client.post("/api/v1/intelligence/anomalies/scenarios/scenario_2_kinematic_spike/analyze")
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == "ENTITY-P4-KINE-02"
    assert data["dimensions"]["kinematic"] >= 0.70
    assert data["anomaly"]["score"] >= 0.15
    assert data["attribution"]["primary_dimension"] == "kinematic"
    assert data["risk"]["model_version"] == "phase4-v1"
    assert "GROUND_SPEED_EXCESS" in data["dimension_details"]["kinematic"]["indicators"]


def test_api_analyze_custom_anomaly_request():
    payload = {
        "entity_id": "ENTITY-CUSTOM-01",
        "events": [
            {
                "event_id": "EVT-CUST-01",
                "event_type": "movement",
                "timestamp": "2026-09-11T12:00:00Z",
                "coordinates": {"latitude": 26.85, "longitude": 80.95},
                "attributes": {"speed": 135.0, "activity_level": 0.85},
            }
        ],
    }
    response = client.post("/api/v1/intelligence/anomalies/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == "ENTITY-CUSTOM-01"
    assert data["dimensions"]["kinematic"] >= 0.70
    assert len(data["assessment"]["observed"]) >= 3


def test_api_entity_anomalies_history():
    response = client.get("/api/v1/intelligence/entities/ENTITY-P4-KINE-02/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == "ENTITY-P4-KINE-02"
    assert len(data["anomalies"]) > 0


def test_api_entity_risk_history():
    response = client.get("/api/v1/intelligence/entities/ENTITY-P4-KINE-02/risk-history")
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == "ENTITY-P4-KINE-02"
    assert len(data["history"]) > 0


def test_api_sector_anomaly_index():
    response = client.get("/api/v1/intelligence/sectors/SECTOR_ALPHA/anomaly-index")
    assert response.status_code == 200
    data = response.json()
    assert data["sector_id"] == "SECTOR_ALPHA"
    assert "anomaly_index" in data
    assert "entity_count" in data


def test_api_anomaly_hotspots():
    response = client.get("/api/v1/intelligence/anomalies/hotspots?min_score=0.40")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_api_strict_50_run_determinism():
    """
    CRITICAL REQUIREMENT: 50 consecutive identical runs must produce bit-for-bit identical outputs.
    """
    scen = get_anomaly_scenario("scenario_7_multi_dimensional")
    assert scen is not None

    payload = {
        "entity_id": scen["entity_id"],
        "events": [e.model_dump(mode="json") for e in scen["events"]],
        "context": scen.get("context"),
        "as_of": "2026-09-11T12:00:00Z",
    }

    first_response = client.post("/api/v1/intelligence/anomalies/analyze", json=payload).json()

    for run_idx in range(49):
        run_response = client.post("/api/v1/intelligence/anomalies/analyze", json=payload).json()
        # Compare key intelligence outputs bit-for-bit
        assert run_response["anomaly"]["score"] == first_response["anomaly"]["score"], f"Score mismatch on run {run_idx}"
        assert run_response["anomaly"]["level"] == first_response["anomaly"]["level"]
        assert run_response["anomaly"]["state"] == first_response["anomaly"]["state"]
        assert run_response["dimensions"] == first_response["dimensions"]
        assert run_response["attribution"] == first_response["attribution"]
        assert run_response["risk"]["score"] == first_response["risk"]["score"]
        assert run_response["risk"]["level"] == first_response["risk"]["level"]
        assert run_response["risk"]["state"] == first_response["risk"]["state"]
        assert run_response["assessment"] == first_response["assessment"]
        assert run_response["analysis_id"] == first_response["analysis_id"]
