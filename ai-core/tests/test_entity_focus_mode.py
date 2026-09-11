"""
Master Integration & Focus Mode Tests for NETRA Entity Intelligence Engine.
Tests all Phase 3 API endpoints, Focus Mode schemas, four-tier assessments,
and strict 50-run determinism verification.
"""

import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_entity_focus_mode_success():
    """Verify GET /api/v1/intelligence/entities/{entity_id} produces valid Focus Mode schema."""
    response = client.get("/api/v1/intelligence/entities/ENTITY-STABLE-01")
    assert response.status_code == 200
    data = response.json()

    # Core Entity
    assert data["entity"]["entity_id"] == "ENTITY-STABLE-01"
    assert data["entity"]["entity_type"] == "VEHICLE"
    assert data["entity"]["event_count"] == 10

    # Profile
    assert data["profile"]["dominant_event_type"] == "movement"
    assert data["profile"]["active_duration_hours"] > 0

    # Baseline & Behavioral Assessment
    assert data["behavior"]["baseline_status"] == "SUFFICIENT_HISTORY"
    assert data["behavior"]["sample_count"] == 10
    assert data["behavior"]["average_speed"] > 0

    # Risk & Confidence
    assert "score" in data["risk"]
    assert "level" in data["risk"]
    assert "score" in data["confidence"]
    assert data["confidence"]["level"] in ["HIGH", "MEDIUM", "LOW"]

    # Four-Tier Assessment
    assessment = data["assessment"]
    assert assessment["summary"] is not None
    assert len(assessment["observed"]) > 0
    assert len(assessment["inferred"]) > 0
    assert len(assessment["predicted"]) > 0
    assert len(assessment["uncertain"]) > 0

    # 30% Map Context
    assert "centroid" in data["map_context"]
    assert len(data["map_context"]["observed_coordinates"]) == 10

    # Chronological Timeline
    assert len(data["timeline"]) == 10


def test_get_entity_focus_mode_not_found():
    """Verify 404 when querying non-existent entity."""
    response = client.get("/api/v1/intelligence/entities/NON-EXISTENT-ID")
    assert response.status_code == 404
    data = response.json()
    msg = data.get("detail") or data.get("error", {}).get("message", "")
    assert "not found" in msg.lower()


def test_compare_entities_endpoint():
    """Verify POST /api/v1/intelligence/entities/compare."""
    payload = {
        "entity_ids": ["ENTITY-STABLE-01", "ENTITY-SHIFT-09"]
    }
    response = client.post("/api/v1/intelligence/entities/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert len(data["entities"]) == 2
    assert "comparison_summary" in data
    assert "Highest risk:" in data["comparison_summary"]

    ids = [e["entity_id"] for e in data["entities"]]
    assert "ENTITY-STABLE-01" in ids
    assert "ENTITY-SHIFT-09" in ids


def test_search_and_roster_endpoint():
    """Verify GET /api/v1/intelligence/entities with filtering."""
    # 1. Total roster
    response = client.get("/api/v1/intelligence/entities")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 10
    assert len(data["entities"]) >= 10

    # 2. Filter by query
    query_resp = client.get("/api/v1/intelligence/entities?query=STABLE")
    assert query_resp.status_code == 200
    q_data = query_resp.json()
    assert q_data["total_count"] >= 1
    assert any("STABLE" in e["entity_id"] for e in q_data["entities"])


def test_entity_scenarios_endpoints():
    """Verify GET and POST for Phase 3 synthetic scenarios."""
    # List scenarios
    list_resp = client.get("/api/v1/intelligence/entities/scenarios")
    assert list_resp.status_code == 200
    scenarios = list_resp.json()["scenarios"]
    assert "stable" in scenarios
    assert "cold_start" in scenarios
    assert "spatial_expansion" in scenarios
    assert "behavioral_shift" in scenarios

    # Execute scenario
    exec_resp = client.post("/api/v1/intelligence/entities/scenarios/spatial_expansion/analyze")
    assert exec_resp.status_code == 200
    res = exec_resp.json()
    assert res["entity"]["entity_id"] == "ENTITY-EXPAND-05"
    assert res["changes"]["detected"] is True
    assert any(c["feature"] == "spatial_expansion" for c in res["changes"]["changes"])


def test_entity_events_endpoint():
    """Verify GET /api/v1/intelligence/entities/{entity_id}/events."""
    resp = client.get("/api/v1/intelligence/entities/ENTITY-STABLE-01/events?limit=5")
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) == 5
    # Verify chronological ordering
    assert events[0]["timestamp"] >= events[1]["timestamp"]


def test_entity_relationships_endpoint():
    """Verify GET /api/v1/intelligence/entities/{entity_id}/relationships."""
    resp = client.get("/api/v1/intelligence/entities/ENTITY-ASSOC-07A/relationships")
    assert resp.status_code == 200
    edges = resp.json()
    assert len(edges) >= 1
    assert any(e["entity_id"] == "ENTITY-ASSOC-07B" for e in edges)


def test_strict_50_run_determinism():
    """
    STRICT 50-RUN DETERMINISM TEST.
    Verifies that 50 consecutive identical calls to Focus Mode produce
    100% bit-for-bit identical outputs (excluding processing_time_ms).
    """
    first_payload = None

    for i in range(50):
        resp = client.get("/api/v1/intelligence/entities/ENTITY-STABLE-01")
        assert resp.status_code == 200
        data = resp.json()

        # Remove volatile processing timing metric
        if "metadata" in data and "processing_time_ms" in data["metadata"]:
            del data["metadata"]["processing_time_ms"]

        canonical_json = json.dumps(data, sort_keys=True)

        if first_payload is None:
            first_payload = canonical_json
        else:
            assert canonical_json == first_payload, f"Determinism violation at run #{i+1}!"


def test_all_ten_synthetic_scenarios():
    """Verify each of the 10 Phase 3 synthetic scenarios behaves according to operational requirements."""
    # 1. Stable
    r1 = client.post("/api/v1/intelligence/entities/scenarios/stable/analyze").json()
    assert r1["entity"]["entity_id"] == "ENTITY-STABLE-01"
    assert r1["behavior"]["baseline_status"] == "SUFFICIENT_HISTORY"
    assert r1["anomalies"]["level"] == "LOW"

    # 2. Cold Start
    r2 = client.post("/api/v1/intelligence/entities/scenarios/cold_start/analyze").json()
    assert r2["entity"]["entity_id"] == "ENTITY-COLD-02"
    assert r2["behavior"]["baseline_status"] == "INSUFFICIENT_HISTORY"
    assert r2["confidence"]["score"] <= 0.35
    assert any(f["factor"] == "COLD_START_RESTRICTION" for f in r2["confidence"]["factors"])

    # 3. Activity Surge
    r3 = client.post("/api/v1/intelligence/entities/scenarios/activity_surge/analyze").json()
    assert r3["entity"]["entity_id"] == "ENTITY-SURGE-03"
    assert r3["changes"]["detected"] is True
    assert any(c["feature"] == "frequency" for c in r3["changes"]["changes"])

    # 4. Activity Drop
    r4 = client.post("/api/v1/intelligence/entities/scenarios/activity_drop/analyze").json()
    assert r4["entity"]["entity_id"] == "ENTITY-DROP-04"
    assert r4["changes"]["detected"] is True
    assert any(c["feature"] == "frequency" for c in r4["changes"]["changes"])

    # 5. Spatial Expansion
    r5 = client.post("/api/v1/intelligence/entities/scenarios/spatial_expansion/analyze").json()
    assert r5["entity"]["entity_id"] == "ENTITY-EXPAND-05"
    assert r5["changes"]["detected"] is True
    assert any(c["feature"] == "spatial_expansion" for c in r5["changes"]["changes"])

    # 6. New Event Type
    r6 = client.post("/api/v1/intelligence/entities/scenarios/new_event_type/analyze").json()
    assert r6["entity"]["entity_id"] == "ENTITY-NEWTYPE-06"
    assert r6["changes"]["detected"] is True
    assert any(c["feature"] == "event_type" for c in r6["changes"]["changes"])

    # 7. Repeated Association
    r7 = client.post("/api/v1/intelligence/entities/scenarios/repeated_association/analyze").json()
    assert r7["entity"]["entity_id"] == "ENTITY-ASSOC-07A"
    assert any(r["relationship_type"].upper() == "REPEATED_ASSOCIATION" for r in r7["relationships"])

    # 8. Multi Cluster Participation
    r8 = client.post("/api/v1/intelligence/entities/scenarios/multi_cluster/analyze").json()
    assert r8["entity"]["entity_id"] == "ENTITY-MULTICLUSTER-08"
    assert len(r8["clusters"]) >= 2

    # 9. Behavioral Shift
    r9 = client.post("/api/v1/intelligence/entities/scenarios/behavioral_shift/analyze").json()
    assert r9["entity"]["entity_id"] == "ENTITY-SHIFT-09"
    assert r9["anomalies"]["score"] >= 0.70
    assert r9["risk"]["score"] >= 0.60

    # 10. Contradictory Telemetry
    r10 = client.post("/api/v1/intelligence/entities/scenarios/contradictory_telemetry/analyze").json()
    assert r10["entity"]["entity_id"] == "ENTITY-CONFLICT-10"
    assert len(r10["confidence"]["contradictions"]) > 0

