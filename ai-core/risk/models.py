"""
Internal models for risk calculation.
"""

from typing import List, Dict
from pydantic import BaseModel
from models.common import RiskLevel
from models.output import RiskFactor, RiskBreakdown


class RiskEvaluationResult(BaseModel):
    breakdown: RiskBreakdown
    indicators: Dict[str, float]
