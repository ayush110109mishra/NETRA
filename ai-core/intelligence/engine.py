"""
Core Intelligence Pipeline Orchestrator for NETRA.
Coordinates validation, normalization, relationship detection, risk calculation,
confidence scoring, severity evaluation, and structured assessment generation.
100% deterministic, explainable, and testable.
"""

import time
import hashlib
from datetime import datetime, timezone
from typing import Optional

from config import NetraConfig, default_config
from models.input import IntelligenceAnalyzeRequest
from models.output import IntelligenceAnalyzeResponse
from events.relationships import detect_event_relationships
from entities.relationships import detect_entity_relationships
from risk.engine import calculate_explainable_risk
from intelligence.confidence import calculate_confidence
from intelligence.severity import evaluate_severity
from intelligence.classifier import classify_observation
from intelligence.assessment import generate_intelligence_assessment


def analyze_intelligence(
    request: IntelligenceAnalyzeRequest,
    config: Optional[NetraConfig] = None,
) -> IntelligenceAnalyzeResponse:
    """
    Execute deterministic intelligence analysis on incoming synthetic operational data.
    """
    start_time = time.perf_counter()
    cfg = config or default_config

    # Step 1: Detect entity relationships in sector context
    related_entities = detect_entity_relationships(
        primary_entity=request.entity,
        primary_location=request.location,
        primary_timestamp=request.timestamp,
        context_entities=request.context_entities,
        spatial_threshold_km=cfg.spatial_proximity_km_threshold,
        temporal_threshold_seconds=cfg.temporal_proximity_seconds_threshold,
    )

    # Step 2: Detect event correlations in sector timeline
    related_events = detect_event_relationships(
        primary_event=request.event,
        primary_entity_id=request.entity.entity_id,
        primary_location=request.location,
        context_events=request.context_events,
        temporal_threshold_seconds=cfg.temporal_proximity_seconds_threshold,
    )

    # Step 3: Compute explainable risk breakdown
    risk_result = calculate_explainable_risk(
        request=request,
        related_entities_count=len(related_entities),
        config=cfg,
    )
    risk_breakdown = risk_result.breakdown
    indicators = risk_result.indicators

    # Step 4: Compute confidence score and breakdown
    confidence_score, conf_breakdown = calculate_confidence(
        request=request,
        config=cfg,
    )

    # Step 5: Evaluate severity level
    severity = evaluate_severity(
        risk_score=risk_breakdown.score,
        indicators=indicators,
        config=cfg,
    )

    # Step 6: Classify observation
    classification = classify_observation(
        risk_score=risk_breakdown.score,
        confidence=confidence_score,
        indicators=indicators,
        confidence_breakdown=conf_breakdown,
        config=cfg,
    )

    # Step 7: Generate explainable intelligence narrative
    assessment_narrative = generate_intelligence_assessment(
        request=request,
        classification=classification,
        severity=severity,
        risk=risk_breakdown,
        confidence=confidence_score,
        confidence_breakdown=conf_breakdown,
        indicators=indicators,
        related_entities=related_entities,
        related_events=related_events,
    )

    # Step 8: Deterministic analysis ID based on event, entity, and timestamp
    id_seed = f"{request.event.event_id}:{request.entity.entity_id}:{request.timestamp.isoformat()}"
    hash_digest = hashlib.sha256(id_seed.encode("utf-8")).hexdigest()[:8].upper()
    analysis_id = f"ANL-{request.event.event_id}-{hash_digest}"

    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 3)

    return IntelligenceAnalyzeResponse(
        analysis_id=analysis_id,
        timestamp=request.timestamp,
        classification=classification,
        severity=severity,
        risk=risk_breakdown,
        confidence=confidence_score,
        confidence_breakdown=conf_breakdown,
        related_entities=related_entities,
        related_events=related_events,
        assessment=assessment_narrative,
        indicators=indicators,
        metadata={
            "processing_time_ms": elapsed_ms,
            "data_classification": cfg.data_classification,
            "engine_version": cfg.version,
            "mode": cfg.mode,
        },
    )
