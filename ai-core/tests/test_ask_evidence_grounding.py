"""
Unit tests verifying 5-tier epistemic ledgering and 100% grounded claims.
"""

from datetime import datetime, timezone
from config import default_config
from entities.repository import EntityRepository
from intelligence.ask_netra import AskNetraEngine
from models.ask_netra import AskNetraRequest
from simulation.synthetic_data import seed_entity_repository


def test_claims_strictly_cite_evidence_ids():
    repo = EntityRepository(default_config.entity)
    seed_entity_repository(repo)
    engine = AskNetraEngine(config=default_config, repository=repo)

    req = AskNetraRequest(
        query="What is the risk level of ENTITY-01?",
        as_of=datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc),
    )
    resp = engine.ask(req)

    # All claims must have at least one valid supporting evidence ID
    assert len(resp.answer.claims) > 0
    for claim in resp.answer.claims:
        assert len(claim.supporting_evidence_ids) > 0
        assert claim.epistemic_tier in ("OBSERVED", "FUSED", "INFERRED", "PREDICTED", "UNCERTAIN")

    # Epistemic ledger contains evidence across tiers
    ledger = resp.answer.evidence_ledger
    assert ledger.total_evidence_count > 0


def test_forecast_claims_tagged_predicted():
    repo = EntityRepository(default_config.entity)
    seed_entity_repository(repo)
    engine = AskNetraEngine(config=default_config, repository=repo)

    req = AskNetraRequest(
        query="What will ENTITY-01 do next?",
        as_of=datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc),
    )
    resp = engine.ask(req)

    # Forecast claims should be tagged PREDICTED or UNCERTAIN
    for claim in resp.answer.claims:
        assert claim.epistemic_tier in ("PREDICTED", "UNCERTAIN")
