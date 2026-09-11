"""
Phase 7 Structured Query Filter Parser for Ask NETRA.
Extracts severity thresholds, risk/anomaly cutoffs, event types, and limit caps.
"""

import re
from typing import List, Optional
from models.ask_netra import StructuredFilters


SEVERITY_PATTERN = re.compile(r"\b(critical|high|medium|low|info)\s+severity\b|\bseverity\s*(?:>=?|>|above|over|is)\s*(critical|high|medium|low|info)\b", re.I)
RISK_CUTOFF_PATTERN = re.compile(r"\brisk\s*(?:>=?|>|above|over|exceeding)\s*([0-9]*\.?[0-9]+)\b", re.I)
ANOMALY_CUTOFF_PATTERN = re.compile(r"\banomaly\s*(?:>=?|>|above|over|exceeding)\s*([0-9]*\.?[0-9]+)\b", re.I)
LIMIT_PATTERN = re.compile(r"\b(?:top|last|first|limit)\s+(\d+)\b", re.I)

COMMON_EVENT_TYPES = [
    "BORDER_CROSSING",
    "SPEED_VIOLATION",
    "FORMATION_CHANGE",
    "SURVEILLANCE_SWEEP",
    "COMMUNICATION_BURST",
    "RADAR_LOCK",
    "PATROL",
    "LOITERING",
    "HEADING_DEVIATION",
]


class FilterExtractor:
    """Extracts operational filtering parameters from operator query strings."""

    def extract(self, text: str) -> StructuredFilters:
        severity_min: Optional[str] = None
        risk_min: Optional[float] = None
        anomaly_min: Optional[float] = None
        limit: int = 50
        event_types: List[str] = []

        # Severity
        sev_match = SEVERITY_PATTERN.search(text)
        if sev_match:
            severity_min = (sev_match.group(1) or sev_match.group(2)).upper()

        # Risk cutoff
        risk_match = RISK_CUTOFF_PATTERN.search(text)
        if risk_match:
            try:
                risk_min = float(risk_match.group(1))
            except ValueError:
                pass

        # Anomaly cutoff
        anom_match = ANOMALY_CUTOFF_PATTERN.search(text)
        if anom_match:
            try:
                anomaly_min = float(anom_match.group(1))
            except ValueError:
                pass

        # Limit
        limit_match = LIMIT_PATTERN.search(text)
        if limit_match:
            try:
                limit = int(limit_match.group(1))
            except ValueError:
                pass

        # Event types
        upper_text = text.upper()
        for evt_type in COMMON_EVENT_TYPES:
            alt_name = evt_type.replace("_", " ")
            if evt_type in upper_text or alt_name in upper_text:
                event_types.append(evt_type)

        return StructuredFilters(
            severity_min=severity_min,
            risk_min=risk_min,
            anomaly_min=anomaly_min,
            event_types=event_types,
            limit=limit,
        )
