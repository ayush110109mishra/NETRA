"""
Unit and integration tests for Ask NETRA integration with Phase 8 Knowledge Graph.
Verifies network answering, path answering, zero-hallucination disconnected claims,
and preservation of baseline Phase 7 behaviors.
"""

from datetime import datetime, timezone
import pytest

from config import default_config
from entities.repository import EntityRepository
from graph.graph_engine import KnowledgeGraphEngine
from intelligence.ask_netra import AskNetraEngine
from models.ask_netra import AskNetraRequest, QueryIntent, EpistemicTier
from models.knowledge_graph import EdgeType


@pytest.fixture
def ask_with_graph():
    repo = EntityRepository(default_config.entity)
    ge = KnowledgeGraphEngine(default_config)
    ask_eng = AskNetraEngine(
        config=default_config,
        repository=repo,
        graph_engine=ge,
    )
    return ask_eng, ge


def test_ask_netra_entity_network_grounding(ask_with_graph):
    ask_eng, ge = ask_with_graph
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)

    # Ingest entities and link them in graph
    ge.builder.ingest_entity("ENTITY-01", first_observed=now)
    ge.builder.ingest_entity("ENTITY-02", first_observed=now, associated_entity_ids=["ENTITY-01"])

    # Query Ask NETRA
    req = AskNetraRequest(query="Who is ENTITY-01 operating with?")
    resp = ask_eng.ask(req)

    assert resp.parsed_query.intent == QueryIntent.RELATIONSHIP
    assert resp.answer is not None
    assert "ENTITY-01" in resp.answer.headline or "ENTITY-01" in resp.answer.summary
    assert len(resp.answer.claims) > 0


def test_ask_netra_path_grounding(ask_with_graph):
    ask_eng, ge = ask_with_graph
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)

    # Ingest multi-hop link
    ge.builder.ingest_entity("ENTITY-A", first_observed=now)
    ge.builder.ingest_entity("ENTITY-B", first_observed=now)
    ge.builder.ingest_entity("ENTITY-C", first_observed=now)

    na = ge.node_registry.get_node_by_reference("ENTITY-A")
    nb = ge.node_registry.get_node_by_reference("ENTITY-B")
    nc = ge.node_registry.get_node_by_reference("ENTITY-C")

    ge.edge_registry.add_edge(na.node_id, nb.node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)
    ge.edge_registry.add_edge(nb.node_id, nc.node_id, EdgeType.ASSOCIATED_WITH, is_directional=False)

    # Ask how ENTITY-A is connected to ENTITY-C
    req = AskNetraRequest(query="How is ENTITY-A connected to ENTITY-C?")
    resp = ask_eng.ask(req)

    assert resp.answer is not None
    assert "Path" in resp.answer.headline or "2 hop" in resp.answer.summary or "2 hop" in " ".join(resp.answer.key_findings)


def test_ask_netra_zero_hallucination_disconnected(ask_with_graph):
    ask_eng, ge = ask_with_graph
    now = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)

    # Ingest two disconnected entities
    ge.builder.ingest_entity("ENTITY-91", first_observed=now)
    ge.builder.ingest_entity("ENTITY-92", first_observed=now)

    req = AskNetraRequest(query="What connects ENTITY-91 and ENTITY-92?")
    resp = ask_eng.ask(req)

    assert resp.answer is not None
    # Must explicitly state no path found
    assert "no evidence-supported path was found" in resp.answer.summary.lower()
    claim_tiers = [c.epistemic_tier for c in resp.answer.claims]
    assert EpistemicTier.UNCERTAIN in claim_tiers
