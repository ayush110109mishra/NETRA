"""
Test suite for NETRA Phase 5 Evidence Fusion and Scoring.
"""

from datetime import datetime, timezone
import pytest

from fusion.normalization import SourceNormalizer
from fusion.corroboration import CorroborationEngine
from fusion.entity_resolution import EntityResolver
from fusion.fusion import EvidenceFuser
from fusion.evidence import EvidenceLedger


def test_weighted_fusion_agreement_and_confidence():
    t0 = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    obs1 = SourceNormalizer.normalize_observation({
        "source_id": "RADAR_01",
        "latitude": 34.0500,
        "longitude": 74.8000,
        "speed_kmh": 60.0,
        "heading_deg": 90.0,
        "event_type": "CONVOY",
        "entity_hint": "ENTITY-07",
        "timestamp": t0,
    })
    obs2 = SourceNormalizer.normalize_observation({
        "source_id": "OPTICAL_01",
        "latitude": 34.0502,
        "longitude": 74.8001,
        "speed_kmh": 59.8,
        "heading_deg": 90.0,
        "event_type": "CONVOY",
        "entity_hint": "ENTITY-07",
        "timestamp": t0,
    })

    resolver = EntityResolver()
    res = resolver.resolve(obs1)

    corrob_engine = CorroborationEngine()
    corrob = corrob_engine.evaluate([obs1, obs2])

    ledger = EvidenceLedger()
    ev_record = ledger.create_evidence_record([obs1, obs2], derived_from=["ENTITY-07"])

    fuser = EvidenceFuser()
    fused = fuser.fuse(
        observations=[obs1, obs2],
        entity_resolution=res,
        corroboration=corrob,
        conflicts=[],
        evidence_quality=ev_record.evidence_quality,
    )

    assert fused.fused_observation_id.startswith("FO-")
    assert fused.entity_id == "ENTITY-07"
    assert 0.0 <= fused.agreement_score <= 1.0
    assert fused.agreement_score >= 0.85
    assert 0.0 <= fused.fusion_confidence <= 1.0
    assert fused.fusion_confidence >= 0.85
    assert fused.independent_source_count == 2
    assert fused.fused_position is not None
    assert 34.049 <= fused.fused_position.latitude <= 34.051
    assert 74.799 <= fused.fused_position.longitude <= 74.801
    assert fused.fused_velocity is not None
    assert 59.5 <= fused.fused_velocity.speed_kmh <= 60.5
    assert fused.fused_event_type == "CONVOY"


def test_cold_start_confidence_cap():
    # When observing from unverified cold-start source
    t0 = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    obs = [
        SourceNormalizer.normalize_observation({
            "source_id": "NEW_UNREGISTERED_SENSOR",
            "latitude": 34.0500,
            "longitude": 74.8000,
            "timestamp": t0,
        })
    ]
    resolver = EntityResolver()
    res = resolver.resolve(obs[0])
    corrob = CorroborationEngine().evaluate(obs)
    ledger = EvidenceLedger()
    ev_record = ledger.create_evidence_record(obs)

    fuser = EvidenceFuser()
    fused = fuser.fuse(
        observations=obs,
        entity_resolution=res,
        corroboration=corrob,
        conflicts=[],
        evidence_quality=ev_record.evidence_quality,
    )

    # Cold start cap must ensure confidence <= 0.35
    assert fused.fusion_confidence <= 0.35
