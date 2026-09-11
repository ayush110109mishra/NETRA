"""
API integration and error handling tests for NETRA Intelligence Core.
Tests FastAPI endpoints and verifies structured error responses.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from simulation.synthetic_data import SCENARIO_NORMAL

client = TestClient(app)


def test_health_endpoints():
    """Verify /health and /api/v1/health return 200 OK."""
    res1 = client.get("/health")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "ok"
    assert data1["service"] == "netra-ai-core"

    res2 = client.get("/api/v1/health")
    assert res2.status_code == 200
    assert res2.json()["status"] == "ok"


def test_analyze_endpoint_valid():
    """Verify POST /api/v1/intelligence/analyze with valid synthetic payload."""
    payload = SCENARIO_NORMAL.model_dump(mode="json")
    response = client.post("/api/v1/intelligence/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert data["classification"] == "NORMAL"
    assert "risk" in data
    assert "score" in data["risk"]
    assert "factors" in data["risk"]
    assert "confidence" in data
    assert "confidence_breakdown" in data
    assert "assessment" in data
    assert data["metadata"]["data_classification"] == "SYNTHETIC"


def test_scenarios_endpoints():
    """Verify listing scenarios and executing predefined scenario by key."""
    res_list = client.get("/api/v1/intelligence/scenarios")
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert "scenarios" in list_data
    assert "normal" in list_data["scenarios"]
    assert "anomalous" in list_data["scenarios"]

    # Execute valid scenario
    res_exec = client.post("/api/v1/intelligence/scenarios/anomalous/analyze")
    assert res_exec.status_code == 200
    assert res_exec.json()["classification"] == "ANOMALOUS"

    # Execute invalid scenario
    res_invalid = client.post("/api/v1/intelligence/scenarios/non_existent_key/analyze")
    assert res_invalid.status_code == 404
    assert res_invalid.json()["error"]["code"] == "HTTP_404"


def test_validation_error_missing_event():
    """Verify missing required field returns structured error envelope."""
    payload = SCENARIO_NORMAL.model_dump(mode="json")
    del payload["event"]  # remove required field

    response = client.post("/api/v1/intelligence/analyze", json=payload)
    assert response.status_code == 422
    err_body = response.json()
    assert "error" in err_body
    assert err_body["error"]["code"] == "INVALID_INPUT"
    assert err_body["error"]["field"] == "event"


def test_validation_error_invalid_coordinates():
    """Verify out-of-range coordinates (> 90.0) trigger structured validation error."""
    payload = SCENARIO_NORMAL.model_dump(mode="json")
    payload["location"]["latitude"] = 999.0  # Invalid latitude

    response = client.post("/api/v1/intelligence/analyze", json=payload)
    assert response.status_code == 422
    err_body = response.json()
    assert "error" in err_body
    assert err_body["error"]["code"] == "INVALID_INPUT"
    assert "latitude" in err_body["error"]["field"]


def test_validation_error_invalid_activity_level():
    """Verify activity level > 1.0 triggers structured validation error."""
    payload = SCENARIO_NORMAL.model_dump(mode="json")
    payload["attributes"]["activity_level"] = 2.5  # Invalid activity level > 1.0

    response = client.post("/api/v1/intelligence/analyze", json=payload)
    assert response.status_code == 422
    err_body = response.json()
    assert "error" in err_body
    assert err_body["error"]["code"] == "INVALID_INPUT"
    assert "activity_level" in err_body["error"]["field"]
