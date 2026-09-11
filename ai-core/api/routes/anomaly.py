"""
Phase 4 Anomaly and Risk Intelligence API Routes for NETRA.
Provides endpoints for multi-dimensional anomaly detection, mathematical attribution,
persistence tracking, phase4-v1 risk history, sector anomaly index, hotspots, and scenarios.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status

from config import NetraConfig
from api.dependencies import get_config, get_anomaly_engine
from models.anomaly_intelligence import (
    AnomalyAnalyzeRequest,
    AnomalyAnalyzeResponse,
    AnomalyHistoryResponse,
    SectorAnomalyHeatIndex,
    AnomalyHotspot,
)
from models.risk_intelligence import RiskHistoryResponse
from intelligence.anomaly_intelligence import AnomalyIntelligenceEngine
from simulation.synthetic_data import (
    get_all_anomaly_scenarios,
    get_anomaly_scenario,
)

logger = logging.getLogger("netra.api.anomaly")

router = APIRouter(prefix="/api/v1/intelligence", tags=["Anomaly & Risk Intelligence"])


@router.post(
    "/anomalies/analyze",
    response_model=AnomalyAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Multi-Dimensional Anomaly & Risk Analysis",
    description=(
        "Core Phase 4 endpoint: Analyzes entity telemetry across 8 dimensions (temporal, spatial, "
        "kinematic, frequency, event_type, behavioral, relational, contextual). Provides mathematically "
        "consistent attribution, persistence state, rate of change trend, calibrated confidence, and "
        "phase4-v1 explainable risk profile."
    ),
)
def analyze_anomaly(
    request: AnomalyAnalyzeRequest,
    engine: AnomalyIntelligenceEngine = Depends(get_anomaly_engine),
) -> AnomalyAnalyzeResponse:
    try:
        return engine.analyze_entity_anomaly(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error(f"Anomaly analysis failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anomaly processing error: {str(exc)}",
        )


@router.get(
    "/entities/{entity_id}/anomalies",
    response_model=AnomalyHistoryResponse,
    summary="Entity Anomaly Timeline & History",
    description="Retrieves chronological point-in-time anomaly score records and dimension drivers for an entity.",
)
def get_entity_anomalies(
    entity_id: str,
    limit: int = Query(default=50, ge=1, le=200, description="Max history records to return"),
    engine: AnomalyIntelligenceEngine = Depends(get_anomaly_engine),
) -> AnomalyHistoryResponse:
    try:
        return engine.get_entity_anomalies_history(entity_id=entity_id, limit=limit)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/entities/{entity_id}/risk-history",
    response_model=RiskHistoryResponse,
    summary="Entity Risk Timeline (phase4-v1)",
    description="Retrieves chronological point-in-time analytical risk scores, states, and confidence for timeline graphing.",
)
def get_entity_risk_history(
    entity_id: str,
    limit: int = Query(default=50, ge=1, le=200, description="Max history records to return"),
    engine: AnomalyIntelligenceEngine = Depends(get_anomaly_engine),
) -> RiskHistoryResponse:
    try:
        return engine.get_entity_risk_history(entity_id=entity_id, limit=limit)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/sectors/{sector_id}/anomaly-index",
    response_model=SectorAnomalyHeatIndex,
    summary="Sector Anomaly Heat Index",
    description="Calculates aggregate anomaly heat index across all entities operating within an operational sector.",
)
def get_sector_anomaly_index(
    sector_id: str,
    engine: AnomalyIntelligenceEngine = Depends(get_anomaly_engine),
) -> SectorAnomalyHeatIndex:
    return engine.get_sector_anomaly_index(sector_id=sector_id)


@router.get(
    "/anomalies/hotspots",
    response_model=List[AnomalyHotspot],
    summary="Geospatial Anomaly Hotspots",
    description="Identifies and clusters geospatial concentrations of elevated anomaly activity across operating domains.",
)
def get_anomaly_hotspots(
    min_score: float = Query(default=0.50, ge=0.0, le=1.0, description="Minimum anomaly intensity threshold"),
    engine: AnomalyIntelligenceEngine = Depends(get_anomaly_engine),
) -> List[AnomalyHotspot]:
    return engine.get_anomaly_hotspots(min_score=min_score)


@router.get(
    "/anomalies/scenarios",
    summary="List Phase 4 Anomaly Operational Scenarios",
    description="Returns catalogue of 14 predefined operational scenarios covering all anomaly dimensions and edge cases.",
)
def list_anomaly_scenarios() -> Dict[str, Any]:
    scenarios = get_all_anomaly_scenarios()
    return {
        "count": len(scenarios),
        "data_classification": "SYNTHETIC",
        "scenarios": scenarios,
    }


@router.post(
    "/anomalies/scenarios/{scenario_id}/analyze",
    response_model=AnomalyAnalyzeResponse,
    summary="Execute Predefined Phase 4 Operational Scenario",
    description="Executes a predefined anomaly scenario by identifier and returns full Phase 4 assessment.",
)
def run_anomaly_scenario(
    scenario_id: str,
    engine: AnomalyIntelligenceEngine = Depends(get_anomaly_engine),
) -> AnomalyAnalyzeResponse:
    scen = get_anomaly_scenario(scenario_id.lower())
    if not scen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anomaly scenario '{scenario_id}' not found. Check GET /api/v1/intelligence/anomalies/scenarios.",
        )

    req = AnomalyAnalyzeRequest(
        entity_id=scen["entity_id"],
        events=[e.model_dump() for e in scen["events"]],
        context=scen.get("context"),
    )
    return engine.analyze_entity_anomaly(req)
