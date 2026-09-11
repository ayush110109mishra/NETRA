"""
Test suite for NETRA Phase 5 Entity Resolution.
"""

import pytest

from fusion.normalization import SourceNormalizer
from fusion.entity_resolution import EntityResolver
from models.fusion_intelligence import EntityResolutionStatus


def test_direct_canonical_id_resolution():
    obs = SourceNormalizer.normalize_observation({
        "source_id": "TELEMETRY_01",
        "entity_id": "ENTITY-07",
    })
    resolver = EntityResolver()
    res = resolver.resolve(obs)
    assert res.status == EntityResolutionStatus.RESOLVED
    assert res.resolved_entity_id == "ENTITY-07"
    assert res.match_confidence >= 0.95


def test_known_synthetic_alias_resolution():
    resolver = EntityResolver()

    # R-104 -> ENTITY-07
    obs1 = SourceNormalizer.normalize_observation({"source_id": "RADAR_01", "track_id": "R-104"})
    res1 = resolver.resolve(obs1)
    assert res1.status == EntityResolutionStatus.RESOLVED
    assert res1.resolved_entity_id == "ENTITY-07"
    assert res1.match_confidence >= 0.90

    # O-771 -> ENTITY-07
    obs2 = SourceNormalizer.normalize_observation({"source_id": "OPTICAL_01", "object_id": "O-771"})
    res2 = resolver.resolve(obs2)
    assert res2.status == EntityResolutionStatus.RESOLVED
    assert res2.resolved_entity_id == "ENTITY-07"

    # T-22 -> ENTITY-07
    obs3 = SourceNormalizer.normalize_observation({"source_id": "TELEMETRY_01", "entity_hint": "T-22"})
    res3 = resolver.resolve(obs3)
    assert res3.status == EntityResolutionStatus.RESOLVED
    assert res3.resolved_entity_id == "ENTITY-07"


def test_unresolvable_unknown_hint():
    obs = SourceNormalizer.normalize_observation({
        "source_id": "RADAR_01",
        "track_id": "UNKNOWN_BOGEY_XYZ_999",
    })
    resolver = EntityResolver()
    res = resolver.resolve(obs)
    assert res.status == EntityResolutionStatus.UNRESOLVED
    assert res.resolved_entity_id == "ENTITY_UNRESOLVED"
    assert res.match_confidence <= 0.35
