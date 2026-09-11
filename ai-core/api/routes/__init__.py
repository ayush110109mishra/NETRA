"""
API routes subpackage.
"""

from .health import router as health_router
from .intelligence import router as intelligence_router
from .anomaly import router as anomaly_router
from .fusion import router as fusion_router
from .prediction import router as prediction_router

__all__ = ["health_router", "intelligence_router", "anomaly_router", "fusion_router", "prediction_router"]


