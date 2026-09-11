"""
Unit tests for NETRA Phase 6 Model Calibration and Evaluation.
Validates ensemble model agreement calculations and synthetic forecasting performance tracking.
"""

import pytest
from prediction.calibration import ModelCalibrator


def test_model_agreement_unanimous():
    candidates = {
        "persistence": "STABLE",
        "trend": "STABLE",
        "recurrence": "STABLE",
    }
    agreement = ModelCalibrator.calculate_model_agreement(candidates)
    assert agreement == 1.0


def test_model_agreement_majority():
    candidates = {
        "persistence": "STABLE",
        "trend": "STABLE",
        "recurrence": "VOLATILE",
    }
    agreement = ModelCalibrator.calculate_model_agreement(candidates)
    assert agreement == 0.70


def test_model_agreement_divergent():
    candidates = {
        "persistence": "STABLE",
        "trend": "INCREASING",
        "recurrence": "DECREASING",
    }
    agreement = ModelCalibrator.calculate_model_agreement(candidates)
    assert agreement == 0.35


def test_calibrator_synthetic_evaluation():
    calibrator = ModelCalibrator()
    calibrator._evaluation_records.clear()
    calibrator.record_evaluation(
        prediction_id="PRD-001",
        target="ACTIVITY_STATE",
        forecast_state="INCREASING",
        actual_state="INCREASING",
        absolute_error=0.05,
    )
    calibrator.record_evaluation(
        prediction_id="PRD-002",
        target="ACTIVITY_STATE",
        forecast_state="STABLE",
        actual_state="INCREASING",
        absolute_error=0.25,
    )

    metrics = calibrator.get_evaluation_metrics()
    assert metrics.total_evaluated == 2
    assert metrics.mean_absolute_error == 0.15
    assert metrics.directional_accuracy == 0.50

