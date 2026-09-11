"""
Phase 7 Master Query Interpretation Engine for Ask NETRA.
Coordinates intent classification, entity extraction, time parsing, filtering, validation, and planning.
"""

from datetime import datetime, timezone
import hashlib
from typing import Dict, Optional, Set, Tuple

from config import NetraConfig, default_config
from models.ask_netra import (
    ParsedQuery,
    QueryPlan,
    QueryValidationStatus,
)
from query.intent import IntentClassifier
from query.entity_extractor import EntityExtractor
from query.time_parser import TimeParser
from query.filters import FilterExtractor
from query.validator import QueryValidator
from query.planner import QueryPlanner


class QueryInterpretationEngine:
    """Orchestrates natural language parsing and converts operator queries into validated execution plans."""

    def __init__(
        self,
        config: Optional[NetraConfig] = None,
        known_entity_ids: Optional[Set[str]] = None,
        alias_map: Optional[Dict[str, str]] = None,
    ):
        self.config = config or default_config
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor(alias_map=alias_map)
        self.time_parser = TimeParser()
        self.filter_extractor = FilterExtractor()
        self.validator = QueryValidator(known_entity_ids=known_entity_ids)
        self.planner = QueryPlanner()

    def update_known_entities(self, entity_ids: Set[str]) -> None:
        """Synchronizes known entity IDs with the validator."""
        self.validator.update_known_entities(entity_ids)

    def interpret(
        self,
        query_text: str,
        session_entity_id: Optional[str] = None,
        as_of: Optional[datetime] = None,
    ) -> Tuple[ParsedQuery, QueryPlan, QueryValidationStatus, Optional[str]]:
        """
        Interprets natural language query string into a structured ParsedQuery and QueryPlan.
        Returns:
            (parsed_query, execution_plan, validation_status, validation_message)
        """
        ref_time = as_of or datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
        if ref_time.tzinfo is None:
            ref_time = ref_time.replace(tzinfo=timezone.utc)

        # 1. Deterministic query ID hash
        q_hash = hashlib.sha256((query_text.strip() + ref_time.isoformat()).encode()).hexdigest()[:10]
        query_id = f"QRY-{q_hash}"

        # 2. Intent Classification
        intent, intent_conf = self.intent_classifier.classify(query_text)

        # 3. Entity and Sector Extraction
        primary_id, secondary_id, is_pronoun, resolved_refs = self.entity_extractor.extract_entities(
            query_text, session_entity_id=session_entity_id
        )
        sector_id = self.entity_extractor.extract_sector(query_text)

        # 4. Temporal Parsing
        time_range = self.time_parser.parse(query_text, as_of=ref_time)

        # 5. Filter Extraction
        filters = self.filter_extractor.extract(query_text)

        # 6. Build ParsedQuery
        parsed = ParsedQuery(
            query_id=query_id,
            raw_query=query_text,
            intent=intent,
            intent_confidence=intent_conf,
            primary_entity_id=primary_id,
            secondary_entity_id=secondary_id,
            sector_id=sector_id,
            time_range=time_range,
            filters=filters,
            is_followup=is_pronoun or (bool(session_entity_id) and primary_id == session_entity_id),
            resolved_references=resolved_refs,
            parsed_at=ref_time,
        )

        # 7. Validation
        val_status, val_msg = self.validator.validate(parsed)

        # 8. Planning
        plan = self.planner.plan(parsed)
        plan.validation_status = val_status
        plan.validation_message = val_msg

        return parsed, plan, val_status, val_msg
