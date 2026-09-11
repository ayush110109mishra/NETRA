"""
Unit tests for Ask NETRA query executor with seeded synthetic repository.
"""

from datetime import datetime, timezone
from config import default_config
from entities.repository import EntityRepository
from models.ask_netra import ParsedQuery, QueryIntent, StructuredFilters
from query.planner import QueryPlanner
from query.executor import QueryExecutor
from simulation.synthetic_data import seed_entity_repository


def test_executor_retrieves_profile_and_events():
    repo = EntityRepository(default_config.entity)
    seed_entity_repository(repo)
    executor = QueryExecutor(config=default_config, repository=repo)
    planner = QueryPlanner()

    parsed = ParsedQuery(
        query_id="QRY-EXEC-01",
        raw_query="Provide profile for ENTITY-01",
        intent=QueryIntent.ENTITY_PROFILE,
        intent_confidence=0.92,
        primary_entity_id="ENTITY-01",
        filters=StructuredFilters(),
        parsed_at=datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc),
    )
    plan = planner.plan(parsed)
    context = executor.execute_plan(plan, parsed)

    assert context["entity_profile"] is not None
    assert len(context["raw_events"]) > 0
    assert context["entity_profile"].entity_id == "ENTITY-01"


def test_executor_runs_anomaly_and_risk():
    repo = EntityRepository(default_config.entity)
    seed_entity_repository(repo)
    executor = QueryExecutor(config=default_config, repository=repo)
    planner = QueryPlanner()

    parsed = ParsedQuery(
        query_id="QRY-EXEC-02",
        raw_query="What is the risk level of ENTITY-01?",
        intent=QueryIntent.RISK,
        intent_confidence=0.91,
        primary_entity_id="ENTITY-01",
        filters=StructuredFilters(),
        parsed_at=datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc),
    )
    plan = planner.plan(parsed)
    context = executor.execute_plan(plan, parsed)

    assert context["anomaly_analysis"] is not None
    assert context["risk_profile"] is not None
