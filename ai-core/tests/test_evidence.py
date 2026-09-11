"""
Test suite for NETRA Phase 5 Evidence Ledger and Quality Assessment.
"""

import pytest

from fusion.normalization import SourceNormalizer
from fusion.evidence import EvidenceLedger


def test_evidence_quality_and_lineage():
    obs1 = SourceNormalizer.normalize_observation({
        "source_id": "RADAR_01",
        "latitude": 34.0500,
        "longitude": 74.8000,
        "speed_kmh": 60.0,
        "event_type": "MOVEMENT",
        "entity_hint": "ENTITY-07",
    })
    obs2 = SourceNormalizer.normalize_observation({
        "source_id": "OPTICAL_01",
        "latitude": 34.0502,
        "longitude": 74.8001,
        "speed_kmh": 59.8,
        "event_type": "MOVEMENT",
        "entity_hint": "ENTITY-07",
    })

    ledger = EvidenceLedger()
    record = ledger.create_evidence_record([obs1, obs2], derived_from=["ENTITY-07"])
    assert record.evidence_id.startswith("EV-")
    assert len(record.source_observations) == 2
    assert 0.0 <= record.evidence_quality <= 1.0
    assert record.evidence_quality >= 0.80
    assert len(record.lineage_path) >= 5


def test_evidence_quality_penalized_by_conflict():
    obs = [
        SourceNormalizer.normalize_observation({"source_id": "RADAR_01", "latitude": 34.0, "longitude": 74.0}),
        SourceNormalizer.normalize_observation({"source_id": "SENSOR_B", "latitude": 34.5, "longitude": 75.0}),
    ]
    ledger = EvidenceLedger()
    qual_no_conflict = ledger.calculate_evidence_quality(obs, conflicts=[])

    # With high conflict
    from models.fusion_intelligence import ConflictRecord, ConflictType, ConflictStatus
    fake_conflict = ConflictRecord(
        conflict_id="CONF-1",
        conflict_type=ConflictType.POSITION,
        severity=0.90,
        sources=["RADAR_01", "SENSOR_B"],
        observation_ids=["O1", "O2"],
        status=ConflictStatus.UNRESOLVED,
        explanation="Severe divergence",
    )
    qual_with_conflict = ledger.calculate_evidence_quality(obs, conflicts=[fake_conflict])
    assert qual_with_conflict < qual_no_conflict
