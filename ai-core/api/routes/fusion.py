"""
Phase 5 Multi-Source Intelligence Fusion API Routes for NETRA.
Provides endpoints for observation fusion, source registry & health queries,
entity-centric fused intelligence profiles, conflict logs, and synthetic scenario execution.
"""

from typing import Any, Dict, List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies import get_config, get_fusion_engine
from config import NetraConfig
from intelligence.fusion_intelligence import FusionIntelligenceEngine
from models.fusion_intelligence import (
    ConflictRecord,
    EntityFusedIntelligenceResponse,
    FusionAnalyzeRequest,
    FusionAnalyzeResponse,
    SourceMetadata,
)
from simulation.fusion_scenarios import (
    get_all_fusion_scenarios,
    get_fusion_scenario,
)

logger = logging.getLogger("netra.api.fusion")

router = APIRouter(prefix="/api/v1/intelligence", tags=["Multi-Source Intelligence Fusion"])


@router.post(
    "/fusion/analyze",
    response_model=FusionAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Multi-Source Intelligence Fusion Analysis",
    description=(
        "Core Phase 5 endpoint: Ingests heterogeneous observations from multiple synthetic sources, "
        "normalizes payloads, evaluates temporal & spatial alignment, resolves synthetic entity references, "
        "measures cross-source corroboration, detects & arbitrates contradictions, ledgerizes immutable evidence, "
        "and produces explainable fused assessments with optional Phase 4 anomaly/risk integration."
    ),
)
def analyze_fusion(
    request: FusionAnalyzeRequest,
    engine: FusionIntelligenceEngine = Depends(get_fusion_engine),
) -> FusionAnalyzeResponse:
    try:
        return engine.analyze_fusion(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error(f"Multi-source fusion failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fusion processing error: {str(exc)}",
        )


@router.get(
    "/fusion/sources",
    response_model=List[SourceMetadata],
    summary="List Registered Intelligence Sources",
    description="Returns the deterministic catalog of registered synthetic sensors, declared reliability, and independence groups.",
)
def list_sources(
    engine: FusionIntelligenceEngine = Depends(get_fusion_engine),
) -> List[SourceMetadata]:
    return engine.list_sources()


@router.get(
    "/fusion/conflicts",
    response_model=List[ConflictRecord],
    summary="List Detected Multi-Source Conflicts",
    description="Returns active and historical sensor contradictions with preserved opposing claims and arbitration details.",
)
def list_conflicts(
    engine: FusionIntelligenceEngine = Depends(get_fusion_engine),
) -> List[ConflictRecord]:
    return engine.get_active_conflicts()


@router.get(
    "/entities/{entity_id}/fused-intelligence",
    response_model=EntityFusedIntelligenceResponse,
    summary="Entity Fused Intelligence Profile",
    description="Returns synthesized multi-source observations, supporting sensors, conflicts, evidence, and Phase 4 risk summary for an entity.",
)
def get_entity_fused_intelligence(
    entity_id: str,
    engine: FusionIntelligenceEngine = Depends(get_fusion_engine),
) -> EntityFusedIntelligenceResponse:
    try:
        return engine.get_entity_fused_intelligence(entity_id=entity_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/fusion/scenarios",
    summary="List Phase 5 Fusion Synthetic Scenarios",
    description="Returns catalog of 14 predefined multi-source operational scenarios covering consensus, conflicts, clock skew, and dropout.",
)
def list_fusion_scenarios() -> Dict[str, Any]:
    scenarios = get_all_fusion_scenarios()
    return {
        "count": len(scenarios),
        "data_classification": "SYNTHETIC",
        "scenarios": {
            k: {
                "scenario_id": k,
                "name": v["name"],
                "description": v["description"],
                "observation_count": len(v["observations"]),
                "target_entity_id": v.get("target_entity_id"),
            }
            for k, v in scenarios.items()
        },
    }


@router.post(
    "/fusion/scenarios/{scenario_id}/analyze",
    response_model=FusionAnalyzeResponse,
    summary="Execute Predefined Phase 5 Operational Scenario",
    description="Executes a predefined multi-source synthetic scenario by identifier and returns full fusion assessment.",
)
def run_fusion_scenario(
    scenario_id: str,
    engine: FusionIntelligenceEngine = Depends(get_fusion_engine),
) -> FusionAnalyzeResponse:
    scen = get_fusion_scenario(scenario_id.lower())
    if not scen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fusion scenario '{scenario_id}' not found. Check GET /api/v1/intelligence/fusion/scenarios.",
        )

    req = FusionAnalyzeRequest(
        observations=scen["observations"],
        target_entity_id=scen.get("target_entity_id"),
        enable_phase4_integration=True,
    )
    return engine.analyze_fusion(req)
