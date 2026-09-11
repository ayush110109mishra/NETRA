"""
Phase 7 Entity and Identifier Extractor for Ask NETRA.
Extracts canonical entity IDs, sensor IDs, sector IDs, aliases, and pronoun references.
"""

import re
from typing import Dict, List, Optional, Tuple


# Regex patterns for canonical IDs
ENTITY_REGEX = re.compile(r"\b(ENTITY[_-][A-Za-z0-9]+|ENT[_-][A-Za-z0-9]+|TRACK[_-][A-Za-z0-9]+|TGT[_-][A-Za-z0-9]+|UAV[_-][A-Za-z0-9]+|VESSEL[_-][A-Za-z0-9]+)\b", re.I)
SOURCE_REGEX = re.compile(r"\b(RADAR[_-][A-Za-z0-9]+|OPTICAL[_-][A-Za-z0-9]+|SIGINT[_-][A-Za-z0-9]+|HUMINT[_-][A-Za-z0-9]+|AIS[_-][A-Za-z0-9]+)\b", re.I)
SECTOR_REGEX = re.compile(r"\b(SECTOR[_-][A-Za-z0-9]+|ZONE[_-][A-Za-z0-9]+|GRID[_-][A-Za-z0-9]+|BORDER[_-][A-Za-z0-9]+)\b", re.I)
PRONOUN_REGEX = re.compile(r"\b(it|its|this entity|that entity|the entity|the track|this track|the target|this target)\b", re.I)

# Common numeric alias patterns like "target 1", "entity 2"
TARGET_NUMERIC_REGEX = re.compile(r"\b(entity|target|track)\s+(\d+)\b", re.I)


class EntityExtractor:
    """Extracts entity IDs, sensor sources, operational sectors, and reference pronouns."""

    def __init__(self, alias_map: Optional[Dict[str, str]] = None):
        self.alias_map = alias_map or {}

    def extract_entities(
        self, text: str, session_entity_id: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str], bool, Dict[str, str]]:
        """
        Extracts primary and secondary entities from text.
        Returns:
            primary_entity_id, secondary_entity_id, is_pronoun_reference, resolved_references
        """
        resolved: Dict[str, str] = {}
        entities_found: List[str] = []

        # 1. Canonical IDs
        for match in ENTITY_REGEX.finditer(text):
            canonical = match.group(1).upper().replace("_", "-")
            if canonical not in entities_found:
                entities_found.append(canonical)

        # 2. Numeric aliases like "entity 1" -> "ENTITY-01"
        for match in TARGET_NUMERIC_REGEX.finditer(text):
            num = match.group(2).zfill(2)
            normalized = f"ENTITY-{num}"
            if normalized not in entities_found:
                entities_found.append(normalized)
                resolved[match.group(0)] = normalized

        # 3. Known aliases
        for alias, target_id in self.alias_map.items():
            if re.search(r"\b" + re.escape(alias) + r"\b", text, re.I):
                if target_id not in entities_found:
                    entities_found.append(target_id)
                    resolved[alias] = target_id

        # 4. Pronoun resolution
        is_pronoun = False
        primary: Optional[str] = None
        secondary: Optional[str] = None

        if len(entities_found) >= 2:
            primary = entities_found[0]
            secondary = entities_found[1]
        elif len(entities_found) == 1:
            primary = entities_found[0]
            # If there's also a pronoun and a session entity, might be secondary
            if PRONOUN_REGEX.search(text) and session_entity_id and session_entity_id != primary:
                secondary = session_entity_id
                resolved["session_context"] = session_entity_id
        else:
            # No explicit entity found: check pronouns
            if PRONOUN_REGEX.search(text):
                is_pronoun = True
                if session_entity_id:
                    primary = session_entity_id
                    resolved["pronoun_target"] = session_entity_id

        return primary, secondary, is_pronoun, resolved

    def extract_sector(self, text: str) -> Optional[str]:
        """Extracts sector or zone identifier."""
        match = SECTOR_REGEX.search(text)
        if match:
            return match.group(1).upper().replace("_", "-")
        return None

    def extract_source(self, text: str) -> Optional[str]:
        """Extracts sensor source identifier."""
        match = SOURCE_REGEX.search(text)
        if match:
            return match.group(1).upper().replace("_", "-")
        return None
