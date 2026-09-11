"""
Unit tests for Ask NETRA FastAPI REST endpoints.
"""

from datetime import datetime, timezone
from fastapi.testclient import TestClient
import pytest
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_ask_endpoint(client):
    payload = {
        "query": "What is the operational situation?",
        "session_id": "api_test_session_01",
        "as_of": "2026-09-12T12:00:00Z",
    }
    resp = client.post("/api/v1/intelligence/ask", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["schema_version"] == "phase7-v1"
    assert "query_id" in data
    assert "parsed_query" in data
    assert "answer" in data
    assert len(data["answer"]["key_findings"]) > 0


def test_api_ask_parse_endpoint(client):
    payload = {
        "query": "Is ENTITY-01 anomalous?",
        "as_of": "2026-09-12T12:00:00Z",
    }
    resp = client.post("/api/v1/intelligence/ask/parse", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["parsed_query"]["intent"] == "ANOMALY"
    assert len(data["execution_plan"]["steps"]) > 0


def test_api_capabilities_endpoint(client):
    resp = client.get("/api/v1/intelligence/ask/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["supported_intents"]) == 16
    assert "OBSERVED" in data["epistemic_tiers"]


def test_api_examples_endpoint(client):
    resp = client.get("/api/v1/intelligence/ask/examples")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["examples"]) >= 10


def test_api_scenarios_list_and_exec(client):
    resp = client.get("/api/v1/intelligence/ask/scenarios")
    assert resp.status_code == 200
    scenarios = resp.json()
    assert len(scenarios) == 20

    # Execute first scenario
    exec_resp = client.post("/api/v1/intelligence/ask/scenarios/scenario_01_status")
    assert exec_resp.status_code == 200
    data = exec_resp.json()
    assert data["parsed_query"]["intent"] == "STATUS"
