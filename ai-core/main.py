"""
NETRA Intelligence Core - Main Application Entrypoint.
ASTRAVEDA Defence Intelligence Platform (ATUL AI/ML Engineering).
FastAPI application with CORS, structured error handlers, logging, and OpenAPI documentation.
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import default_config
from models.error import APIError, APIErrorResponse
from api.routes import (
    health_router,
    intelligence_router,
    anomaly_router,
    fusion_router,
    prediction_router,
    ask_router,
    graph_router,
)




# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [NETRA-AI] %(name)s - %(message)s",
)
logger = logging.getLogger("netra.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Initializing NETRA Intelligence Core Phase 1 (Deterministic MVP)...")
    logger.info(f"App: {default_config.app_name} v{default_config.version}")
    logger.info(f"Operational Mode: {default_config.mode} | Classification: {default_config.data_classification}")
    yield
    logger.info("Shutting down NETRA Intelligence Core.")


app = FastAPI(
    title="NETRA Intelligence Core API",
    description=(
        "ASTRAVEDA Defence Intelligence Platform - Python Intelligence Core (ATUL).\n\n"
        "Provides deterministic, explainable intelligence assessments, risk scoring, "
        "anomaly classification, confidence modeling, and relationship detection over "
        "synthetic operational data.\n\n"
        "**Note**: All telemetry and assessments are explicitly **SYNTHETIC / DEMO**."
    ),
    version=default_config.version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Enable CORS for Ayush's operational frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing & audit middleware
@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    logger.info(f"Incoming {request.method} {request.url.path}")
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
    logger.info(f"Completed {request.method} {request.url.path} with status {response.status_code} in {duration_ms}ms")
    return response


# --- Structured Error Handlers (Section 16 Specification) ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors by formatting into NETRA's structured error envelope.
    """
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    loc = first_error.get("loc", [])
    field_path = ".".join(str(item) for item in loc if item not in ("body",))

    api_error = APIError(
        code="INVALID_INPUT",
        message=first_error.get("msg", "Validation error occurred."),
        field=field_path or None,
        details=[{"field": ".".join(str(x) for x in e.get("loc", [])), "msg": e.get("msg")} for e in errors],
    )
    logger.warning(f"Request validation failed: {api_error.message} on field {api_error.field}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIErrorResponse(error=api_error).model_dump(),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle standard HTTP exceptions with structured error envelope.
    """
    api_error = APIError(
        code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
        field=None,
        details=None,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=APIErrorResponse(error=api_error).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler to prevent raw stack trace leakage.
    """
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    api_error = APIError(
        code="INTERNAL_PROCESSING_ERROR",
        message="An unexpected error occurred during intelligence processing.",
        field=None,
        details=None,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIErrorResponse(error=api_error).model_dump(),
    )


# Register routers
app.include_router(health_router)
app.include_router(intelligence_router)
app.include_router(anomaly_router)
app.include_router(fusion_router)
app.include_router(prediction_router)
app.include_router(ask_router)
app.include_router(graph_router)






if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
