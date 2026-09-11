"""
Integration tests for NETRA Phase 8 REST API Endpoints.
Verifies all /api/v1/intelligence/graph/* routes via FastAPI TestClient.
"""

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_api_scenarios_listing():
    resp = client.get("/api/v1/intelligence/graph/scenarios")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 18


def test_api_scenario_analyze_endpoint():
    resp = client.post("/api/v1/intelligence/graph/scenarios/SCENARIO-16-FULL-INTELLIGENCE-CHAIN/analyze")
    assert resp.status_code == 200
    data = resp.json()
    assert data["statistics"]["entity_count"] >= 1
    assert data["statistics"]["event_count"] >= 1
    assert data["statistics"]["anomaly_count"] >= 1
    assert data["statistics"]["forecast_count"] >= 1
    assert "version" in data
    assert data["version"] == "8.0.0"


def test_api_nodes_and_edges():
    # Load a scenario first
    client.post("/api/v1/intelligence/graph/scenarios/SCENARIO-02-MULTI-HOP-NETWORK/analyze")

    nodes_resp = client.get("/api/v1/intelligence/graph/nodes")
    assert nodes_resp.status_code == 200
    nodes = nodes_resp.json()
    assert len(nodes) >= 4

    edges_resp = client.get("/api/v1/intelligence/graph/edges")
    assert edges_resp.status_code == 200
    edges = edges_resp.json()
    assert len(edges) >= 3


def test_api_entity_network():
    client.post("/api/v1/intelligence/graph/scenarios/SCENARIO-02-MULTI-HOP-NETWORK/analyze")
    resp = client.get("/api/v1/intelligence/graph/entities/ENTITY-B/network?depth=1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["focus_entity"] == "ENTITY-B"
    assert len(data["neighbors"]) >= 2


def test_api_path():
    client.post("/api/v1/intelligence/graph/scenarios/SCENARIO-02-MULTI-HOP-NETWORK/analyze")
    resp = client.get("/api/v1/intelligence/graph/path?source=ENTITY-A&target=ENTITY-D")
    assert resp.status_code == 200
    data = resp.json()
    assert data["path_found"] is True
    assert data["hop_count"] == 3


def test_api_communities_and_centrality():
    client.post("/api/v1/intelligence/graph/scenarios/SCENARIO-09-COMMUNITY-DETECTION/analyze")

    comm_resp = client.get("/api/v1/intelligence/graph/communities")
    assert comm_resp.status_code == 200
    comms = comm_resp.json()
    assert len(comms) == 2

    cent_resp = client.get("/api/v1/intelligence/graph/centrality")
    assert cent_resp.status_code == 200
    cents = cent_resp.json()
    assert len(cents) > 0


def test_api_changes_bad_request():
    # start_time >= end_time must return 400
    t = "2026-09-12T12:00:00Z"
    resp = client.get(f"/api/v1/intelligence/graph/changes?start_time={t}&end_time={t}")
    assert resp.status_code == 400
