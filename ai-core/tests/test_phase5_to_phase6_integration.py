"""
Integration test for NETRA Phase 5 Multi-Source Fusion to Phase 6 Predictive Intelligence.
Validates end-to-end evidence lineage from multi-sensor feeds through fusion,
anomaly scoring, and probabilistic future-state projection.
"""

from datetime import datetime, timezone, timedelta
import pytest

from config import default_config
from entities.repository import EntityRepository
from intelligence.anomaly_intelligence import AnomalyIntelligenceEngine
from intelligence.fusion_intelligence import FusionIntelligenceEngine
from intelligence.predictive_intelligence import PredictiveIntelligenceEngine
from models.fusion_intelligence import FusionAnalyzeRequest
from models.predictive_intelligence import (
    ForecastHorizon,
    PredictionAnalyzeRequest,
    PredictiveTarget,
)
from simulation.synthetic_data import seed_entity_repository


@pytest.fixture
def intelligence_stack():
    repo = EntityRepository(default_config.entity)
    seed_entity_repository(repo)
    anomaly_engine = AnomalyIntelligenceEngine(default_config, repository=repo)
    fusion_engine = FusionIntelligenceEngine(default_config, repository=repo, anomaly_engine=anomaly_engine)
    pred_engine = PredictiveIntelligenceEngine(
        default_config,
        repository=repo,
        anomaly_engine=anomaly_engine,
        fusion_engine=fusion_engine,
    )
    return repo, fusion_engine, anomaly_engine, pred_engine


def test_fusion_to_prediction_pipeline(intelligence_stack):
    repo, fusion_engine, anomaly_engine, pred_engine = intelligence_stack
    t0 = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)

    # 1. Ingest multi-source observations into Fusion Engine
    obs = [
        {
            "source_id": "RADAR_01",
            "source_type": "RADAR",
            "timestamp": t0,
            "entity_hint": "ENTITY-07",
            "position": {"latitude": 34.0500, "longitude": 74.8000, "sector_id": "SECTOR_ALPHA"},
            "velocity": {"speed_kmh": 60.0, "heading_deg": 90.0},
            "event_type": "CONVOY_MOVEMENT",
            "quality": 0.95,
        },
        {
            "source_id": "OPTICAL_01",
            "source_type": "OPTICAL",
            "timestamp": t0 + timedelta(seconds=2),
            "entity_hint": "ENTITY-07",
            "position": {"latitude": 34.0502, "longitude": 74.8003, "sector_id": "SECTOR_ALPHA"},
            "velocity": {"speed_kmh": 59.5, "heading_deg": 91.0},
            "event_type": "CONVOY_MOVEMENT",
            "quality": 0.92,
        },
    ]

    fusion_req = FusionAnalyzeRequest(
        observations=obs,
        target_entity_id="ENTITY-07",
        enable_phase4_integration=True,
    )
    fusion_resp = fusion_engine.analyze_fusion(fusion_req)
    assert len(fusion_resp.fused_observations) > 0

    # 2. Trigger Predictive Intelligence Analysis on ENTITY-07
    pred_req = PredictionAnalyzeRequest(
        entity_id="ENTITY-07",
        target=PredictiveTarget.ACTIVITY_STATE,
        horizon=ForecastHorizon.SHORT,
        as_of=t0 + timedelta(minutes=5),
        include_phase5_fusion=True,
    )
    pred_resp = pred_engine.analyze_prediction(pred_req)

    assert pred_resp.status == "SUCCESS"
    assert pred_resp.entity_id == "ENTITY-07"
    assert pred_resp.forecast is not None
    assert pred_resp.provenance["fused_sources_active"] >= 1
    assert "FUSED" in pred_resp.assessment.epistemic_ledger
