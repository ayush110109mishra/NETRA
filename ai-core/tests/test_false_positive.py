"""
Test suite for NETRA Phase 4 False-Positive Controls.
Verifies that isolated single-event sensor glitches do not cause runaway risk or high confirmation,
and that analytical anomalies are never mapped directly to threat/hostile classification.
"""

from datetime import datetime, timezone
import pytest
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent, EventSource
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from models.anomaly_intelligence import (
    AnomalyAnalyzeRequest,
    AnomalyPersistenceState,
    AnomalyConfirmationLevel,
)
from intelligence.anomaly_intelligence import AnomalyIntelligenceEngine
from simulation.synthetic_data import get_anomaly_scenario


def test_false_positive_single_glitch_bounded():
    # Load Scenario 10 (Single corrupted reading 220 km/h from unverified sensor)
    scen = get_anomaly_scenario("scenario_10_false_positive")
    assert scen is not None

    engine = AnomalyIntelligenceEngine()
    req = AnomalyAnalyzeRequest(
        entity_id=scen["entity_id"],
        events=[e.model_dump() for e in scen["events"]],
    )
    res = engine.analyze_entity_anomaly(req)

    # Persistence should NOT be persistent or escalating
    assert res.persistence.state in [AnomalyPersistenceState.TRANSIENT, AnomalyPersistenceState.DECLINING]

    # Confirmation must not be strongly corroborated
    assert res.anomaly.confirmation in [AnomalyConfirmationLevel.UNCONFIRMED, AnomalyConfirmationLevel.SUPPORTED]

    # Analytical risk must be bounded and not CRITICAL
    assert res.risk.score < 0.75

    # Verification: Assessment must maintain analytical neutrality (never declare enemy/hostile)
    summary_text = res.assessment.operational_summary.upper()
    assert "HOSTILE" not in summary_text or "POSTURE" in summary_text
    assert "ENEMY" not in summary_text
    assert "TARGET DESTROY" not in summary_text
