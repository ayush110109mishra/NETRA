"""
Unit tests for NETRA Severity Engine.
Verifies INFO, LOW, MEDIUM, HIGH, and CRITICAL boundary mappings.
"""

import pytest
from models.common import SeverityLevel
from intelligence.severity import evaluate_severity
from config import default_config


def test_severity_info():
    """Verify minimal metrics map to INFO."""
    indicators = {"event_severity_baseline": 0.10, "activity_deviation": 0.05, "relationship_density": 0.0}
    severity = evaluate_severity(risk_score=0.10, indicators=indicators)
    assert severity == SeverityLevel.INFO


def test_severity_low():
    """Verify low metrics map to LOW."""
    indicators = {"event_severity_baseline": 0.20, "activity_deviation": 0.20, "relationship_density": 0.1}
    severity = evaluate_severity(risk_score=0.30, indicators=indicators)
    assert severity == SeverityLevel.LOW


def test_severity_medium():
    """Verify moderate metrics map to MEDIUM."""
    indicators = {"event_severity_baseline": 0.50, "activity_deviation": 0.45, "relationship_density": 0.2}
    severity = evaluate_severity(risk_score=0.55, indicators=indicators)
    assert severity == SeverityLevel.MEDIUM


def test_severity_high():
    """Verify high metrics map to HIGH."""
    indicators = {"event_severity_baseline": 0.70, "activity_deviation": 0.75, "relationship_density": 0.4}
    severity = evaluate_severity(risk_score=0.75, indicators=indicators)
    assert severity == SeverityLevel.HIGH


def test_severity_critical():
    """Verify severe multi-factor metrics map to CRITICAL."""
    indicators = {"event_severity_baseline": 0.90, "activity_deviation": 0.95, "relationship_density": 0.8}
    severity = evaluate_severity(risk_score=0.92, indicators=indicators)
    assert severity == SeverityLevel.CRITICAL
