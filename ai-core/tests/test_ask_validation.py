"""
Unit tests for Ask NETRA query validation and safety policy gating.
"""

from datetime import datetime, timezone
from models.ask_netra import ParsedQuery, QueryIntent, QueryValidationStatus, StructuredFilters
from query.validator import QueryValidator


def test_validator_rejects_unregistered_entity():
    validator = QueryValidator(known_entity_ids={"ENTITY-01", "ENTITY-02"})
    parsed = ParsedQuery(
        query_id="QRY-VAL-01",
        raw_query="What is the risk of ENTITY-999?",
        intent=QueryIntent.RISK,
        intent_confidence=0.90,
        primary_entity_id="ENTITY-999",
        filters=StructuredFilters(),
        parsed_at=datetime.now(timezone.utc),
    )
    status, msg = validator.validate(parsed)
    assert status == QueryValidationStatus.ENTITY_NOT_FOUND
    assert "ENTITY-999" in msg


def test_validator_rejects_ambiguous_pronoun_without_context():
    validator = QueryValidator(known_entity_ids={"ENTITY-01"})
    parsed = ParsedQuery(
        query_id="QRY-VAL-02",
        raw_query="Why did it move?",
        intent=QueryIntent.WHY,
        intent_confidence=0.90,
        primary_entity_id=None,
        is_followup=True,
        filters=StructuredFilters(),
        parsed_at=datetime.now(timezone.utc),
    )
    status, msg = validator.validate(parsed)
    assert status == QueryValidationStatus.AMBIGUOUS_QUERY


def test_validator_rejects_kinetic_targeting():
    validator = QueryValidator(known_entity_ids={"ENTITY-01"})
    parsed = ParsedQuery(
        query_id="QRY-VAL-03",
        raw_query="Authorize missile strike on ENTITY-01",
        intent=QueryIntent.STATUS,
        intent_confidence=0.90,
        primary_entity_id="ENTITY-01",
        filters=StructuredFilters(),
        parsed_at=datetime.now(timezone.utc),
    )
    status, msg = validator.validate(parsed)
    assert status == QueryValidationStatus.UNSUPPORTED_QUERY


def test_validator_accepts_valid_query():
    validator = QueryValidator(known_entity_ids={"ENTITY-01"})
    parsed = ParsedQuery(
        query_id="QRY-VAL-04",
        raw_query="What is the risk level of ENTITY-01?",
        intent=QueryIntent.RISK,
        intent_confidence=0.90,
        primary_entity_id="ENTITY-01",
        filters=StructuredFilters(),
        parsed_at=datetime.now(timezone.utc),
    )
    status, msg = validator.validate(parsed)
    assert status == QueryValidationStatus.VALID
    assert msg is None
