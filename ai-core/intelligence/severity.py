"""
Deterministic Severity Engine for NETRA Intelligence Core.
Maps operational magnitude, event type baselines, and risk metrics to standardized severity levels.
"""

from typing import Dict, Optional
from config import NetraConfig, default_config
from models.common import SeverityLevel


def evaluate_severity(
    risk_score: float,
    indicators: Dict[str, float],
    config: Optional[NetraConfig] = None,
) -> SeverityLevel:
    """
    Evaluate deterministic operational severity.
    Combines calculated risk score with event baseline severity and activity deviation.
    """
    cfg = config or default_config
    thresholds = cfg.severity

    base_sev = indicators.get("event_severity_baseline", 0.20)
    act_dev = indicators.get("activity_deviation", 0.10)
    rel_density = indicators.get("relationship_density", 0.0)

    composite_severity = (
        (0.40 * risk_score)
        + (0.30 * base_sev)
        + (0.20 * act_dev)
        + (0.10 * rel_density)
    )

    if composite_severity < thresholds.info_max:
        return SeverityLevel.INFO
    elif composite_severity < thresholds.low_max:
        return SeverityLevel.LOW
    elif composite_severity < thresholds.medium_max:
        return SeverityLevel.MEDIUM
    elif composite_severity < thresholds.high_max:
        return SeverityLevel.HIGH
    else:
        return SeverityLevel.CRITICAL
