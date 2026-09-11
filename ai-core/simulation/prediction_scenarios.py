"""
Predefined Synthetic Scenarios for NETRA Phase 6 Predictive Intelligence & Forecasting.
Provides 16 deterministic scenarios covering stability, escalation, decaying risk,
cyclical patterns, regime shifts, cold start, limited history, sensor conflict,
ensemble agreement/divergence, sensor dropout, burst activity, and spatial trajectories.
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from models.predictive_intelligence import (
    DataSufficiency,
    ForecastHorizon,
    ForecastState,
    PredictiveTarget,
)


def _base_time() -> datetime:
    """Fixed reference timestamp for deterministic scenario evaluation."""
    return datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)


def get_all_prediction_scenarios() -> Dict[str, Dict[str, Any]]:
    """Returns all 16 Phase 6 operational test scenarios."""
    t0 = _base_time()

    scenarios: Dict[str, Dict[str, Any]] = {
        # 1. Stable Entity
        "scenario_1_stable_entity": {
            "name": "Stable Entity (Nominal Activity)",
            "description": "Entity exhibits consistent nominal activity telemetry across 10 regular observation cycles.",
            "entity_id": "PRED-ENT-01",
            "target": PredictiveTarget.ACTIVITY_STATE.value,
            "horizon": ForecastHorizon.SHORT.value,
            "reference_time": t0 + timedelta(minutes=90),
            "expected_forecast_state": ForecastState.STABLE.value,
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S1-{i}",
                    "event_type": "ROUTINE_TELEMETRY",
                    "timestamp": t0 + timedelta(minutes=i * 10),
                    "location": {"latitude": 34.050, "longitude": 74.800},
                    "attributes": {"activity_level": 0.50 + (0.01 if i % 2 == 0 else -0.01), "speed": 40.0},
                }
                for i in range(10)
            ],
        },

        # 2. Escalating Activity
        "scenario_2_escalating_activity": {
            "name": "Escalating Activity Trend",
            "description": "Monotonically rising activity telemetry indicating impending operational surge.",
            "entity_id": "PRED-ENT-02",
            "target": PredictiveTarget.ACTIVITY_STATE.value,
            "horizon": ForecastHorizon.SHORT.value,
            "reference_time": t0 + timedelta(minutes=90),
            "expected_forecast_state": ForecastState.INCREASING.value,
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S2-{i}",
                    "event_type": "TACTICAL_SURVEILLANCE",
                    "timestamp": t0 + timedelta(minutes=i * 10),
                    "location": {"latitude": 34.050, "longitude": 74.800 + i * 0.01},
                    "attributes": {"activity_level": round(0.25 + i * 0.075, 3), "speed": 45.0},
                }
                for i in range(10)
            ],
        },

        # 3. Decaying Risk
        "scenario_3_decaying_risk": {
            "name": "Decaying Risk Trajectory",
            "description": "Steady reduction in operational threat score following tactical standoff resolution.",
            "entity_id": "PRED-ENT-03",
            "target": PredictiveTarget.RISK_TREND.value,
            "horizon": ForecastHorizon.MEDIUM.value,
            "reference_time": t0 + timedelta(minutes=90),
            "expected_forecast_state": ForecastState.FALLING.value,
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S3-{i}",
                    "event_type": "THREAT_MONITORING",
                    "timestamp": t0 + timedelta(minutes=i * 10),
                    "location": {"latitude": 34.050, "longitude": 74.800},
                    "attributes": {"risk_score": round(0.90 - i * 0.075, 3), "activity_level": 0.40},
                }
                for i in range(10)
            ],
        },

        # 4. Cyclical Patrol
        "scenario_4_cyclical_patrol": {
            "name": "Cyclical Patrol Waypoint Recurrence",
            "description": "Repetitive patrol waypoint reporting exhibiting regular periodic recurrence intervals.",
            "entity_id": "PRED-ENT-04",
            "target": PredictiveTarget.EVENT_TYPE_RECURRENCE.value,
            "horizon": ForecastHorizon.SHORT.value,
            "reference_time": t0 + timedelta(hours=5),
            "expected_forecast_state": ForecastState.RECURRING.value,
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S4-{i}",
                    "event_type": "PATROL_WAYPOINT_CHECK",
                    "timestamp": t0 + timedelta(minutes=i * 30),
                    "location": {"latitude": 34.050 + (i % 3) * 0.01, "longitude": 74.800},
                    "attributes": {"activity_level": 0.55, "speed": 35.0},
                }
                for i in range(10)
            ],
        },

        # 5. Regime Shift
        "scenario_5_regime_shift": {
            "name": "Operational Regime Shift",
            "description": "Entity transitions sharply from dormant state to active tactical maneuver (delta slope >= 0.20).",
            "entity_id": "PRED-ENT-05",
            "target": PredictiveTarget.BEHAVIORAL_STATE.value,
            "horizon": ForecastHorizon.SHORT.value,
            "reference_time": t0 + timedelta(minutes=90),
            "expected_forecast_state": ForecastState.REGIME_CHANGE.value,
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S5-{i}",
                    "event_type": "RADAR_TRACK",
                    "timestamp": t0 + timedelta(minutes=i * 10),
                    "location": {"latitude": 34.050, "longitude": 74.800},
                    "attributes": {
                        "activity_level": 0.20 if i < 5 else round(0.40 + (i - 4) * 0.11, 3),
                        "speed": 10.0 if i < 5 else 65.0,
                    },
                }
                for i in range(10)
            ],
        },


        # 6. Cold Start Entity
        "scenario_6_cold_start_entity": {
            "name": "Cold Start Entity (< 3 Observations)",
            "description": "Newly detected entity with only 2 observation points, triggering cold-start safety fallback.",
            "entity_id": "PRED-ENT-06",
            "target": PredictiveTarget.ACTIVITY_STATE.value,
            "horizon": ForecastHorizon.SHORT.value,
            "reference_time": t0 + timedelta(minutes=20),
            "expected_forecast_state": ForecastState.UNKNOWN.value,
            "expected_sufficiency": DataSufficiency.INSUFFICIENT.value,
            "events": [
                {
                    "event_id": "EVT-S6-1",
                    "event_type": "INITIAL_CONTACT",
                    "timestamp": t0,
                    "location": {"latitude": 34.050, "longitude": 74.800},
                    "attributes": {"activity_level": 0.60},
                },
                {
                    "event_id": "EVT-S6-2",
                    "event_type": "SECONDARY_CONTACT",
                    "timestamp": t0 + timedelta(minutes=10),
                    "location": {"latitude": 34.052, "longitude": 74.802},
                    "attributes": {"activity_level": 0.65},
                },
            ],
        },

        # 7. Limited History
        "scenario_7_limited_history": {
            "name": "Limited Observation History (3-5 Observations)",
            "description": "Entity has 4 recorded observations; predictions capped at 0.55 confidence.",
            "entity_id": "PRED-ENT-07",
            "target": PredictiveTarget.ACTIVITY_STATE.value,
            "horizon": ForecastHorizon.SHORT.value,
            "reference_time": t0 + timedelta(minutes=40),
            "expected_forecast_state": ForecastState.STABLE.value,
            "expected_sufficiency": DataSufficiency.LIMITED.value,
            "events": [
                {
                    "event_id": f"EVT-S7-{i}",
                    "event_type": "SURVEILLANCE_CONTACT",
                    "timestamp": t0 + timedelta(minutes=i * 10),
                    "location": {"latitude": 34.050, "longitude": 74.800},
                    "attributes": {"activity_level": 0.50},
                }
                for i in range(4)
            ],
        },

        # 8. High Sensor Conflict
        "scenario_8_high_sensor_conflict": {
            "name": "High Multi-Sensor Conflict",
            "description": "Telemetry subject to inter-source contradiction resulting in widened uncertainty interval.",
            "entity_id": "PRED-ENT-08",
            "target": PredictiveTarget.ACTIVITY_STATE.value,
            "horizon": ForecastHorizon.SHORT.value,
            "reference_time": t0 + timedelta(minutes=60),
            "expected_forecast_state": ForecastState.STABLE.value,
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S8-{i}",
                    "event_type": "CONTRADICTORY_FEED",
                    "timestamp": t0 + timedelta(minutes=i * 10),
                    "location": {"latitude": 34.050, "longitude": 74.800},
                    "attributes": {"activity_level": 0.52},
                }
                for i in range(6)
            ],
        },

        # 9. Unanimous Ensemble
        "scenario_9_unanimous_ensemble": {
            "name": "Unanimous Forecasting Ensemble",
            "description": "Persistence, Trend, and Recurrence strategies achieve 100% agreement on future state.",
            "entity_id": "PRED-ENT-09",
            "target": PredictiveTarget.ACTIVITY_STATE.value,
            "horizon": ForecastHorizon.SHORT.value,
            "reference_time": t0 + timedelta(minutes=80),
            "expected_forecast_state": ForecastState.STABLE.value,
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S9-{i}",
                    "event_type": "ROUTINE_BEACON",
                    "timestamp": t0 + timedelta(minutes=i * 10),
                    "location": {"latitude": 34.050, "longitude": 74.800},
                    "attributes": {"activity_level": 0.50},
                }
                for i in range(8)
            ],
        },

        # 10. Divergent Ensemble (High Volatility)
        "scenario_10_divergent_ensemble": {
            "name": "Divergent Ensemble Under Volatility",
            "description": "High metric oscillation triggers VOLATILE state projection with widened uncertainty interval.",
            "entity_id": "PRED-ENT-10",
            "target": PredictiveTarget.ACTIVITY_STATE.value,
            "horizon": ForecastHorizon.SHORT.value,
            "reference_time": t0 + timedelta(minutes=80),
            "expected_forecast_state": ForecastState.VOLATILE.value,
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S10-{i}",
                    "event_type": "ERRATIC_BEACON",
                    "timestamp": t0 + timedelta(minutes=i * 10),
                    "location": {"latitude": 34.050, "longitude": 74.800},
                    "attributes": {"activity_level": 0.15 if i % 2 == 0 else 0.90},
                }
                for i in range(8)
            ],
        },

        # 11. Sensor Dropout (Temporal Gap)
        "scenario_11_sensor_dropout": {
            "name": "Sensor Dropout / Telemetry Gap",
            "description": "Extended gap of 8 hours before latest evaluation time increases temporal uncertainty.",
            "entity_id": "PRED-ENT-11",
            "target": PredictiveTarget.ACTIVITY_STATE.value,
            "horizon": ForecastHorizon.LONG.value,
            "reference_time": t0 + timedelta(hours=12),
            "expected_forecast_state": ForecastState.STABLE.value,
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S11-{i}",
                    "event_type": "INTERMITTENT_FEED",
                    "timestamp": t0 + timedelta(minutes=i * 15),
                    "location": {"latitude": 34.050, "longitude": 74.800},
                    "attributes": {"activity_level": 0.48},
                }
                for i in range(6)
            ],
        },

        # 12. Burst Activity
        "scenario_12_burst_activity": {
            "name": "Burst Activity Cluster",
            "description": "Dense cluster of 8 observations in rapid 2-minute succession.",
            "entity_id": "PRED-ENT-12",
            "target": PredictiveTarget.ACTIVITY_STATE.value,
            "horizon": ForecastHorizon.SHORT.value,
            "reference_time": t0 + timedelta(minutes=5),
            "expected_forecast_state": ForecastState.STABLE.value,
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S12-{i}",
                    "event_type": "HIGH_RATE_PULSE",
                    "timestamp": t0 + timedelta(seconds=i * 15),
                    "location": {"latitude": 34.050, "longitude": 74.800},
                    "attributes": {"activity_level": 0.70},
                }
                for i in range(8)
            ],
        },

        # 13. Spatial Loitering
        "scenario_13_spatial_loitering": {
            "name": "Spatial Loitering Pattern",
            "description": "Low speed circular telemetry indicating localized loitering behavior.",
            "entity_id": "PRED-ENT-13",
            "target": PredictiveTarget.SPATIAL_STATE.value,
            "horizon": ForecastHorizon.SHORT.value,
            "reference_time": t0 + timedelta(minutes=70),
            "expected_forecast_state": "LOITERING",
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S13-{i}",
                    "event_type": "SLOW_PATROL",
                    "timestamp": t0 + timedelta(minutes=i * 10),
                    "location": {"latitude": 34.050, "longitude": 74.800},
                    "attributes": {"speed": 12.0, "activity_level": 0.40},
                }
                for i in range(7)
            ],
        },

        # 14. Directed Incursion
        "scenario_14_directed_incursion": {
            "name": "Directed Incursion Transit",
            "description": "High sustained velocity along direct vector indicating intentional transit.",
            "entity_id": "PRED-ENT-14",
            "target": PredictiveTarget.SPATIAL_STATE.value,
            "horizon": ForecastHorizon.SHORT.value,
            "reference_time": t0 + timedelta(minutes=70),
            "expected_forecast_state": "DIRECTED_TRANSIT",
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S14-{i}",
                    "event_type": "HIGH_SPEED_TRANSIT",
                    "timestamp": t0 + timedelta(minutes=i * 10),
                    "location": {"latitude": 34.050 + i * 0.05, "longitude": 74.800 + i * 0.05},
                    "attributes": {"speed": 75.0, "activity_level": 0.65},
                }
                for i in range(7)
            ],
        },

        # 15. Spurious Anomaly Spike
        "scenario_15_spurious_anomaly": {
            "name": "Spurious Single Spike (Anti-Alarm)",
            "description": "Isolated single observation spike fails trend persistence check and does not trigger sustained alert.",
            "entity_id": "PRED-ENT-15",
            "target": PredictiveTarget.ANOMALY_STATE.value,
            "horizon": ForecastHorizon.SHORT.value,
            "reference_time": t0 + timedelta(minutes=70),
            "expected_forecast_state": ForecastState.NORMAL.value,
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S15-{i}",
                    "event_type": "RADAR_ECHO",
                    "timestamp": t0 + timedelta(minutes=i * 10),
                    "location": {"latitude": 34.050, "longitude": 74.800},
                    "attributes": {
                        "anomaly_score": 0.95 if i == 5 else 0.15,
                        "activity_level": 0.40,
                    },
                }
                for i in range(8)
            ],
        },

        # 16. Mixed Quality Multi-Sensor
        "scenario_16_mixed_quality_forecast": {
            "name": "Mixed Quality Multi-Sensor Feeds",
            "description": "Heterogeneous observations with calibrated confidence and empirical bounds.",
            "entity_id": "PRED-ENT-16",
            "target": PredictiveTarget.ACTIVITY_STATE.value,
            "horizon": ForecastHorizon.MEDIUM.value,
            "reference_time": t0 + timedelta(minutes=90),
            "expected_forecast_state": ForecastState.STABLE.value,
            "expected_sufficiency": DataSufficiency.SUFFICIENT.value,
            "events": [
                {
                    "event_id": f"EVT-S16-{i}",
                    "event_type": "MULTI_SENSOR_TELEMETRY",
                    "timestamp": t0 + timedelta(minutes=i * 10),
                    "location": {"latitude": 34.050, "longitude": 74.800},
                    "attributes": {
                        "activity_level": 0.50 + (0.02 if i % 2 == 0 else -0.02),
                        "sensor_quality": 0.45 + (i * 0.05),
                    },
                }
                for i in range(10)
            ],
        },
    }

    return scenarios


def get_prediction_scenario(scenario_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single Phase 6 scenario by its identifier."""
    return get_all_prediction_scenarios().get(scenario_id)
