"""
Deterministic Intelligence Classification Module.
Categorizes observations into NORMAL, UNUSUAL, ANOMALOUS, HIGH_RISK, or UNKNOWN
based on explicit threshold boundaries and confidence checks.
"""

from typing import Dict, Optional
from config import NetraConfig, default_config
from models.common import ClassificationType
from models.output import ConfidenceBreakdown


def classify_observation(
    risk_score: float,
    confidence: float,
    indicators: Dict[str, float],
    confidence_breakdown: Optional[ConfidenceBreakdown] = None,
    config: Optional[NetraConfig] = None,
) -> ClassificationType:
    """
    Classify the observed operational situation into the deterministic NETRA taxonomy.
    """
    cfg = config or default_config
    thresholds = cfg.classification

    # Rule 1: Insufficient information check (cold-start or low data confidence)
    if confidence < thresholds.min_confidence_for_definitive:
        return ClassificationType.UNKNOWN
    if confidence_breakdown and confidence_breakdown.historical_baseline_depth <= 0.20:
        return ClassificationType.UNKNOWN

    act_dev = indicators.get("activity_deviation", 0.0)
    spd_anom = indicators.get("speed_anomaly", 0.0)
    rel_density = indicators.get("relationship_density", 0.0)

    # Rule 2: High Risk classification
    # Overall critical risk OR combined severe threat indicators
    if risk_score >= thresholds.anomalous_max:
        return ClassificationType.HIGH_RISK
    if risk_score >= 0.60 and (act_dev >= 0.60 and spd_anom >= 0.60):
        return ClassificationType.HIGH_RISK
    if risk_score >= 0.60 and rel_density >= 0.70 and act_dev >= 0.50:
        return ClassificationType.HIGH_RISK

    # Rule 3: Anomalous classification
    # Significant deviation from baseline
    if act_dev > thresholds.unusual_max or risk_score > thresholds.unusual_max or spd_anom > 0.70:
        return ClassificationType.ANOMALOUS

    # Rule 4: Unusual classification
    # Moderate deviation detected
    if act_dev > thresholds.normal_max or risk_score > thresholds.normal_max:
        return ClassificationType.UNUSUAL

    # Rule 5: Normal
    return ClassificationType.NORMAL
