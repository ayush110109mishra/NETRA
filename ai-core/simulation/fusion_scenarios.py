"""
Predefined Synthetic Scenarios for NETRA Phase 5 Multi-Source Intelligence Fusion.
Provides 14 deterministic scenarios covering agreement, contradictions, clock skew,
source dropout, cold start, duplicate feeds, ambiguous entity resolution, and mixed quality.
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional


def _base_time() -> datetime:
    """Fixed reference timestamp for deterministic scenario reproducibility."""
    return datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)


def get_all_fusion_scenarios() -> Dict[str, Dict[str, Any]]:
    """Generates all 14 Phase 5 operational test scenarios."""
    t0 = _base_time()

    scenarios = {
        # 1. all_sources_agree
        "scenario_1_all_sources_agree": {
            "name": "All Sources Agree (Full Consensus)",
            "description": "Three independent sensors (RADAR, OPTICAL, TELEMETRY) observe ENTITY-07 at same location and speed.",
            "target_entity_id": "ENTITY-07",
            "observations": [
                {
                    "source_id": "RADAR_01",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0500, "longitude": 74.8000, "sector_id": "SECTOR_ALPHA"},
                    "velocity": {"speed_kmh": 60.0, "heading_deg": 90.0},
                    "event_type": "CONVOY_MOVEMENT",
                    "quality": 0.95,
                },
                {
                    "source_id": "OPTICAL_01",
                    "source_type": "OPTICAL",
                    "timestamp": t0 + timedelta(seconds=2),
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0502, "longitude": 74.8003, "sector_id": "SECTOR_ALPHA"},
                    "velocity": {"speed_kmh": 59.5, "heading_deg": 91.0},
                    "event_type": "CONVOY_MOVEMENT",
                    "quality": 0.92,
                },
                {
                    "source_id": "TELEMETRY_01",
                    "source_type": "TELEMETRY",
                    "timestamp": t0 + timedelta(seconds=1),
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0501, "longitude": 74.8001, "sector_id": "SECTOR_ALPHA"},
                    "velocity": {"speed_kmh": 60.2, "heading_deg": 90.0},
                    "event_type": "CONVOY_MOVEMENT",
                    "quality": 0.98,
                },
            ],
        },

        # 2. position_conflict
        "scenario_2_position_conflict": {
            "name": "Position Conflict",
            "description": "Two sensors report positions separated by > 35km. Discrepancy is recorded without silent deletion.",
            "target_entity_id": "ENTITY-07",
            "observations": [
                {
                    "source_id": "RADAR_01",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0500, "longitude": 74.8000, "sector_id": "SECTOR_ALPHA"},
                    "velocity": {"speed_kmh": 50.0, "heading_deg": 45.0},
                    "event_type": "PATROL",
                },
                {
                    "source_id": "SENSOR_B",
                    "source_type": "SENSOR_B",
                    "timestamp": t0 + timedelta(seconds=5),
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.4000, "longitude": 75.1500, "sector_id": "SECTOR_EAST"},
                    "velocity": {"speed_kmh": 52.0, "heading_deg": 45.0},
                    "event_type": "PATROL",
                },
            ],
        },

        # 3. velocity_conflict
        "scenario_3_velocity_conflict": {
            "name": "Velocity Conflict",
            "description": "Sensors report wildly incompatible velocities (30 km/h vs 140 km/h).",
            "target_entity_id": "ENTITY-07",
            "observations": [
                {
                    "source_id": "RADAR_01",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0500, "longitude": 74.8000},
                    "velocity": {"speed_kmh": 30.0, "heading_deg": 10.0},
                    "event_type": "PATROL",
                },
                {
                    "source_id": "SENSOR_A",
                    "source_type": "SENSOR_A",
                    "timestamp": t0 + timedelta(seconds=2),
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0505, "longitude": 74.8008},
                    "velocity": {"speed_kmh": 140.0, "heading_deg": 190.0},
                    "event_type": "PATROL",
                },
            ],
        },

        # 4. timestamp_skew
        "scenario_4_timestamp_skew": {
            "name": "Timestamp Skew",
            "description": "Sensors report same synthetic entity with small clock skew (3s delta), successfully aligned.",
            "target_entity_id": "ENTITY-07",
            "observations": [
                {
                    "source_id": "RADAR_01",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0500, "longitude": 74.8000},
                    "velocity": {"speed_kmh": 55.0},
                },
                {
                    "source_id": "OPTICAL_01",
                    "source_type": "OPTICAL",
                    "timestamp": t0 + timedelta(seconds=3),
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0502, "longitude": 74.8002},
                    "velocity": {"speed_kmh": 54.8},
                },
            ],
        },

        # 5. source_dropout
        "scenario_5_source_dropout": {
            "name": "Source Dropout",
            "description": "SENSOR_B suffers telemetry dropout; remaining sensor data continues fusion.",
            "target_entity_id": "ENTITY-07",
            "observations": [
                {
                    "source_id": "RADAR_01",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0500, "longitude": 74.8000},
                    "velocity": {"speed_kmh": 50.0},
                },
                {
                    "source_id": "SENSOR_B",
                    "source_type": "SENSOR_B",
                    "timestamp": t0 - timedelta(minutes=10),
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0450, "longitude": 74.7950},
                    "attributes": {"dropout": True},
                },
            ],
        },

        # 6. low_reliability_source
        "scenario_6_low_reliability_source": {
            "name": "Low Reliability Source Disagreement",
            "description": "Unverified acoustic sensor (rel=0.35) disagrees with primary radar (rel=0.90). Disagreement preserved.",
            "target_entity_id": "ENTITY-07",
            "observations": [
                {
                    "source_id": "RADAR_01",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0500, "longitude": 74.8000},
                    "velocity": {"speed_kmh": 60.0},
                    "event_type": "PATROL",
                },
                {
                    "source_id": "LOW_REL_SENSOR",
                    "source_type": "SENSOR_B",
                    "timestamp": t0 + timedelta(seconds=2),
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.1500, "longitude": 74.9200},
                    "velocity": {"speed_kmh": 120.0},
                    "event_type": "AIR_INTERCEPT",
                },
            ],
        },

        # 7. three_source_corroboration
        "scenario_7_three_source_corroboration": {
            "name": "Three Independent Sources Corroboration",
            "description": "RADAR, OPTICAL, and SIGNAL from 3 independent groups confirm activity.",
            "target_entity_id": "ENTITY-07",
            "observations": [
                {
                    "source_id": "RADAR_01",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0500, "longitude": 74.8000},
                    "velocity": {"speed_kmh": 65.0},
                },
                {
                    "source_id": "OPTICAL_01",
                    "source_type": "OPTICAL",
                    "timestamp": t0 + timedelta(seconds=1),
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0501, "longitude": 74.8002},
                    "velocity": {"speed_kmh": 65.2},
                },
                {
                    "source_id": "SIGNAL_01",
                    "source_type": "SIGNAL",
                    "timestamp": t0 + timedelta(seconds=2),
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0510, "longitude": 74.8010},
                    "velocity": {"speed_kmh": 64.0},
                },
            ],
        },

        # 8. duplicate_same_source
        "scenario_8_duplicate_same_source": {
            "name": "Duplicate Same Source Retransmissions",
            "description": "RADAR_01 and retransmission RADAR_01_DUP share independence group. Independence count remains 1.",
            "target_entity_id": "ENTITY-07",
            "observations": [
                {
                    "source_id": "RADAR_01",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0500, "longitude": 74.8000},
                    "velocity": {"speed_kmh": 50.0},
                },
                {
                    "source_id": "RADAR_01_DUP",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0500, "longitude": 74.8000},
                    "velocity": {"speed_kmh": 50.0},
                },
            ],
        },

        # 9. ambiguous_entity_resolution
        "scenario_9_ambiguous_entity_resolution": {
            "name": "Ambiguous Entity Resolution",
            "description": "Generic observation with unmapped hint located equidistant between entities. Status AMBIGUOUS.",
            "target_entity_id": None,
            "observations": [
                {
                    "source_id": "RADAR_01",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "entity_hint": "UNKNOWN_BOGEY_99",
                    "position": {"latitude": 34.0500, "longitude": 74.8000},
                    "velocity": {"speed_kmh": 50.0},
                },
            ],
        },

        # 10. successful_entity_resolution
        "scenario_10_successful_entity_resolution": {
            "name": "Successful Multi-Source Entity Resolution",
            "description": "Source track IDs R-104, O-771, and T-22 all deterministically resolve to ENTITY-07.",
            "target_entity_id": "ENTITY-07",
            "observations": [
                {
                    "source_id": "RADAR_01",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "entity_hint": "R-104",
                    "position": {"latitude": 34.0500, "longitude": 74.8000},
                    "velocity": {"speed_kmh": 58.0},
                },
                {
                    "source_id": "OPTICAL_01",
                    "source_type": "OPTICAL",
                    "timestamp": t0 + timedelta(seconds=1),
                    "entity_hint": "O-771",
                    "position": {"latitude": 34.0502, "longitude": 74.8001},
                    "velocity": {"speed_kmh": 58.5},
                },
                {
                    "source_id": "TELEMETRY_01",
                    "source_type": "TELEMETRY",
                    "timestamp": t0 + timedelta(seconds=2),
                    "entity_hint": "T-22",
                    "position": {"latitude": 34.0501, "longitude": 74.8000},
                    "velocity": {"speed_kmh": 58.0},
                },
            ],
        },

        # 11. new_source_onboarding
        "scenario_11_new_source_onboarding": {
            "name": "New Source Cold-Start Onboarding",
            "description": "A previously unregistered sensor reports. Cold-start health created and confidence capped <= 0.35.",
            "target_entity_id": "ENTITY-07",
            "observations": [
                {
                    "source_id": "UNKNOWN_DRONE_FEED_X",
                    "source_type": "UNKNOWN",
                    "timestamp": t0,
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0500, "longitude": 74.8000},
                    "velocity": {"speed_kmh": 40.0},
                },
            ],
        },

        # 12. contradictory_event_type
        "scenario_12_contradictory_event_type": {
            "name": "Contradictory Event Type Reports",
            "description": "RADAR reports routine PATROL while SIGNAL reports RADAR_JAMMING. Contradiction flagged.",
            "target_entity_id": "ENTITY-07",
            "observations": [
                {
                    "source_id": "RADAR_01",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0500, "longitude": 74.8000},
                    "event_type": "ROUTINE_PATROL",
                },
                {
                    "source_id": "SIGNAL_01",
                    "source_type": "SIGNAL",
                    "timestamp": t0 + timedelta(seconds=2),
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0505, "longitude": 74.8005},
                    "event_type": "RADAR_JAMMING_ATTACK",
                },
            ],
        },

        # 13. stale_observation
        "scenario_13_stale_observation": {
            "name": "Stale Observation Fusion",
            "description": "One sensor reports telemetry from 3 hours prior. Freshness penalty applied.",
            "target_entity_id": "ENTITY-07",
            "observations": [
                {
                    "source_id": "RADAR_01",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0500, "longitude": 74.8000},
                    "velocity": {"speed_kmh": 60.0},
                },
                {
                    "source_id": "SENSOR_B",
                    "source_type": "SENSOR_B",
                    "timestamp": t0 - timedelta(hours=3),
                    "entity_hint": "ENTITY-07",
                    "position": {"latitude": 34.0200, "longitude": 74.7500},
                    "velocity": {"speed_kmh": 30.0},
                },
            ],
        },

        # 14. mixed_quality_fusion
        "scenario_14_mixed_quality_fusion": {
            "name": "Mixed Quality Multi-Source Fusion",
            "description": "Realistic operational operational telemetry mix: 4 sensors, varying accuracy, unit formats, and one conflict.",
            "target_entity_id": "ENTITY-07",
            "observations": [
                {
                    "source_id": "RADAR_01",
                    "source_type": "RADAR",
                    "timestamp": t0,
                    "track_id": "R-104",
                    "lat": 34.0500,
                    "lon": 74.8000,
                    "speed_knots": 32.4,  # Knots to km/h conversion
                    "heading": 90.0,
                    "event": "PATROL",
                },
                {
                    "source_id": "OPTICAL_01",
                    "source_type": "OPTICAL",
                    "timestamp": t0 + timedelta(seconds=2),
                    "object_id": "O-771",
                    "latitude": 34.0502,
                    "longitude": 74.8001,
                    "velocity_mps": 16.67,  # m/s to km/h conversion
                    "category": "PATROL",
                },
                {
                    "source_id": "TELEMETRY_01",
                    "source_type": "TELEMETRY",
                    "timestamp": t0 + timedelta(seconds=1),
                    "entity_id": "T-22",
                    "position": {"latitude": 34.0501, "longitude": 74.8000},
                    "speed": 60.0,
                },
                {
                    "source_id": "LOW_REL_SENSOR",
                    "source_type": "SENSOR_B",
                    "timestamp": t0 + timedelta(seconds=3),
                    "entity_hint": "ENTITY-07",
                    "lat": 34.1200,  # Slight spatial disagreement
                    "lon": 74.8900,
                    "speed": 62.0,
                },
            ],
        },
    }
    return scenarios


def get_fusion_scenario(scenario_id: str) -> Optional[Dict[str, Any]]:
    """Lookup a synthetic Phase 5 fusion scenario by exact or partial key."""
    scenarios = get_all_fusion_scenarios()
    clean_id = scenario_id.lower().strip()
    if clean_id in scenarios:
        return scenarios[clean_id]

    # Try matching without prefix e.g. "scenario_1" or "all_sources_agree"
    for k, v in scenarios.items():
        if clean_id == k.replace("scenario_", "") or clean_id in k:
            return v
    return None
