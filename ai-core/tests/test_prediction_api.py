"""
API integration and strict determinism tests for NETRA Phase 6 Predictive Intelligence.
Tests all 7 REST endpoints, verifies the 16 synthetic scenarios,
and executes a strict 50-run bit-for-bit determinism verification test.
"""

from datetime import datetime, timezone, timedelta
import hashlib
import json
import pytest
from fastapi.testclient import TestClient

from main import app
from simulation.prediction_scenarios import get_all_prediction_scenarios


@pytest.fixture
def client():
    return TestClient(app)


def test_api_list_scenarios(client):
    response = client.get("/api/v1/intelligence/predictions/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 16
    assert len(data["scenarios"]) == 16
    assert "scenario_1_stable_entity" in data["scenarios"]
    assert "scenario_6_cold_start_entity" in data["scenarios"]


def test_api_analyze_prediction(client):
    payload = {
        "entity_id": "PRED-TEST-01",
        "target": "ACTIVITY_STATE",
        "horizon": "SHORT",
        "as_of": "2026-09-12T12:00:00Z",
        "custom_events": [
            {
                "event_id": f"EVT-T-{i}",
                "event_type": "RADAR_TRACK",
                "timestamp": f"2026-09-12T11:{i*10:02d}:00Z",
                "location": {"latitude": 34.0, "longitude": 74.5},
                "attributes": {"activity_level": 0.50},
            }
            for i in range(6)
        ],
    }
    response = client.post("/api/v1/intelligence/predictions/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["entity_id"] == "PRED-TEST-01"
    assert "forecast" in data
    assert "assessment" in data
    assert "epistemic_ledger" in data["assessment"]
    assert "PREDICTED" in data["assessment"]["epistemic_ledger"]


def test_api_entity_predictions_history(client):
    response = client.get("/api/v1/intelligence/entities/PRED-TEST-01/predictions")
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == "PRED-TEST-01"
    assert len(data["predictions"]) >= 1


def test_api_entity_forecast(client):
    response = client.get("/api/v1/intelligence/entities/PRED-TEST-01/forecast")
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == "PRED-TEST-01"
    assert "current_forecasts" in data
    assert len(data["current_forecasts"]) == 6
    assert 0.0 <= data["overall_confidence"] <= 1.0
    assert 0.0 <= data["overall_uncertainty"] <= 1.0


def test_api_global_history(client):
    response = client.get("/api/v1/intelligence/predictions/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_api_evaluation(client):
    response = client.get("/api/v1/intelligence/predictions/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert "total_evaluated" in data
    assert "directional_accuracy" in data
    assert "mean_absolute_error" in data


@pytest.mark.parametrize("scenario_id", list(get_all_prediction_scenarios().keys()))
def test_all_16_scenarios_execution(client, scenario_id):
    response = client.post(f"/api/v1/intelligence/predictions/scenarios/{scenario_id}/analyze")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["forecast"] is not None
    assert data["assessment"] is not None


def test_strict_50_run_determinism(client):
    """
    Executes identical analysis 50 times under pinned evaluation time.
    Asserts bit-for-bit identical SHA-256 JSON hash across all 50 iterations.
    """
    payload = {
        "entity_id": "PRED-DETERMINISM-01",
        "target": "ACTIVITY_STATE",
        "horizon": "SHORT",
        "as_of": "2026-09-12T12:00:00Z",
        "custom_events": [
            {
                "event_id": f"EVT-DET-{i}",
                "event_type": "SURVEILLANCE_SWEEP",
                "timestamp": f"2026-09-12T11:{i*5:02d}:00Z",

                "location": {"latitude": 34.05, "longitude": 74.85},
                "attributes": {"activity_level": round(0.30 + i * 0.08, 3), "speed": 42.0},
            }
            for i in range(8)
        ],
    }

    reference_hash = None

    for run_idx in range(50):
        response = client.post("/api/v1/intelligence/predictions/analyze", json=payload)
        assert response.status_code == 200
        raw_json = json.dumps(response.json(), sort_keys=True)
        run_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

        if reference_hash is None:
            reference_hash = run_hash
        else:
            assert run_hash == reference_hash, f"Determinism failure at run {run_idx}: {run_hash} != {reference_hash}"

    assert reference_hash is not None
