"""
Unit tests for Ask NETRA query planner generating inspectable DAG step plans.
"""

from datetime import datetime, timezone
from models.ask_netra import ParsedQuery, QueryIntent, StructuredFilters
from query.planner import QueryPlanner


def test_planner_generates_steps_for_status():
    planner = QueryPlanner()
    parsed = ParsedQuery(
        query_id="QRY-TEST-01",
        raw_query="What is the operational situation?",
        intent=QueryIntent.STATUS,
        intent_confidence=0.90,
        filters=StructuredFilters(),
        parsed_at=datetime.now(timezone.utc),
    )
    plan = planner.plan(parsed)
    assert len(plan.steps) == 4
    engines = [s.engine for s in plan.steps]
    assert "event_engine" in engines
    assert "entity_engine" in engines
    assert "risk_engine" in engines
    assert "reasoning_engine" in engines


def test_planner_generates_steps_for_forecast():
    planner = QueryPlanner()
    parsed = ParsedQuery(
        query_id="QRY-TEST-02",
        raw_query="What will ENTITY-01 do next?",
        intent=QueryIntent.FORECAST,
        intent_confidence=0.92,
        primary_entity_id="ENTITY-01",
        filters=StructuredFilters(),
        parsed_at=datetime.now(timezone.utc),
    )
    plan = planner.plan(parsed)
    assert len(plan.steps) == 2
    assert plan.steps[0].engine == "prediction_engine"
    assert plan.steps[1].engine == "reasoning_engine"


def test_planner_generates_comparison_steps():
    planner = QueryPlanner()
    parsed = ParsedQuery(
        query_id="QRY-TEST-03",
        raw_query="Compare ENTITY-01 to ENTITY-02",
        intent=QueryIntent.COMPARISON,
        intent_confidence=0.95,
        primary_entity_id="ENTITY-01",
        secondary_entity_id="ENTITY-02",
        filters=StructuredFilters(),
        parsed_at=datetime.now(timezone.utc),
    )
    plan = planner.plan(parsed)
    assert len(plan.steps) == 3
    assert plan.steps[2].action == "compare_entities"
