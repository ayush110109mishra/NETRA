"""
Unit tests for Ask NETRA entity, sector, sensor, and pronoun reference extraction.
"""

from query.entity_extractor import EntityExtractor


def test_canonical_entity_extraction():
    extractor = EntityExtractor()
    text = "What is the status of ENTITY-01?"
    primary, secondary, is_pronoun, resolved = extractor.extract_entities(text)
    assert primary == "ENTITY-01"
    assert secondary is None
    assert not is_pronoun


def test_dual_entity_extraction_for_comparison():
    extractor = EntityExtractor()
    text = "Compare ENTITY-01 to ENTITY-02 across all dimensions"
    primary, secondary, is_pronoun, resolved = extractor.extract_entities(text)
    assert primary == "ENTITY-01"
    assert secondary == "ENTITY-02"


def test_numeric_alias_extraction():
    extractor = EntityExtractor()
    text = "Assess risk for target 3"
    primary, secondary, is_pronoun, resolved = extractor.extract_entities(text)
    assert primary == "ENTITY-03"


def test_pronoun_reference_with_session():
    extractor = EntityExtractor()
    text = "Why is its risk so high?"
    primary, secondary, is_pronoun, resolved = extractor.extract_entities(text, session_entity_id="ENTITY-05")
    assert is_pronoun is True
    assert primary == "ENTITY-05"


def test_sector_and_source_extraction():
    extractor = EntityExtractor()
    text = "Identify threats in SECTOR-ALPHA detected by RADAR-01"
    sector = extractor.extract_sector(text)
    source = extractor.extract_source(text)
    assert sector == "SECTOR-ALPHA"
    assert source == "RADAR-01"
