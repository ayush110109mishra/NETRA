"""
Unit tests for NETRA Intelligence Classification taxonomy.
Tests NORMAL, UNUSUAL, ANOMALOUS, HIGH_RISK, and UNKNOWN deterministic boundary conditions.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from models.common import ClassificationType
from intelligence.classifier import classify_observation
from config import default_config


def test_classify_normal():
    """Verify nominal activity produces NORMAL."""
    indicators = {"activity_deviation": 0.05, "speed_anomaly": 0.10, "relationship_density": 0.0}
    result = classify_observation(risk_score=0.12, confidence=0.90, indicators=indicators)
    assert result == ClassificationType.NORMAL


def test_classify_unusual():
    """Verify moderate deviation produces UNUSUAL."""
    indicators = {"activity_deviation": 0.35, "speed_anomaly": 0.20, "relationship_density": 0.0}
    result = classify_observation(risk_score=0.35, confidence=0.85, indicators=indicators)
    assert result == ClassificationType.UNUSUAL


def test_classify_anomalous():
    """Verify strong deviation produces ANOMALOUS."""
    indicators = {"activity_deviation": 0.65, "speed_anomaly": 0.50, "relationship_density": 0.2}
    result = classify_observation(risk_score=0.58, confidence=0.80, indicators=indicators)
    assert result == ClassificationType.ANOMALOUS


def test_classify_high_risk_score():
    """Verify high combined risk produces HIGH_RISK."""
    indicators = {"activity_deviation": 0.85, "speed_anomaly": 0.80, "relationship_density": 0.6}
    result = classify_observation(risk_score=0.82, confidence=0.88, indicators=indicators)
    assert result == ClassificationType.HIGH_RISK


def test_classify_high_risk_multi_indicators():
    """Verify multiple severe indicators elevate to HIGH_RISK even at moderate aggregate risk."""
    indicators = {"activity_deviation": 0.65, "speed_anomaly": 0.65, "relationship_density": 0.3}
    result = classify_observation(risk_score=0.62, confidence=0.85, indicators=indicators)
    assert result == ClassificationType.HIGH_RISK


def test_classify_unknown_low_confidence():
    """Verify low confidence produces UNKNOWN regardless of risk score."""
    indicators = {"activity_deviation": 0.80, "speed_anomaly": 0.90, "relationship_density": 0.5}
    # Confidence 0.20 is below default_config.classification.min_confidence_for_definitive (0.35)
    result = classify_observation(risk_score=0.85, confidence=0.20, indicators=indicators)
    assert result == ClassificationType.UNKNOWN
