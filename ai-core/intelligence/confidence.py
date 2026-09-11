"""
Deterministic Confidence Engine for NETRA Intelligence Core.
Separates confidence (reliability of assessment) from risk (degree of concern).
Evaluates data completeness, historical baseline depth, and sensor/telemetry signal consistency.
"""

from typing import Tuple, Optional
from config import NetraConfig, default_config
from models.input import IntelligenceAnalyzeRequest
from models.output import ConfidenceBreakdown


def calculate_confidence(
    request: IntelligenceAnalyzeRequest,
    config: Optional[NetraConfig] = None,
) -> Tuple[float, ConfidenceBreakdown]:
    """
    Calculate deterministic confidence score and detailed breakdown.
    """
    cfg = config or default_config
    weights = cfg.confidence_weights

    # 1. Data Completeness [0.0 - 1.0]
    total_checks = 6
    present_checks = 0

    if request.entity.callsign:
        present_checks += 1
    if request.location.sector_id:
        present_checks += 1
    if request.attributes.heading_deg is not None:
        present_checks += 1
    if request.attributes.signal_strength_dbm is not None:
        present_checks += 1
    if request.historical_context.baseline_speed is not None:
        present_checks += 1
    if (request.attributes.sensor_count or 0) > 1:
        present_checks += 1

    data_completeness = round(0.60 + 0.40 * (present_checks / total_checks), 2)

    # 2. Historical Baseline Depth [0.0 - 1.0]
    hist_count = request.historical_context.historical_event_count
    if hist_count <= 0:
        hist_depth = 0.15
    elif hist_count < 5:
        hist_depth = round(0.15 + (hist_count / 5.0) * 0.35, 2)
    elif hist_count < 20:
        hist_depth = round(0.50 + ((hist_count - 5) / 15.0) * 0.40, 2)
    else:
        hist_depth = 1.00

    # 3. Signal Consistency [0.0 - 1.0]
    consistency_penalties = 0.0

    if request.attributes.speed > 50.0 and request.attributes.activity_level < 0.05:
        consistency_penalties += 0.35

    if (request.attributes.sensor_count or 0) == 0:
        consistency_penalties += 0.40

    if request.attributes.activity_level > 0.95 and request.attributes.speed == 0.0 and hist_count == 0:
        consistency_penalties += 0.20

    signal_consistency = max(0.10, round(1.0 - consistency_penalties, 2))

    total_confidence = round(
        (weights.data_completeness * data_completeness)
        + (weights.historical_baseline_depth * hist_depth)
        + (weights.signal_consistency * signal_consistency),
        2,
    )
    total_confidence = min(1.0, max(0.05, total_confidence))

    breakdown = ConfidenceBreakdown(
        data_completeness=data_completeness,
        historical_baseline_depth=hist_depth,
        signal_consistency=signal_consistency,
    )

    return total_confidence, breakdown
