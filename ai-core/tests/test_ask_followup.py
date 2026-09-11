"""
Unit tests verifying multi-turn conversation context and pronoun continuation.
"""

from datetime import datetime, timezone
from config import default_config
from entities.repository import EntityRepository
from intelligence.ask_netra import AskNetraEngine
from models.ask_netra import AskNetraRequest, QueryIntent
from simulation.synthetic_data import seed_entity_repository


def test_conversational_followup_resolves_pronoun():
    repo = EntityRepository(default_config.entity)
    seed_entity_repository(repo)
    engine = AskNetraEngine(config=default_config, repository=repo)

    session_id = "test_session_followup_01"
    as_of = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)

    # Turn 1: Explicit entity query
    req1 = AskNetraRequest(
        query="Provide entity profile for ENTITY-01",
        session_id=session_id,
        as_of=as_of,
    )
    resp1 = engine.ask(req1)
    assert resp1.parsed_query.primary_entity_id == "ENTITY-01"
    assert resp1.parsed_query.intent == QueryIntent.ENTITY_PROFILE

    # Turn 2: Follow-up query using pronoun "its risk"
    req2 = AskNetraRequest(
        query="What is its risk?",
        session_id=session_id,
        as_of=as_of,
    )
    resp2 = engine.ask(req2)
    assert resp2.parsed_query.primary_entity_id == "ENTITY-01"
    assert resp2.parsed_query.intent == QueryIntent.RISK
    assert "ENTITY-01" in resp2.answer.headline


def test_session_state_cleared():
    repo = EntityRepository(default_config.entity)
    seed_entity_repository(repo)
    engine = AskNetraEngine(config=default_config, repository=repo)

    session_id = "test_session_clear"
    as_of = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)

    # Turn 1
    req1 = AskNetraRequest(
        query="Tell me about ENTITY-02",
        session_id=session_id,
        as_of=as_of,
    )
    engine.ask(req1)
    assert engine.sessions[session_id].active_entity_id == "ENTITY-02"

    # Clear session
    engine.clear_session(session_id)
    assert session_id not in engine.sessions
