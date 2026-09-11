"""
Intelligence analysis and scenario testing endpoints for NETRA.
Provides both Phase 1 single-event and Phase 2 multi-event intelligence routes.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime

from config import NetraConfig
from api.dependencies import get_config, get_entity_engine
from models.common import EntityStatus, SeverityLevel
from models.input import IntelligenceAnalyzeRequest
from models.output import IntelligenceAnalyzeResponse
from models.event_intelligence import (
    MultiEventAnalyzeRequest,
    MultiEventAnalyzeResponse,
)
from models.entity_intelligence import (
    EntityIntelligenceResponse,
    EntityCompareRequest,
    EntityCompareResponse,
    EntitySearchResponse,
    EntityTimelineItem,
    EntityRelationshipEdge,
)
from intelligence.engine import analyze_intelligence
from intelligence.event_intelligence import EventIntelligenceEngine
from intelligence.entity_intelligence import EntityIntelligenceEngine
from simulation.synthetic_data import (
    get_synthetic_scenario,
    get_all_synthetic_scenarios,
    get_multi_scenario,
    get_all_multi_scenarios,
    get_all_entity_scenarios,
    ENTITY_SCENARIOS_MAP,
)

logger = logging.getLogger("netra.api.intelligence")
router = APIRouter(prefix="/api/v1/intelligence", tags=["Intelligence Core"])


# ==============================================================================
# PHASE 1 SINGLE-EVENT ENDPOINTS (100% PRESERVED & COMPATIBLE)
# ==============================================================================

@router.post(
    "/analyze",
    response_model=IntelligenceAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Synthetic Operational Data (Single Event)",
    description="Transforms structured synthetic operational telemetry into a deterministic, explainable intelligence assessment.",
)
def analyze_telemetry(
    request: IntelligenceAnalyzeRequest,
    config: NetraConfig = Depends(get_config),
) -> IntelligenceAnalyzeResponse:
    """
    Primary Phase 1 intelligence pipeline entry point.
    Returns classification, severity, risk breakdown, confidence, correlations, and narrative assessment.
    """
    logger.info(
        f"Processing intelligence analysis for event '{request.event.event_id}', "
        f"entity '{request.entity.entity_id}'"
    )
    try:
        response = analyze_intelligence(request=request, config=config)
        logger.info(
            f"Analysis completed: ID={response.analysis_id}, "
            f"classification={response.classification.value}, risk={response.risk.score}"
        )
        return response
    except Exception as exc:
        logger.error(f"Intelligence analysis failure: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during deterministic intelligence processing.",
        )


@router.get(
    "/scenarios",
    summary="List Available Single-Event Synthetic Scenarios",
    description="Returns catalogue of pre-configured synthetic operational scenarios for frontend testing.",
)
def list_scenarios() -> Dict[str, Any]:
    return {
        "count": len(get_all_synthetic_scenarios()),
        "data_classification": "SYNTHETIC",
        "scenarios": get_all_synthetic_scenarios(),
    }


@router.post(
    "/scenarios/{scenario_id}/analyze",
    response_model=IntelligenceAnalyzeResponse,
    summary="Execute Predefined Single-Event Scenario",
    description="Executes a predefined scenario (e.g., normal, unusual, anomalous, high_risk, insufficient_history, conflicting_signals).",
)
def run_scenario(
    scenario_id: str,
    config: NetraConfig = Depends(get_config),
) -> IntelligenceAnalyzeResponse:
    try:
        req = get_synthetic_scenario(scenario_id.lower())
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario '{scenario_id}' not found. Check GET /api/v1/intelligence/scenarios.",
        )
    return analyze_intelligence(request=req, config=config)


# ==============================================================================
# PHASE 2 MULTI-EVENT INTELLIGENCE ENDPOINTS (NEW)
# ==============================================================================

@router.post(
    "/events/analyze",
    response_model=MultiEventAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Multi-Event Batch (Event Intelligence Engine)",
    description=(
        "Core Phase 2 endpoint: Normalizes synthetic events, flags duplicates, computes "
        "evidence-backed multi-dimensional correlations (temporal, spatial, entity, taxonomy, attributes), "
        "forms tactical clusters, detects behavioral patterns, and tracks sector baseline drift."
    ),
)
def analyze_multi_events(
    request: MultiEventAnalyzeRequest,
    config: NetraConfig = Depends(get_config),
) -> MultiEventAnalyzeResponse:
    logger.info(f"Initiating multi-event analysis on batch of {len(request.events)} events.")
    try:
        engine = EventIntelligenceEngine(config=config)
        response = engine.analyze_events(request)
        logger.info(
            f"Multi-event analysis completed: ID={response.analysis_id}, "
            f"clusters={len(response.clusters)}, correlations={len(response.correlations)}"
        )
        return response
    except Exception as exc:
        logger.error(f"Multi-event processing failure: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in multi-event intelligence pipeline: {str(exc)}",
        )


@router.get(
    "/events/scenarios",
    summary="List Phase 2 Multi-Event Synthetic Scenarios",
    description="Returns catalogue of pre-configured multi-event scenarios (bursts, clusters, sequences, duplicates, false-correlations).",
)
def list_multi_scenarios() -> Dict[str, Any]:
    return {
        "count": len(get_all_multi_scenarios()),
        "data_classification": "SYNTHETIC",
        "scenarios": get_all_multi_scenarios(),
    }


@router.post(
    "/events/scenarios/{scenario_id}/analyze",
    response_model=MultiEventAnalyzeResponse,
    summary="Execute Predefined Phase 2 Multi-Event Scenario",
    description="Executes a predefined multi-event scenario directly by scenario ID.",
)
def run_multi_scenario(
    scenario_id: str,
    config: NetraConfig = Depends(get_config),
) -> MultiEventAnalyzeResponse:
    try:
        req = get_multi_scenario(scenario_id.lower())
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Multi-event scenario '{scenario_id}' not found. Check GET /api/v1/intelligence/events/scenarios.",
        )
    engine = EventIntelligenceEngine(config=config)
    return engine.analyze_events(req)


# ==============================================================================
# PHASE 3 ENTITY INTELLIGENCE & FOCUS MODE ENDPOINTS
# ==============================================================================

@router.get(
    "/entities",
    response_model=EntitySearchResponse,
    summary="List / Search Known Canonical Entities",
    description="Returns filtered roster of active and historical synthetic entities.",
)
def search_entities(
    query: Optional[str] = None,
    entity_type: Optional[str] = None,
    status: Optional[EntityStatus] = None,
    engine: EntityIntelligenceEngine = Depends(get_entity_engine),
) -> EntitySearchResponse:
    return engine.search_entities(query=query, entity_type=entity_type, status=status)


@router.get(
    "/entities/scenarios",
    summary="List Phase 3 Entity Synthetic Scenarios",
    description="Returns catalogue of pre-configured entity scenarios (stable, cold-start, surge, drop, expansion, novel type, contradictory).",
)
def list_entity_scenarios() -> Dict[str, Any]:
    return {
        "count": len(get_all_entity_scenarios()),
        "data_classification": "SYNTHETIC",
        "scenarios": get_all_entity_scenarios(),
    }


@router.post(
    "/entities/scenarios/{scenario_id}/analyze",
    response_model=EntityIntelligenceResponse,
    summary="Execute Predefined Phase 3 Entity Scenario",
    description="Executes analysis for a predefined entity scenario by scenario ID.",
)
def run_entity_scenario(
    scenario_id: str,
    engine: EntityIntelligenceEngine = Depends(get_entity_engine),
) -> EntityIntelligenceResponse:
    scen_key = scenario_id.lower()
    if scen_key not in ENTITY_SCENARIOS_MAP:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity scenario '{scenario_id}' not found. Check GET /api/v1/intelligence/entities/scenarios.",
        )
    target_entity_id = ENTITY_SCENARIOS_MAP[scen_key]["entity_id"]
    return engine.analyze_entity(target_entity_id)


@router.post(
    "/entities/compare",
    response_model=EntityCompareResponse,
    summary="Side-by-Side Entity Comparison",
    description="Compares behavioral baselines, anomaly ratings, risk, and confidence across 2+ entities.",
)
def compare_entities(
    request: EntityCompareRequest,
    engine: EntityIntelligenceEngine = Depends(get_entity_engine),
) -> EntityCompareResponse:
    try:
        return engine.compare_entities(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/entities/{entity_id}",
    response_model=EntityIntelligenceResponse,
    summary="Entity Focus Mode Intelligence Dossier",
    description=(
        "Core Phase 3 Master Endpoint: Delivers complete entity profile, behavioral baseline, "
        "change detection, multi-indicator anomaly rating, explainable risk breakdown, bounded confidence, "
        "relational network edges, 30% map context, and strict four-tier intelligence assessment."
    ),
)
def get_entity_intelligence(
    entity_id: str,
    as_of: Optional[datetime] = None,
    engine: EntityIntelligenceEngine = Depends(get_entity_engine),
) -> EntityIntelligenceResponse:
    try:
        return engine.analyze_entity(entity_id=entity_id, as_of=as_of)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity '{entity_id}' not found in operational repository.",
        )


@router.get(
    "/entities/{entity_id}/events",
    response_model=List[EntityTimelineItem],
    summary="Entity Event Timeline Stream",
    description="Returns chronological event timeline items with server-side filtering.",
)
def get_entity_events(
    entity_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    event_type: Optional[str] = None,
    severity: Optional[SeverityLevel] = None,
    limit: Optional[int] = None,
    engine: EntityIntelligenceEngine = Depends(get_entity_engine),
) -> List[EntityTimelineItem]:
    events = engine.repository.get_events_for_entity(entity_id)
    if not events and not engine.repository.get_entity(entity_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity '{entity_id}' not found in operational repository.",
        )
    return engine.timeline_builder.build_timeline(
        events=events,
        start_time=start_time,
        end_time=end_time,
        event_type=event_type,
        severity=severity,
        limit=limit,
    )


@router.get(
    "/entities/{entity_id}/relationships",
    response_model=List[EntityRelationshipEdge],
    summary="Entity Relational Network Graph",
    description="Returns evidence-backed relationship edges connecting this entity to other sector entities.",
)
def get_entity_relationships(
    entity_id: str,
    engine: EntityIntelligenceEngine = Depends(get_entity_engine),
) -> List[EntityRelationshipEdge]:
    entity = engine.repository.get_entity(entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity '{entity_id}' not found in operational repository.",
        )
    all_events = engine.repository.get_all_events()
    return engine.network_builder.build_relationships(
        target_entity_id=entity_id,
        all_events=all_events,
    )

