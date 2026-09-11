"""
Explainable, deterministic Risk Engine for NETRA Intelligence Core.
Computes weighted factor contributions and maps to operational risk levels.
"""

from typing import List, Dict, Optional
from config import NetraConfig, default_config
from models.common import RiskLevel
from models.input import IntelligenceAnalyzeRequest
from models.output import RiskFactor, RiskBreakdown
from events.models import EVENT_TYPE_SEVERITY_BASELINE
from risk.models import RiskEvaluationResult


def calculate_explainable_risk(
    request: IntelligenceAnalyzeRequest,
    related_entities_count: int = 0,
    config: Optional[NetraConfig] = None,
) -> RiskEvaluationResult:
    """
    Compute a deterministic, explainable risk score between 0.0 and 1.0.
    Returns the complete risk breakdown and individual factor contributions.
    """
    cfg = config or default_config
    weights = cfg.risk_weights

    # 1. Activity Deviation Indicator [0.0 - 1.0]
    curr_act = request.attributes.activity_level
    prev_act = request.historical_context.previous_activity
    activity_dev = min(1.0, max(0.0, abs(curr_act - prev_act)))

    # 2. Speed Anomaly Indicator [0.0 - 1.0]
    curr_speed = request.attributes.speed
    baseline_speed = request.historical_context.baseline_speed
    if baseline_speed is not None and baseline_speed > 0:
        speed_delta = abs(curr_speed - baseline_speed)
        speed_anomaly = min(1.0, max(0.0, speed_delta / max(30.0, baseline_speed)))
    else:
        speed_anomaly = min(1.0, max(0.0, curr_speed / 120.0))

    # 3. Base Event Severity Baseline [0.0 - 1.0]
    evt_type = request.event.event_type.lower()
    base_severity = EVENT_TYPE_SEVERITY_BASELINE.get(evt_type, 0.25)
    if request.event.priority_hint:
        hint_weights = {"INFO": 0.1, "LOW": 0.3, "MEDIUM": 0.6, "HIGH": 0.8, "CRITICAL": 1.0}
        hint_val = hint_weights.get(request.event.priority_hint.value, base_severity)
        base_severity = round((base_severity * 0.6) + (hint_val * 0.4), 3)

    # 4. Relationship Density & Past Deviations [0.0 - 1.0]
    past_devs = request.historical_context.deviation_history_count or 0
    rel_density = min(1.0, (past_devs * 0.20) + (related_entities_count * 0.15))

    # Compute Factor Contributions
    contrib_act = round(weights.activity_deviation * activity_dev, 4)
    contrib_spd = round(weights.speed_anomaly * speed_anomaly, 4)
    contrib_sev = round(weights.event_severity_baseline * base_severity, 4)
    contrib_rel = round(weights.relationship_density * rel_density, 4)

    total_score = min(1.0, max(0.0, round(contrib_act + contrib_spd + contrib_sev + contrib_rel, 2)))

    # Determine Risk Level
    if total_score < 0.25:
        level = RiskLevel.LOW
    elif total_score < 0.50:
        level = RiskLevel.MEDIUM
    elif total_score < 0.75:
        level = RiskLevel.HIGH
    else:
        level = RiskLevel.CRITICAL

    factors: List[RiskFactor] = [
        RiskFactor(
            factor="activity_deviation",
            weight=weights.activity_deviation,
            contribution=contrib_act,
            description=(
                f"Activity level {curr_act:.2f} deviates by {activity_dev:.2f} "
                f"from baseline {prev_act:.2f}"
            ),
        ),
        RiskFactor(
            factor="speed_anomaly",
            weight=weights.speed_anomaly,
            contribution=contrib_spd,
            description=(
                f"Observed speed {curr_speed:.1f} km/h versus "
                f"{f'baseline {baseline_speed:.1f} km/h' if baseline_speed else 'standard patrol threshold'}"
            ),
        ),
        RiskFactor(
            factor="event_severity_baseline",
            weight=weights.event_severity_baseline,
            contribution=contrib_sev,
            description=f"Tactical baseline for event type '{request.event.event_type}'",
        ),
        RiskFactor(
            factor="relationship_density",
            weight=weights.relationship_density,
            contribution=contrib_rel,
            description=(
                f"Associated with {related_entities_count} nearby entities "
                f"and {past_devs} historical deviation incidents"
            ),
        ),
    ]

    breakdown = RiskBreakdown(
        score=total_score,
        level=level,
        factors=factors,
    )

    indicators = {
        "activity_deviation": round(activity_dev, 4),
        "speed_anomaly": round(speed_anomaly, 4),
        "event_severity_baseline": round(base_severity, 4),
        "relationship_density": round(rel_density, 4),
    }

    return RiskEvaluationResult(breakdown=breakdown, indicators=indicators)
