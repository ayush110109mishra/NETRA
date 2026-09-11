"""
Phase 6 Predictive Intelligence & Forecasting API Routes for NETRA.
Provides endpoints for predictive analysis, multi-target forecasts, prediction histories,
synthetic evaluation metrics, and operational scenario execution.
"""

from typing import Any, Dict, List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies import get_config, get_prediction_engine
from config import NetraConfig
from intelligence.predictive_intelligence import PredictiveIntelligenceEngine
from models.predictive_intelligence import (
    EntityForecastResponse,
    EntityPredictionsHistoryResponse,
    ForecastEvaluationResponse,
    ForecastHorizon,
    PredictionAnalyzeRequest,
    PredictionAnalyzeResponse,
    PredictiveTarget,
)
from simulation.prediction_scenarios import (
    get_all_prediction_scenarios,
    get_prediction_scenario,
)

logger = logging.getLogger("netra.api.prediction")

router = APIRouter(prefix="/api/v1/intelligence", tags=["Predictive Intelligence & Forecasting"])


@router.post(
    "/predictions/analyze",
    response_model=PredictionAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Predictive Intelligence Analysis",
    description=(
        "Core Phase 6 endpoint: Analyzes historical observations, evaluates temporal trends, "
        "applies multi-strategy ensemble forecasting (Persistence, Trend, Recurrence), "
        "quantifies residual uncertainty, calibrates confidence, and produces an explainable "
        "five-tier epistemic intelligence assessment."
    ),
)
def analyze_prediction(
    request: PredictionAnalyzeRequest,
    engine: PredictiveIntelligenceEngine = Depends(get_prediction_engine),
) -> PredictionAnalyzeResponse:
    try:
        return engine.analyze_prediction(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error(f"Predictive analysis failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction processing error: {str(exc)}",
        )


@router.get(
    "/entities/{entity_id}/predictions",
    response_model=EntityPredictionsHistoryResponse,
    summary="Entity Predictions History",
    description="Retrieves chronological log of past predictions and forecasts generated for an entity.",
)
def get_entity_predictions(
    entity_id: str,
    limit: int = Query(default=50, ge=1, le=200, description="Max history records to return"),
    engine: PredictiveIntelligenceEngine = Depends(get_prediction_engine),
) -> EntityPredictionsHistoryResponse:
    return engine.get_entity_predictions(entity_id=entity_id, limit=limit)


@router.get(
    "/entities/{entity_id}/forecast",
    response_model=EntityForecastResponse,
    summary="Multi-Target Operational Entity Forecast",
    description="Returns synchronized forecasts across all 6 predictive target dimensions for an entity dashboard.",
)
def get_entity_forecast(
    entity_id: str,
    engine: PredictiveIntelligenceEngine = Depends(get_prediction_engine),
) -> EntityForecastResponse:
    try:
        return engine.get_entity_forecast(entity_id=entity_id)
    except Exception as exc:
        logger.error(f"Entity forecast lookup failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecast calculation error: {str(exc)}",
        )


@router.get(
    "/predictions/history",
    response_model=List[PredictionAnalyzeResponse],
    summary="List Global Prediction History",
    description="Returns recent predictions across all synthetic entities with optional filtering.",
)
def get_global_predictions_history(
    entity_id: Optional[str] = Query(default=None, description="Optional entity ID filter"),
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    engine: PredictiveIntelligenceEngine = Depends(get_prediction_engine),
) -> List[PredictionAnalyzeResponse]:
    if entity_id:
        return engine.get_entity_predictions(entity_id=entity_id, limit=limit).predictions

    all_preds: List[PredictionAnalyzeResponse] = []
    for preds in engine._entity_forecast_cache.values():
        all_preds.extend(preds)
    return all_preds[-limit:]


@router.get(
    "/predictions/evaluation",
    response_model=ForecastEvaluationResponse,
    summary="Get Forecasting Accuracy & Evaluation Metrics",
    description="Returns aggregate synthetic prediction accuracy, mean absolute error, and directional accuracy.",
)
def get_prediction_evaluation(
    engine: PredictiveIntelligenceEngine = Depends(get_prediction_engine),
) -> ForecastEvaluationResponse:
    return engine.evaluate_predictions()


@router.get(
    "/predictions/scenarios",
    summary="List Phase 6 Predictive Synthetic Scenarios",
    description="Returns catalog of 16 predefined predictive operational test scenarios.",
)
def list_prediction_scenarios() -> Dict[str, Any]:
    scenarios = get_all_prediction_scenarios()
    return {
        "count": len(scenarios),
        "data_classification": "SYNTHETIC",
        "scenarios": {
            k: {
                "scenario_id": k,
                "name": v["name"],
                "description": v["description"],
                "target_entity_id": v["entity_id"],
                "target": v["target"],
                "horizon": v["horizon"],
                "observation_count": len(v["events"]),
                "expected_forecast_state": v["expected_forecast_state"],
                "expected_sufficiency": v["expected_sufficiency"],
            }
            for k, v in scenarios.items()
        },
    }


@router.post(
    "/predictions/scenarios/{scenario_id}/analyze",
    response_model=PredictionAnalyzeResponse,
    summary="Execute Predefined Phase 6 Operational Scenario",
    description="Executes a predefined predictive synthetic scenario by identifier and returns full forecast assessment.",
)
def run_prediction_scenario(
    scenario_id: str,
    engine: PredictiveIntelligenceEngine = Depends(get_prediction_engine),
) -> PredictionAnalyzeResponse:
    scen = get_prediction_scenario(scenario_id.lower())
    if not scen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction scenario '{scenario_id}' not found. Check GET /api/v1/intelligence/predictions/scenarios.",
        )

    req = PredictionAnalyzeRequest(
        entity_id=scen["entity_id"],
        target=PredictiveTarget(scen["target"]),
        horizon=ForecastHorizon(scen["horizon"]),
        as_of=scen.get("reference_time"),
        custom_events=scen.get("events"),
        include_phase5_fusion=True,
    )
    return engine.analyze_prediction(req)
