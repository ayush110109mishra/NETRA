"""
Test suite for NETRA Phase 5 Cross-Source Corroboration and Independence.
"""

from datetime import datetime, timezone
import pytest

from fusion.normalization import SourceNormalizer
from fusion.corroboration import CorroborationEngine
from fusion.source_registry import SourceRegistry


def test_single_source_baseline():
    obs = [
        SourceNormalizer.normalize_observation({"source_id": "RADAR_01", "entity_id": "ENTITY-07"}),
    ]
    engine = CorroborationEngine()
    res = engine.evaluate(obs)
    assert res.independent_source_count == 1
    assert res.duplicate_source_count == 0
    assert res.corroboration_score == 0.35


def test_duplicate_retransmission_no_inflation():
    # RADAR_01 and RADAR_01_DUP share the independence group RADAR_ALPHA
    obs = [
        SourceNormalizer.normalize_observation({"source_id": "RADAR_01", "entity_id": "ENTITY-07"}),
        SourceNormalizer.normalize_observation({"source_id": "RADAR_01_DUP", "entity_id": "ENTITY-07"}),
    ]
    engine = CorroborationEngine()
    res = engine.evaluate(obs)
    assert res.independent_source_count == 1
    assert res.duplicate_source_count == 1
    # Crucial assertion: Corroboration score must NOT inflate to 0.70 because they share the same independence group
    assert res.corroboration_score == 0.35
    assert "RADAR_ALPHA" in res.independence_groups


def test_dual_independent_sources():
    # RADAR_01 (RADAR_ALPHA) + OPTICAL_01 (OPTICAL_BRAVO)
    obs = [
        SourceNormalizer.normalize_observation({"source_id": "RADAR_01", "entity_id": "ENTITY-07"}),
        SourceNormalizer.normalize_observation({"source_id": "OPTICAL_01", "entity_id": "ENTITY-07"}),
    ]
    engine = CorroborationEngine()
    res = engine.evaluate(obs)
    assert res.independent_source_count == 2
    assert res.duplicate_source_count == 0
    assert res.corroboration_score == 0.70


def test_three_independent_sources_robust_corroboration():
    # RADAR_01 + OPTICAL_01 + TELEMETRY_01
    obs = [
        SourceNormalizer.normalize_observation({"source_id": "RADAR_01", "entity_id": "ENTITY-07"}),
        SourceNormalizer.normalize_observation({"source_id": "OPTICAL_01", "entity_id": "ENTITY-07"}),
        SourceNormalizer.normalize_observation({"source_id": "TELEMETRY_01", "entity_id": "ENTITY-07"}),
    ]
    engine = CorroborationEngine()
    res = engine.evaluate(obs)
    assert res.independent_source_count == 3
    assert res.corroboration_score >= 0.85
