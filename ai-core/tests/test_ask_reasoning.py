"""
Unit tests for Ask NETRA reasoning engine (Why?, What changed?, Comparison).
"""

from datetime import datetime, timezone
from config import default_config
from entities.repository import EntityRepository
from models.ask_netra import ParsedQuery, QueryIntent, StructuredFilters
from query.engine import QueryInterpretationEngine
from query.executor import QueryExecutor
from reasoning.engine import ReasoningEngine
from simulation.synthetic_data import seed_entity_repository


def test_reasoning_why_attribution():
    repo = EntityRepository(default_config.entity)
    seed_entity_repository(repo)
    query_engine = QueryInterpretationEngine(config=default_config, known_entity_ids=set(repo._entities.keys()) | set(repo._entity_events.keys()))
    executor = QueryExecutor(config=default_config, repository=repo)
    reasoning = ReasoningEngine()

    as_of = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    parsed, plan, val_status, _ = query_engine.interpret("Why is ENTITY-01 high risk?", as_of=as_of)
    context = executor.execute_plan(plan, parsed, as_of=as_of)
    answer, ledger = reasoning.reason_and_synthesize(parsed, context)

    assert "Attribution" in answer.headline or "Root Cause" in answer.headline
    assert len(answer.key_findings) > 0
    assert len(answer.claims) > 0
    assert len(answer.claims[0].supporting_evidence_ids) > 0


def test_reasoning_what_changed():
    repo = EntityRepository(default_config.entity)
    seed_entity_repository(repo)
    query_engine = QueryInterpretationEngine(config=default_config, known_entity_ids=set(repo._entities.keys()) | set(repo._entity_events.keys()))
    executor = QueryExecutor(config=default_config, repository=repo)
    reasoning = ReasoningEngine()

    as_of = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    parsed, plan, val_status, _ = query_engine.interpret("What changed with ENTITY-01?", as_of=as_of)
    context = executor.execute_plan(plan, parsed, as_of=as_of)
    answer, ledger = reasoning.reason_and_synthesize(parsed, context)

    assert "Changes" in answer.headline or "Drift" in answer.headline
    assert len(answer.key_findings) > 0
