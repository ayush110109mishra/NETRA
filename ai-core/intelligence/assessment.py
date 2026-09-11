"""
Deterministic Assessment Generator for NETRA Intelligence Core.
Generates an explainable, fact-grounded intelligence narrative strictly derived
from structured inputs and calculated metrics.
Explicitly demarcates OBSERVED, INFERRED, and UNCERTAIN operational aspects.
"""

from typing import List, Dict
from models.common import ClassificationType, SeverityLevel
from models.input import IntelligenceAnalyzeRequest
from models.output import RiskBreakdown, ConfidenceBreakdown, RelatedEntityOutput, RelatedEventOutput


def generate_intelligence_assessment(
    request: IntelligenceAnalyzeRequest,
    classification: ClassificationType,
    severity: SeverityLevel,
    risk: RiskBreakdown,
    confidence: float,
    confidence_breakdown: ConfidenceBreakdown,
    indicators: Dict[str, float],
    related_entities: List[RelatedEntityOutput],
    related_events: List[RelatedEventOutput],
) -> str:
    """
    Produce a deterministic natural-language intelligence summary.
    Does not hallucinate or extrapolate beyond provided structured telemetry.
    """
    entity_id = request.entity.entity_id
    callsign_str = f" ({request.entity.callsign})" if request.entity.callsign else ""
    event_type = request.event.event_type
    curr_speed = request.attributes.speed
    curr_act = request.attributes.activity_level
    prev_act = request.historical_context.previous_activity

    # 1. Observed facts
    observed_parts = [
        f"Entity {entity_id}{callsign_str} detected conducting synthetic '{event_type}'",
        f"at coordinates [{request.location.latitude:.4f}, {request.location.longitude:.4f}]",
        f"at {curr_speed:.1f} km/h with normalized activity level of {curr_act:.2f} (baseline: {prev_act:.2f}).",
    ]
    observed_text = f"[OBSERVED] {' '.join(observed_parts)}"

    # 2. Inferred intelligence
    top_factor = risk.factors[0].description if risk.factors else "nominal activity"
    inferred_parts = [
        f"Current situation classified as {classification.value} with {severity.value} operational severity.",
        f"Calculated risk score is {risk.score:.2f} ({risk.level.value}) driven by {top_factor.lower()}.",
    ]
    if related_entities:
        inferred_parts.append(
            f"Detected {len(related_entities)} correlated entities in sector ({', '.join(e.entity_id for e in related_entities)})."
        )
    if related_events:
        inferred_parts.append(
            f"Identified {len(related_events)} correlated events in timeline ({', '.join(e.event_id for e in related_events)})."
        )
    inferred_text = f"[INFERRED] {' '.join(inferred_parts)}"

    # 3. Uncertainties & Data Quality
    uncertainty_parts = []
    if confidence_breakdown.historical_baseline_depth < 0.40:
        uncertainty_parts.append("Limited historical observations available for this synthetic entity.")
    if confidence_breakdown.signal_consistency < 0.80:
        uncertainty_parts.append("Sensor telemetry exhibits potential signal contradiction.")
    if not request.location.sector_id:
        uncertainty_parts.append("Sector designation not explicitly provided.")

    if not uncertainty_parts:
        uncertainty_parts.append("High baseline coverage with consistent multi-sensor telemetry.")

    uncertain_text = f"[UNCERTAIN] Assessment confidence rated at {confidence:.2f}. {' '.join(uncertainty_parts)}"

    return f"{observed_text} {inferred_text} {uncertain_text}"
