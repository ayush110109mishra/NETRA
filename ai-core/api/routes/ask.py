"""
Phase 7 Ask NETRA REST API Routes.
Mounts /ask, /ask/parse, /ask/capabilities, /ask/examples, and scenario execution endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies import get_ask_engine
from intelligence.ask_netra import AskNetraEngine
from models.ask_netra import (
    AskNetraRequest,
    AskNetraResponse,
    CapabilitiesResponse,
    ExamplesResponse,
    ParseResponse,
)
from simulation.ask_scenarios import get_ask_scenarios, get_ask_scenario_by_id


router = APIRouter(prefix="/api/v1/intelligence/ask", tags=["Ask NETRA Intelligence"])


@router.post("", response_model=AskNetraResponse, status_code=status.HTTP_200_OK)
def ask_netra(
    request: AskNetraRequest,
    engine: AskNetraEngine = Depends(get_ask_engine),
) -> AskNetraResponse:
    """
    Execute natural language intelligence query against NETRA deterministic core.
    Translates question to structured query, executes inspectable multi-step plan,
    indexes 5-tier epistemic ledger, and synthesizes explainable answer with no hallucination.
    """
    return engine.ask(request)


@router.post("/parse", response_model=ParseResponse, status_code=status.HTTP_200_OK)
def parse_query(
    request: AskNetraRequest,
    engine: AskNetraEngine = Depends(get_ask_engine),
) -> ParseResponse:
    """
    Parse a natural language question and construct the inspectable execution plan
    without executing engine steps.
    """
    return engine.parse(
        query=request.query,
        session_id=request.session_id,
        as_of=request.as_of,
    )


@router.get("/capabilities", response_model=CapabilitiesResponse, status_code=status.HTTP_200_OK)
def get_capabilities(
    engine: AskNetraEngine = Depends(get_ask_engine),
) -> CapabilitiesResponse:
    """
    Retrieve full catalog of supported intents, epistemic tiers, and system capabilities.
    """
    return engine.get_capabilities()


@router.get("/examples", response_model=ExamplesResponse, status_code=status.HTTP_200_OK)
def get_examples(
    engine: AskNetraEngine = Depends(get_ask_engine),
) -> ExamplesResponse:
    """
    Retrieve catalog of categorized example operational queries.
    """
    return engine.get_examples()


@router.get("/scenarios", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def list_scenarios() -> List[Dict[str, Any]]:
    """
    List all 20 predefined operational scenarios for Ask NETRA.
    """
    return get_ask_scenarios()


@router.post("/scenarios/{scenario_id}", response_model=AskNetraResponse, status_code=status.HTTP_200_OK)
def execute_scenario(
    scenario_id: str,
    as_of: Optional[datetime] = None,
    engine: AskNetraEngine = Depends(get_ask_engine),
) -> AskNetraResponse:
    """
    Execute a specific pre-packaged operational scenario by ID.
    """
    try:
        scenario = get_ask_scenario_by_id(scenario_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario '{scenario_id}' not found.",
        )

    # Set up session if scenario specifies an active entity
    session_id = f"scenario_session_{scenario_id}"
    req = AskNetraRequest(
        query=scenario["query"],
        session_id=session_id,
        as_of=as_of,
        active_entity_id=scenario.get("session_active_entity"),
    )
    return engine.ask(req)
