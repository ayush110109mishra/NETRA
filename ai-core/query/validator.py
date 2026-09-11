"""
Phase 7 Query Validator for Ask NETRA.
Validates operator queries for entity existence, semantic ambiguity, out-of-scope requests, and valid time bounds.
"""

import re
from typing import List, Optional, Set
from models.ask_netra import ParsedQuery, QueryIntent, QueryValidationStatus


# Disallowed or out-of-scope operational triggers
UNSUPPORTED_PATTERNS = [
    re.compile(r"\b(fire|shoot|launch weapon|strike|engage target|authorize missile|kill chain)\b", re.I),
    re.compile(r"\b(weather forecast for tomorrow|buy stocks|crypto|translate to spanish)\b", re.I),
    re.compile(r"\b(hack|exploit|bypass security)\b", re.I),
]


class QueryValidator:
    """Deterministic validator enforcing operational constraints and data sanity."""

    def __init__(self, known_entity_ids: Optional[Set[str]] = None):
        self.known_entity_ids = known_entity_ids or set()

    def update_known_entities(self, entity_ids: Set[str]) -> None:
        """Refreshes the set of known registered entity identifiers."""
        self.known_entity_ids = set(entity_ids)

    def validate(self, parsed: ParsedQuery) -> (QueryValidationStatus, Optional[str]):
        """
        Validates the parsed query object.
        Returns:
            (QueryValidationStatus, validation_message)
        """
        # 1. Check out-of-scope / unsupported operational requests
        for pat in UNSUPPORTED_PATTERNS:
            if pat.search(parsed.raw_query):
                return (
                    QueryValidationStatus.UNSUPPORTED_QUERY,
                    "Query falls outside NETRA intelligence scope (e.g. autonomous engagement or general assistant actions).",
                )

        # 2. Check Entity Existence
        if parsed.primary_entity_id and self.known_entity_ids:
            if parsed.primary_entity_id not in self.known_entity_ids:
                return (
                    QueryValidationStatus.ENTITY_NOT_FOUND,
                    f"Entity '{parsed.primary_entity_id}' is not recognized in the current operational registry.",
                )

        if parsed.secondary_entity_id and self.known_entity_ids:
            if parsed.secondary_entity_id not in self.known_entity_ids:
                return (
                    QueryValidationStatus.ENTITY_NOT_FOUND,
                    f"Secondary entity '{parsed.secondary_entity_id}' is not recognized in the current operational registry.",
                )

        # 3. Check Ambiguity: pronoun reference without resolved entity
        if parsed.is_followup and not parsed.primary_entity_id:
            return (
                QueryValidationStatus.AMBIGUOUS_QUERY,
                "Query contains reference pronoun ('it' / 'the entity') but no active entity context is established.",
            )

        # 4. Check Comparison Intent requires two entities or comparative context
        if parsed.intent == QueryIntent.COMPARISON and not parsed.primary_entity_id:
            return (
                QueryValidationStatus.AMBIGUOUS_QUERY,
                "Comparison queries require explicit entities or prior session focus.",
            )

        # 5. Check Time Window Validity
        if parsed.time_range and parsed.time_range.start_time and parsed.time_range.end_time:
            if parsed.time_range.start_time > parsed.time_range.end_time:
                return (
                    QueryValidationStatus.TIME_WINDOW_INVALID,
                    "Temporal filter start time cannot be after end time.",
                )

        return QueryValidationStatus.VALID, None
