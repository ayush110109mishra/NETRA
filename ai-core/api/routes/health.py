"""
Health and operational status endpoints for NETRA Intelligence Core.
"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(tags=["System Health"])


@router.get("/health", summary="Basic Health Check")
@router.get("/api/v1/health", summary="V1 Health Check")
def health_check() -> Dict[str, Any]:
    """
    Returns the operational and readiness status of the NETRA Python Intelligence Core.
    """
    return {
        "status": "ok",
        "service": "netra-ai-core",
        "version": "1.0.0",
        "mode": "SIMULATION",
        "data_classification": "SYNTHETIC",
        "intelligence_pipeline": "DETERMINISTIC_V1",
    }
