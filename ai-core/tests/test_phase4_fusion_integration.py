"""
Test suite for NETRA Phase 5 Integration with Phase 4 Anomaly & Risk Intelligence.
"""

from datetime import datetime, timezone
import pytest

from config import default_config
from entities.repository import EntityRepository
from intelligence.anomaly_intelligence import AnomalyIntelligenceEngine
from intelligence.fusion_intelligence import FusionIntelligenceEngine
from models.fusion_intelligence import FusionAnalyzeRequest
from simulation.synthetic_data import seed_entity_repository


def test_fusion_to_phase4_anomaly_pipeline():
    repo = EntityRepository(default_config.entity)
    seed_entity_repository(repo)

    engine = FusionIntelligenceEngine(config=default_config, repository=repo)

    # 3 sensors reporting on ENTITY-07
    req = FusionAnalyzeRequest(
        observations=[
            {
                "source_id": "RADAR_01",
                "track_id": "R-104",
                "lat": 34.0500,
                "lon": 74.8000,
                "speed": 60.0,
                "time": "2026-09-12T12:00:00Z",
            },
            {
                "source_id": "OPTICAL_01",
                "object_id": "O-771",
                "lat": 34.0502,
                "lon": 74.8001,
                "speed": 59.8,
                "time": "2026-09-12T12:00:01Z",
            },
        ],
        target_entity_id="ENTITY-07",
        enable_phase4_integration=True,
    )

    res = engine.analyze_fusion(req)
    assert res.status == "SUCCESS"
    assert len(res.fused_observations) == 1
    assert res.fused_observations[0].entity_id == "ENTITY-07"

    # Verify Phase 4 Anomaly Assessment is populated
    assert res.phase4_anomaly_assessment is not None
    phase4 = res.phase4_anomaly_assessment
    assert "anomaly" in phase4
    assert "attribution" in phase4
    assert "risk" in phase4
    assert "assessment" in phase4



    # Epistemic assessment
    assert len(res.assessment.observed) >= 2
    assert len(res.assessment.fused) >= 1
    assert len(res.assessment.inferred) >= 1
