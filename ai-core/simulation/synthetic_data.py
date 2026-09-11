"""
Predefined synthetic operational scenarios for NETRA Intelligence Core.
Includes both Phase 1 single-event scenarios and Phase 2 multi-event scenarios.
All coordinates, entities, and events are strictly SYNTHETIC / FICTIONAL for testing and validation.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from models.common import Coordinates, Allegiance, SeverityLevel
from models.input import (
    IntelligenceAnalyzeRequest,
    EventInput,
    EntityInput,
    AttributesInput,
    HistoricalContextInput,
    ContextEntityInput,
    ContextEventInput,
)
from models.event_intelligence import (
    MultiEventAnalyzeRequest,
    MultiEventContextInput,
    CanonicalEvent,
    EventSource,
)
from models.entity_intelligence import CanonicalEntity

# Reference synthetic timestamp
BASE_TIME = datetime(2026, 9, 11, 10, 30, 0, tzinfo=timezone.utc)

# ==============================================================================
# PHASE 1 SINGLE-EVENT SYNTHETIC SCENARIOS (PRESERVED 100%)
# ==============================================================================

# 1. SCENARIO 1: NORMAL ACTIVITY
SCENARIO_NORMAL = IntelligenceAnalyzeRequest(
    event=EventInput(
        event_id="EVT-SYNTH-001",
        event_type="movement",
        description="Routine synthetic logistics patrol traversing Sector Alpha",
        timestamp=BASE_TIME,
    ),
    entity=EntityInput(
        entity_id="ENTITY-SYNTH-010",
        entity_type="vehicle",
        callsign="CONVOY-LEAD",
        allegiance=Allegiance.FRIENDLY,
    ),
    timestamp=BASE_TIME,
    location=Coordinates(latitude=26.8467, longitude=80.9462, sector_id="SECTOR_ALPHA"),
    attributes=AttributesInput(
        speed=42.0,
        activity_level=0.30,
        heading_deg=85.0,
        sensor_count=3,
        signal_strength_dbm=-68.0,
    ),
    historical_context=HistoricalContextInput(
        previous_activity=0.32,
        historical_event_count=45,
        baseline_speed=40.0,
        deviation_history_count=0,
    ),
    context_entities=[],
    context_events=[],
)

# 2. SCENARIO 2: MODERATELY UNUSUAL ACTIVITY
SCENARIO_UNUSUAL = IntelligenceAnalyzeRequest(
    event=EventInput(
        event_id="EVT-SYNTH-002",
        event_type="movement",
        description="Patrol unit exhibiting moderate speed acceleration off standard schedule",
        timestamp=BASE_TIME,
    ),
    entity=EntityInput(
        entity_id="ENTITY-SYNTH-025",
        entity_type="vehicle",
        callsign="SENTINEL-4",
        allegiance=Allegiance.NEUTRAL,
    ),
    timestamp=BASE_TIME,
    location=Coordinates(latitude=26.8520, longitude=80.9510, sector_id="SECTOR_ALPHA"),
    attributes=AttributesInput(
        speed=52.0,
        activity_level=0.55,
        heading_deg=110.0,
        sensor_count=2,
        signal_strength_dbm=-75.0,
    ),
    historical_context=HistoricalContextInput(
        previous_activity=0.28,
        historical_event_count=30,
        baseline_speed=40.0,
        deviation_history_count=1,
    ),
    context_entities=[],
    context_events=[],
)

# 3. SCENARIO 3: STRONG DEVIATION FROM BASELINE (ANOMALOUS)
SCENARIO_ANOMALOUS = IntelligenceAnalyzeRequest(
    event=EventInput(
        event_id="EVT-SYNTH-003",
        event_type="patrol_deviation",
        description="Significant sudden surge in kinetic signature and speed without flight plan",
        timestamp=BASE_TIME,
    ),
    entity=EntityInput(
        entity_id="ENTITY-SYNTH-047",
        entity_type="aircraft",
        callsign="VECTOR-9",
        allegiance=Allegiance.UNKNOWN,
    ),
    timestamp=BASE_TIME,
    location=Coordinates(latitude=26.8850, longitude=80.9820, sector_id="SECTOR_BRAVO"),
    attributes=AttributesInput(
        speed=175.0,
        activity_level=0.82,
        heading_deg=225.0,
        sensor_count=4,
        signal_strength_dbm=-55.0,
    ),
    historical_context=HistoricalContextInput(
        previous_activity=0.25,
        historical_event_count=18,
        baseline_speed=110.0,
        deviation_history_count=2,
    ),
    context_entities=[],
    context_events=[],
)

# 4. SCENARIO 4: MULTIPLE CORRELATED EVENTS & HIGH RISK
SCENARIO_HIGH_RISK_CORRELATED = IntelligenceAnalyzeRequest(
    event=EventInput(
        event_id="EVT-SYNTH-004",
        event_type="perimeter_proximity",
        description="High-speed non-cooperative synthetic entity operating near sector perimeter",
        timestamp=BASE_TIME,
        priority_hint=SeverityLevel.HIGH,
    ),
    entity=EntityInput(
        entity_id="ENTITY-SYNTH-099",
        entity_type="vehicle",
        callsign="INTRUDER-MOCK",
        allegiance=Allegiance.SIMULATED_HOSTILE,
    ),
    timestamp=BASE_TIME,
    location=Coordinates(latitude=26.8900, longitude=80.9900, sector_id="SECTOR_BRAVO"),
    attributes=AttributesInput(
        speed=140.0,
        activity_level=0.95,
        heading_deg=180.0,
        sensor_count=5,
        signal_strength_dbm=-48.0,
    ),
    historical_context=HistoricalContextInput(
        previous_activity=0.15,
        historical_event_count=22,
        baseline_speed=40.0,
        deviation_history_count=4,
    ),
    context_entities=[
        ContextEntityInput(
            entity_id="ENTITY-SYNTH-098",
            entity_type="vehicle",
            location=Coordinates(latitude=26.8920, longitude=80.9915),
            last_seen=BASE_TIME,
            allegiance=Allegiance.SIMULATED_HOSTILE,
        )
    ],
    context_events=[
        ContextEventInput(
            event_id="EVT-SYNTH-003B",
            event_type="radar_anomaly",
            entity_id="ENTITY-SYNTH-099",
            location=Coordinates(latitude=26.8890, longitude=80.9880),
            timestamp=BASE_TIME,
            severity=SeverityLevel.HIGH,
        )
    ],
)

# 5. SCENARIO 5: INSUFFICIENT HISTORICAL INFORMATION (UNKNOWN)
SCENARIO_INSUFFICIENT_HISTORY = IntelligenceAnalyzeRequest(
    event=EventInput(
        event_id="EVT-SYNTH-005",
        event_type="sensor_ping",
        description="Initial telemetry contact from previously uncataloged synthetic platform",
        timestamp=BASE_TIME,
    ),
    entity=EntityInput(
        entity_id="ENTITY-SYNTH-NEW",
        entity_type="unknown",
        allegiance=Allegiance.UNKNOWN,
    ),
    timestamp=BASE_TIME,
    location=Coordinates(latitude=26.7500, longitude=80.8500),
    attributes=AttributesInput(
        speed=25.0,
        activity_level=0.50,
        sensor_count=1,
    ),
    historical_context=HistoricalContextInput(
        previous_activity=0.50,
        historical_event_count=0,
    ),
    context_entities=[],
    context_events=[],
)

# 6. SCENARIO 6: CONFLICTING SYNTHETIC SIGNALS
SCENARIO_CONFLICTING_SIGNALS = IntelligenceAnalyzeRequest(
    event=EventInput(
        event_id="EVT-SYNTH-006",
        event_type="movement",
        description="Synthetic platform with contradictory speed vs activity telemetry",
        timestamp=BASE_TIME,
    ),
    entity=EntityInput(
        entity_id="ENTITY-SYNTH-CONFL",
        entity_type="vehicle",
        callsign="GHOST-1",
        allegiance=Allegiance.UNKNOWN,
    ),
    timestamp=BASE_TIME,
    location=Coordinates(latitude=26.8100, longitude=80.9100, sector_id="SECTOR_ALPHA"),
    attributes=AttributesInput(
        speed=110.0,
        activity_level=0.01,
        sensor_count=0,
    ),
    historical_context=HistoricalContextInput(
        previous_activity=0.35,
        historical_event_count=6,
        baseline_speed=40.0,
    ),
    context_entities=[],
    context_events=[],
)

SCENARIOS_MAP: Dict[str, IntelligenceAnalyzeRequest] = {
    "normal": SCENARIO_NORMAL,
    "unusual": SCENARIO_UNUSUAL,
    "anomalous": SCENARIO_ANOMALOUS,
    "high_risk": SCENARIO_HIGH_RISK_CORRELATED,
    "insufficient_history": SCENARIO_INSUFFICIENT_HISTORY,
    "conflicting_signals": SCENARIO_CONFLICTING_SIGNALS,
}


def get_synthetic_scenario(scenario_id: str) -> IntelligenceAnalyzeRequest:
    """Retrieve Phase 1 single-event scenario by key."""
    if scenario_id not in SCENARIOS_MAP:
        raise KeyError(f"Scenario '{scenario_id}' not found. Available: {list(SCENARIOS_MAP.keys())}")
    return SCENARIOS_MAP[scenario_id]


def get_all_synthetic_scenarios() -> Dict[str, Dict[str, Any]]:
    """Return dictionary of scenario metadata for testing."""
    return {
        key: {
            "name": key,
            "description": req.event.description,
            "entity_id": req.entity.entity_id,
            "event_type": req.event.event_type,
            "data_classification": "SYNTHETIC",
        }
        for key, req in SCENARIOS_MAP.items()
    }


# ==============================================================================
# PHASE 2 MULTI-EVENT SYNTHETIC SCENARIOS (10 SCENARIOS)
# ==============================================================================

# 1. SCENARIO 1: Normal Isolated Events (no strong correlations)
MULTI_SCENARIO_ISOLATED = MultiEventAnalyzeRequest(
    events=[
        {
            "event_id": "EVT-M-001",
            "event_type": "movement",
            "timestamp": BASE_TIME.isoformat(),
            "location": {"latitude": 26.8400, "longitude": 80.9400},
            "entity_ids": ["ENTITY-ALPHA"],
            "attributes": {"speed": 35.0, "activity_level": 0.25},
        },
        {
            "event_id": "EVT-M-002",
            "event_type": "sensor_ping",
            "timestamp": (BASE_TIME + timedelta(hours=6)).isoformat(),
            "location": {"latitude": 27.5000, "longitude": 81.6000},  # ~100 km away
            "entity_ids": ["ENTITY-BETA"],
            "attributes": {"speed": 20.0, "activity_level": 0.20},
        },
    ],
    context=MultiEventContextInput(
        sector_id="SECTOR_ALPHA",
        historical_baseline_activity=0.25,
    ),
)

# 2. SCENARIO 2: Temporal Cluster (burst within 10 minutes)
MULTI_SCENARIO_TEMPORAL_CLUSTER = MultiEventAnalyzeRequest(
    events=[
        {
            "event_id": f"EVT-BURST-{i}",
            "event_type": "sensor_ping",
            "timestamp": (BASE_TIME + timedelta(minutes=i * 2)).isoformat(),
            "location": {"latitude": 26.8500 + (i * 0.002), "longitude": 80.9500 + (i * 0.002)},
            "entity_ids": ["ENTITY-RADAR-1"],
            "attributes": {"speed": 0.0, "activity_level": 0.65},
        }
        for i in range(4)
    ],
    context=MultiEventContextInput(sector_id="SECTOR_ALPHA", historical_baseline_activity=0.30),
)

# 3. SCENARIO 3: Spatial Cluster (events within 1 km over 1 hour)
MULTI_SCENARIO_SPATIAL_CLUSTER = MultiEventAnalyzeRequest(
    events=[
        {
            "event_id": f"EVT-SPATIAL-{i}",
            "event_type": "movement",
            "timestamp": (BASE_TIME + timedelta(minutes=i * 20)).isoformat(),
            "location": {"latitude": 26.8800 + (i * 0.001), "longitude": 80.9800 + (i * 0.001)},
            "entity_ids": [f"ENTITY-PATROL-{i}"],
            "attributes": {"speed": 40.0, "activity_level": 0.50},
        }
        for i in range(3)
    ],
    context=MultiEventContextInput(sector_id="SECTOR_BRAVO"),
)

# 4. SCENARIO 4: Same-Entity Sequence (A -> B -> C sequential progression)
MULTI_SCENARIO_SAME_ENTITY_SEQUENCE = MultiEventAnalyzeRequest(
    events=[
        {
            "event_id": "EVT-SEQ-001",
            "event_type": "movement",
            "timestamp": BASE_TIME.isoformat(),
            "location": {"latitude": 26.8400, "longitude": 80.9400},
            "entity_ids": ["ENTITY-TRACK-99"],
            "attributes": {"speed": 45.0, "activity_level": 0.40},
        },
        {
            "event_id": "EVT-SEQ-002",
            "event_type": "patrol_deviation",
            "timestamp": (BASE_TIME + timedelta(minutes=15)).isoformat(),
            "location": {"latitude": 26.8480, "longitude": 80.9480},
            "entity_ids": ["ENTITY-TRACK-99"],
            "attributes": {"speed": 75.0, "activity_level": 0.70},
        },
        {
            "event_id": "EVT-SEQ-003",
            "event_type": "perimeter_proximity",
            "timestamp": (BASE_TIME + timedelta(minutes=28)).isoformat(),
            "location": {"latitude": 26.8550, "longitude": 80.9550},
            "entity_ids": ["ENTITY-TRACK-99"],
            "attributes": {"speed": 95.0, "activity_level": 0.90},
        },
    ],
    context=MultiEventContextInput(sector_id="SECTOR_ALPHA"),
)

# 5. SCENARIO 5: Duplicate Events (exact duplicate and near duplicate)
MULTI_SCENARIO_DUPLICATES = MultiEventAnalyzeRequest(
    events=[
        {
            "event_id": "EVT-ORIG-001",
            "event_type": "movement",
            "timestamp": BASE_TIME.isoformat(),
            "location": {"latitude": 26.8467, "longitude": 80.9462},
            "entity_ids": ["ENTITY-CONVOY"],
            "attributes": {"speed": 40.0, "activity_level": 0.35},
        },
        # Exact duplicate
        {
            "event_id": "EVT-DUP-001",
            "event_type": "movement",
            "timestamp": (BASE_TIME + timedelta(seconds=2)).isoformat(),
            "location": {"latitude": 26.84671, "longitude": 80.94621},
            "entity_ids": ["ENTITY-CONVOY"],
            "attributes": {"speed": 40.0, "activity_level": 0.35},
        },
        # Near duplicate (within 30s, 100m)
        {
            "event_id": "EVT-DUP-002",
            "event_type": "movement",
            "timestamp": (BASE_TIME + timedelta(seconds=25)).isoformat(),
            "location": {"latitude": 26.8475, "longitude": 80.9468},
            "entity_ids": ["ENTITY-CONVOY"],
            "attributes": {"speed": 42.0, "activity_level": 0.36},
        },
    ]
)

# 6. SCENARIO 6: Strongly Correlated Multi-Event Pattern
MULTI_SCENARIO_STRONG_CORRELATION = MultiEventAnalyzeRequest(
    events=[
        {
            "event_id": "EVT-STRONG-1",
            "event_type": "movement",
            "timestamp": BASE_TIME.isoformat(),
            "location": {"latitude": 26.8800, "longitude": 80.9800},
            "entity_ids": ["ENTITY-HOSTILE-1"],
            "attributes": {"speed": 60.0, "activity_level": 0.65},
        },
        {
            "event_id": "EVT-STRONG-2",
            "event_type": "patrol_deviation",
            "timestamp": (BASE_TIME + timedelta(minutes=10)).isoformat(),
            "location": {"latitude": 26.8840, "longitude": 80.9830},
            "entity_ids": ["ENTITY-HOSTILE-1"],
            "attributes": {"speed": 85.0, "activity_level": 0.80},
        },
        {
            "event_id": "EVT-STRONG-3",
            "event_type": "perimeter_proximity",
            "timestamp": (BASE_TIME + timedelta(minutes=22)).isoformat(),
            "location": {"latitude": 26.8890, "longitude": 80.9870},
            "entity_ids": ["ENTITY-HOSTILE-1"],
            "attributes": {"speed": 110.0, "activity_level": 0.95},
        },
    ],
    context=MultiEventContextInput(
        sector_id="SECTOR_BRAVO",
        historical_baseline_activity=0.25,
        recent_baseline_activity=0.75,
    ),
)

# 7. SCENARIO 7: Weak Correlation (different entities, distant time, moderate space)
MULTI_SCENARIO_WEAK_CORRELATION = MultiEventAnalyzeRequest(
    events=[
        {
            "event_id": "EVT-WEAK-1",
            "event_type": "movement",
            "timestamp": BASE_TIME.isoformat(),
            "location": {"latitude": 26.8400, "longitude": 80.9400},
            "entity_ids": ["ENTITY-A"],
            "attributes": {"speed": 30.0, "activity_level": 0.3},
        },
        {
            "event_id": "EVT-WEAK-2",
            "event_type": "sensor_ping",
            "timestamp": (BASE_TIME + timedelta(minutes=90)).isoformat(),
            "location": {"latitude": 26.9200, "longitude": 80.9900},  # ~12 km away
            "entity_ids": ["ENTITY-B"],
            "attributes": {"speed": 15.0, "activity_level": 0.4},
        },
    ]
)

# 8. SCENARIO 8: False Correlation Case (Same location, BUT 8 hours later and different entities)
# CRITICAL: Must NOT produce a strong relationship!
MULTI_SCENARIO_FALSE_CORRELATION = MultiEventAnalyzeRequest(
    events=[
        {
            "event_id": "EVT-FALSE-LOC1",
            "event_type": "movement",
            "timestamp": BASE_TIME.isoformat(),
            "location": {"latitude": 26.8467, "longitude": 80.9462},
            "entity_ids": ["ENTITY-MORNING-PATROL"],
            "attributes": {"speed": 35.0, "activity_level": 0.30},
        },
        {
            "event_id": "EVT-FALSE-LOC2",
            "event_type": "movement",
            "timestamp": (BASE_TIME + timedelta(hours=8)).isoformat(),  # 8 hours later!
            "location": {"latitude": 26.8467, "longitude": 80.9462},  # Exactly same location!
            "entity_ids": ["ENTITY-NIGHT-MAINTENANCE"],               # Completely different entity!
            "attributes": {"speed": 10.0, "activity_level": 0.20},
        },
    ]
)

# 9. SCENARIO 9: Baseline Drift Case
MULTI_SCENARIO_BASELINE_DRIFT = MultiEventAnalyzeRequest(
    events=[
        {
            "event_id": f"EVT-DRIFT-{i}",
            "event_type": "movement",
            "timestamp": (BASE_TIME + timedelta(minutes=i * 15)).isoformat(),
            "location": {"latitude": 26.8500, "longitude": 80.9500},
            "entity_ids": [f"ENTITY-UNIT-{i}"],
            "attributes": {"speed": 55.0, "activity_level": 0.72},
        }
        for i in range(3)
    ],
    context=MultiEventContextInput(
        sector_id="SECTOR_ALPHA",
        historical_baseline_activity=0.30,
        recent_baseline_activity=0.72,
    ),
)

# 10. SCENARIO 10: Mixed Cluster (3 strongly linked + 2 isolated outliers)
MULTI_SCENARIO_MIXED_CLUSTER = MultiEventAnalyzeRequest(
    events=[
        # Cluster A (3 related events)
        {
            "event_id": "EVT-MIX-1",
            "event_type": "movement",
            "timestamp": BASE_TIME.isoformat(),
            "location": {"latitude": 26.8500, "longitude": 80.9500},
            "entity_ids": ["ENTITY-CLUSTER-LEAD"],
            "attributes": {"speed": 50.0, "activity_level": 0.60},
        },
        {
            "event_id": "EVT-MIX-2",
            "event_type": "patrol_deviation",
            "timestamp": (BASE_TIME + timedelta(minutes=10)).isoformat(),
            "location": {"latitude": 26.8520, "longitude": 80.9520},
            "entity_ids": ["ENTITY-CLUSTER-LEAD"],
            "attributes": {"speed": 70.0, "activity_level": 0.75},
        },
        {
            "event_id": "EVT-MIX-3",
            "event_type": "sensor_ping",
            "timestamp": (BASE_TIME + timedelta(minutes=15)).isoformat(),
            "location": {"latitude": 26.8510, "longitude": 80.9515},
            "entity_ids": ["ENTITY-CLUSTER-WINGMAN"],
            "attributes": {"speed": 65.0, "activity_level": 0.70},
        },
        # Outlier 1: distant in time and space
        {
            "event_id": "EVT-OUTLIER-1",
            "event_type": "movement",
            "timestamp": (BASE_TIME + timedelta(hours=5)).isoformat(),
            "location": {"latitude": 27.2000, "longitude": 81.3000},
            "entity_ids": ["ENTITY-REMOTE-1"],
            "attributes": {"speed": 25.0, "activity_level": 0.20},
        },
        # Outlier 2: distant in time and space
        {
            "event_id": "EVT-OUTLIER-2",
            "event_type": "communication",
            "timestamp": (BASE_TIME + timedelta(hours=9)).isoformat(),
            "location": {"latitude": 27.8000, "longitude": 81.9000},
            "entity_ids": ["ENTITY-REMOTE-2"],
            "attributes": {"speed": 0.0, "activity_level": 0.15},
        },
    ]
)

MULTI_SCENARIOS_MAP: Dict[str, MultiEventAnalyzeRequest] = {
    "isolated": MULTI_SCENARIO_ISOLATED,
    "temporal_cluster": MULTI_SCENARIO_TEMPORAL_CLUSTER,
    "spatial_cluster": MULTI_SCENARIO_SPATIAL_CLUSTER,
    "same_entity_sequence": MULTI_SCENARIO_SAME_ENTITY_SEQUENCE,
    "duplicates": MULTI_SCENARIO_DUPLICATES,
    "strong_correlation": MULTI_SCENARIO_STRONG_CORRELATION,
    "weak_correlation": MULTI_SCENARIO_WEAK_CORRELATION,
    "false_correlation": MULTI_SCENARIO_FALSE_CORRELATION,
    "baseline_drift": MULTI_SCENARIO_BASELINE_DRIFT,
    "mixed_cluster": MULTI_SCENARIO_MIXED_CLUSTER,
}


def get_multi_scenario(scenario_id: str) -> MultiEventAnalyzeRequest:
    """Retrieve Phase 2 multi-event scenario by key."""
    if scenario_id not in MULTI_SCENARIOS_MAP:
        raise KeyError(f"Multi-event scenario '{scenario_id}' not found. Available: {list(MULTI_SCENARIOS_MAP.keys())}")
    return MULTI_SCENARIOS_MAP[scenario_id]


def get_all_multi_scenarios() -> Dict[str, Dict[str, Any]]:
    """Return catalogue of Phase 2 scenarios for testing."""
    return {
        key: {
            "name": key,
            "event_count": len(req.events),
            "data_classification": "SYNTHETIC",
        }
        for key, req in MULTI_SCENARIOS_MAP.items()
    }


# ==============================================================================
# PHASE 3 ENTITY INTELLIGENCE SYNTHETIC SCENARIOS
# ==============================================================================

# 1. STABLE ENTITY: 10 events over 72h with predictable speed (~38 km/h) and tight spatial radius
SCENARIO_EVENTS_STABLE: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-STABLE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=72 - i * 8),
        location=Coordinates(latitude=26.8460 + (i % 3) * 0.003, longitude=80.9460 + (i % 2) * 0.003, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-STABLE-01"],
        attributes={"speed": 36.0 + (i % 4), "activity_level": 0.30, "heading_deg": 90.0, "callsign": "ECHO-STABLE", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability_score=0.90),
    )
    for i in range(10)
]

# 2. COLD START ENTITY: Single event (< 3 events -> INSUFFICIENT_HISTORY, confidence <= 0.35)
SCENARIO_EVENTS_COLD_START: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id="EVT-COLD-01",
        event_type="movement",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-COLD-02"],
        attributes={"speed": 30.0, "activity_level": 0.25, "callsign": "NOVICE-01", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-OPTICAL-01", reliability_score=0.85),
    )
]

# 3. ACTIVITY SURGE ENTITY: 4 baseline events over 96h, followed by 6 events in the final 12h
SCENARIO_EVENTS_ACTIVITY_SURGE: List[CanonicalEvent] = [
    # 4 baseline events (spaced every 24h)
    CanonicalEvent(
        event_id=f"EVT-SURGE-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=96 - i * 24),
        location=Coordinates(latitude=26.8600 + i * 0.002, longitude=80.9600, sector_id="SECTOR_BETA"),
        entity_ids=["ENTITY-SURGE-03"],
        attributes={"speed": 22.0, "activity_level": 0.25, "callsign": "TEMPO-03", "entity_type": "PATROL_UNIT"},
        source=EventSource(source_id="SENSOR-RADAR-02", reliability_score=0.88),
    )
    for i in range(4)
] + [
    # 6 rapid events within 12h
    CanonicalEvent(
        event_id=f"EVT-SURGE-BURST-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=12 - i * 2),
        location=Coordinates(latitude=26.8650 + i * 0.003, longitude=80.9620, sector_id="SECTOR_BETA"),
        entity_ids=["ENTITY-SURGE-03"],
        attributes={"speed": 45.0, "activity_level": 0.75, "callsign": "TEMPO-03", "entity_type": "PATROL_UNIT"},
        source=EventSource(source_id="SENSOR-RADAR-02", reliability_score=0.88),
    )
    for i in range(6)
]

# 4. ACTIVITY DROP ENTITY: 7 frequent baseline events, then sudden drop to 1 sparse event in 24h
SCENARIO_EVENTS_ACTIVITY_DROP: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-DROP-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=72 - i * 4),
        location=Coordinates(latitude=26.8700, longitude=80.9700, sector_id="SECTOR_GAMMA"),
        entity_ids=["ENTITY-DROP-04"],
        attributes={"speed": 35.0, "activity_level": 0.35, "callsign": "SILENT-04", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability_score=0.85),
    )
    for i in range(7)
] + [
    CanonicalEvent(
        event_id="EVT-DROP-LATE",
        event_type="movement",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=26.8700, longitude=80.9700, sector_id="SECTOR_GAMMA"),
        entity_ids=["ENTITY-DROP-04"],
        attributes={"speed": 35.0, "activity_level": 0.10, "callsign": "SILENT-04", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability_score=0.85),
    )
]

# 5. SPATIAL EXPANSION ENTITY: 5 events tightly centered (< 2 km radius), then 2 events 40+ km away
SCENARIO_EVENTS_SPATIAL_EXPANSION: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-EXPAND-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=48 - i * 8),
        location=Coordinates(latitude=26.8500 + i * 0.002, longitude=80.9500 + (i % 2) * 0.002, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-EXPAND-05"],
        attributes={"speed": 40.0, "activity_level": 0.30, "callsign": "ROAMER-05", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability_score=0.85),
    )
    for i in range(5)
] + [
    CanonicalEvent(
        event_id="EVT-EXPAND-OUT-01",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=3),
        location=Coordinates(latitude=27.2500, longitude=81.3500, sector_id="SECTOR_DELTA"),
        entity_ids=["ENTITY-EXPAND-05"],
        attributes={"speed": 75.0, "activity_level": 0.65, "callsign": "ROAMER-05", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-03", reliability_score=0.88),
    ),
    CanonicalEvent(
        event_id="EVT-EXPAND-OUT-02",
        event_type="movement",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=27.3500, longitude=81.4500, sector_id="SECTOR_DELTA"),
        entity_ids=["ENTITY-EXPAND-05"],
        attributes={"speed": 82.0, "activity_level": 0.70, "callsign": "ROAMER-05", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-03", reliability_score=0.88),
    ),
]

# 6. NEW EVENT TYPE ENTITY: 5 baseline movement events, then 2 novel sensor spoofing events
SCENARIO_EVENTS_NEW_EVENT_TYPE: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-NEWTYPE-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=48 - i * 8),
        location=Coordinates(latitude=26.9000, longitude=80.9800, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-NEWTYPE-06"],
        attributes={"speed": 280.0, "activity_level": 0.40, "callsign": "PHANTOM-06", "entity_type": "AIRCRAFT"},
        source=EventSource(source_id="SENSOR-ELINT-01", reliability_score=0.90),
    )
    for i in range(5)
] + [
    CanonicalEvent(
        event_id="EVT-NEWTYPE-NOVEL-01",
        event_type="electronic_emission",
        timestamp=BASE_TIME - timedelta(hours=2),
        location=Coordinates(latitude=26.9200, longitude=80.9900, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-NEWTYPE-06"],
        attributes={"speed": 290.0, "activity_level": 0.75, "priority_hint": "HIGH", "callsign": "PHANTOM-06", "entity_type": "AIRCRAFT"},
        source=EventSource(source_id="SENSOR-ELINT-01", reliability_score=0.90),
    ),
    CanonicalEvent(
        event_id="EVT-NEWTYPE-NOVEL-02",
        event_type="sensor_spoofing",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=26.9300, longitude=81.0000, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-NEWTYPE-06"],
        attributes={"speed": 310.0, "activity_level": 0.85, "priority_hint": "CRITICAL", "callsign": "PHANTOM-06", "entity_type": "AIRCRAFT"},
        source=EventSource(source_id="SENSOR-ELINT-01", reliability_score=0.90),
    ),
]

# 7. REPEATED ASSOCIATION ENTITY PAIR: 3 events containing both ENTITY-ASSOC-07A and ENTITY-ASSOC-07B
SCENARIO_EVENTS_REPEATED_ASSOCIATION: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-ASSOC-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=24 - i * 8),
        location=Coordinates(latitude=26.8550 + i * 0.005, longitude=80.9550 + i * 0.005, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-ASSOC-07A", "ENTITY-ASSOC-07B"],
        attributes={"speed": 40.0, "activity_level": 0.40, "callsign": f"PAIR-{i}", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability_score=0.88),
    )
    for i in range(3)
]

# 8. MULTI CLUSTER PARTICIPATION: Entity active in two distinct temporal/spatial clusters
SCENARIO_EVENTS_MULTI_CLUSTER: List[CanonicalEvent] = [
    # Cluster 1 participation (3 events at Sector Alpha)
    CanonicalEvent(
        event_id=f"EVT-MULTICLUS-C1-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=48 - i * 2),
        location=Coordinates(latitude=26.8460 + i * 0.001, longitude=80.9460 + i * 0.001, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-MULTICLUSTER-08"],
        attributes={"speed": 35.0, "activity_level": 0.30, "callsign": "NOMAD-08", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability_score=0.88),
    )
    for i in range(3)
] + [
    # Cluster 2 participation (3 events at Sector Omega, 80 km away and 24h later)
    CanonicalEvent(
        event_id=f"EVT-MULTICLUS-C2-{i:02d}",
        event_type="patrol",
        timestamp=BASE_TIME - timedelta(hours=12 - i * 2),
        location=Coordinates(latitude=27.5000 + i * 0.002, longitude=81.6000 + i * 0.002, sector_id="SECTOR_OMEGA"),
        entity_ids=["ENTITY-MULTICLUSTER-08"],
        attributes={"speed": 45.0, "activity_level": 0.50, "callsign": "NOMAD-08", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-04", reliability_score=0.92),
    )
    for i in range(3)
]

# 9. BEHAVIORAL SHIFT (HIGH RISK): Speed surges from 30 km/h to 105 km/h with patrol deviation
SCENARIO_EVENTS_BEHAVIORAL_SHIFT: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-SHIFT-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=60 - i * 10),
        location=Coordinates(latitude=26.8400 + i * 0.002, longitude=80.9400, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-SHIFT-09"],
        attributes={"speed": 30.0, "activity_level": 0.25, "callsign": "VIPER-09", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability_score=0.85),
    )
    for i in range(5)
] + [
    CanonicalEvent(
        event_id="EVT-SHIFT-DEV-01",
        event_type="patrol_deviation",
        timestamp=BASE_TIME - timedelta(hours=1),
        location=Coordinates(latitude=26.8800, longitude=80.9900, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-SHIFT-09"],
        attributes={"speed": 98.0, "activity_level": 0.85, "priority_hint": "HIGH", "callsign": "VIPER-09", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability_score=0.85),
    ),
    CanonicalEvent(
        event_id="EVT-SHIFT-DEV-02",
        event_type="patrol_deviation",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=26.9200, longitude=81.0400, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-SHIFT-09"],
        attributes={"speed": 115.0, "activity_level": 0.95, "priority_hint": "CRITICAL", "callsign": "VIPER-09", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability_score=0.85),
    ),
]

# 10. CONTRADICTORY TELEMETRY: 4 baseline events, then two sensors disagree on location and speed within 30s
SCENARIO_EVENTS_CONTRADICTORY_TELEMETRY: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-CONFLICT-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=48 - i * 10),
        location=Coordinates(latitude=26.8500 + i * 0.002, longitude=80.9500, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-CONFLICT-10"],
        attributes={"speed": 40.0, "activity_level": 0.30, "callsign": "DISCORD-10", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability_score=0.85),
    )
    for i in range(4)
] + [
    CanonicalEvent(
        event_id="EVT-CONFLICT-S1",
        event_type="movement",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=26.8600, longitude=80.9600, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-CONFLICT-10"],
        attributes={"speed": 35.0, "activity_level": 0.30, "callsign": "DISCORD-10", "entity_type": "VEHICLE"},
        source=EventSource(source_id="SENSOR-RADAR-NORTH", reliability_score=0.85),
    ),
    CanonicalEvent(
        event_id="EVT-CONFLICT-S2",
        event_type="movement",
        timestamp=BASE_TIME + timedelta(seconds=25),
        location=Coordinates(latitude=27.1500, longitude=81.2500, sector_id="SECTOR_DELTA"),  # ~40 km away in 25 seconds
        entity_ids=["ENTITY-CONFLICT-10"],
        attributes={"speed": 140.0, "activity_level": 0.85, "callsign": "DISCORD-10", "entity_type": "VEHICLE", "contradictory_sensor": True},
        source=EventSource(source_id="SENSOR-OPTICAL-SOUTH", reliability_score=0.75),
    ),
]

# Map of Scenario IDs to target primary Entity IDs and event lists
ENTITY_SCENARIOS_MAP: Dict[str, Dict[str, Any]] = {
    "stable": {
        "entity_id": "ENTITY-STABLE-01",
        "description": "Stable baseline entity with 10 consistent observations over 72h",
        "events": SCENARIO_EVENTS_STABLE,
    },
    "cold_start": {
        "entity_id": "ENTITY-COLD-02",
        "description": "Cold start entity with only 1 observation (insufficient history)",
        "events": SCENARIO_EVENTS_COLD_START,
    },
    "activity_surge": {
        "entity_id": "ENTITY-SURGE-03",
        "description": "Entity exhibiting sudden activity and frequency burst",
        "events": SCENARIO_EVENTS_ACTIVITY_SURGE,
    },
    "activity_drop": {
        "entity_id": "ENTITY-DROP-04",
        "description": "Entity exhibiting significant activity drop / operational silence",
        "events": SCENARIO_EVENTS_ACTIVITY_DROP,
    },
    "spatial_expansion": {
        "entity_id": "ENTITY-EXPAND-05",
        "description": "Entity operating > 1.5x beyond historical bounding radius",
        "events": SCENARIO_EVENTS_SPATIAL_EXPANSION,
    },
    "new_event_type": {
        "entity_id": "ENTITY-NEWTYPE-06",
        "description": "Entity displaying novel electronic warfare / spoofing event types",
        "events": SCENARIO_EVENTS_NEW_EVENT_TYPE,
    },
    "repeated_association": {
        "entity_id": "ENTITY-ASSOC-07A",
        "partner_id": "ENTITY-ASSOC-07B",
        "description": "Entity pair exhibiting repeated co-occurrence across multiple events",
        "events": SCENARIO_EVENTS_REPEATED_ASSOCIATION,
    },
    "multi_cluster": {
        "entity_id": "ENTITY-MULTICLUSTER-08",
        "description": "Entity participating across distinct tactical clusters",
        "events": SCENARIO_EVENTS_MULTI_CLUSTER,
    },
    "behavioral_shift": {
        "entity_id": "ENTITY-SHIFT-09",
        "description": "Entity undergoing high-risk behavioral shift in speed and route deviation",
        "events": SCENARIO_EVENTS_BEHAVIORAL_SHIFT,
    },
    "contradictory_telemetry": {
        "entity_id": "ENTITY-CONFLICT-10",
        "description": "Entity with conflicting sensor feeds resulting in confidence penalties",
        "events": SCENARIO_EVENTS_CONTRADICTORY_TELEMETRY,
    },
}


# ==============================================================================
# PHASE 4 MULTI-DIMENSIONAL ANOMALY & RISK SCENARIOS (14 SCENARIOS)
# ==============================================================================

# 1. NORMAL: Within speed, within area, standard hours, matched baseline
SCENARIO_P4_NORMAL: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-P4-NORM-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=48 - i * 5),
        location=Coordinates(latitude=26.8467 + i * 0.001, longitude=80.9462 + i * 0.001, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-NORM-01"],
        attributes={"speed": 40.0 + (i % 3), "activity_level": 0.30, "entity_type": "VEHICLE", "callsign": "NORM-01"},
        source=EventSource(source_id="SENSOR-RADAR-ALPHA", reliability=0.90),
    )
    for i in range(10)
]

# 2. KINEMATIC SPIKE: Ground vehicle operating at 145 km/h (baseline 40 km/h)
SCENARIO_P4_KINEMATIC_SPIKE: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-P4-KINE-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=48 - i * 5),
        location=Coordinates(latitude=26.8500 + i * 0.001, longitude=80.9500 + i * 0.001, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-KINE-02"],
        attributes={"speed": 40.0, "activity_level": 0.30, "entity_type": "VEHICLE", "callsign": "KINE-02"},
        source=EventSource(source_id="SENSOR-RADAR-ALPHA", reliability=0.90),
    )
    for i in range(8)
] + [
    CanonicalEvent(
        event_id="EVT-P4-KINE-SPIKE-01",
        event_type="movement",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=26.8600, longitude=80.9600, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-KINE-02"],
        attributes={"speed": 145.0, "activity_level": 0.85, "entity_type": "VEHICLE", "callsign": "KINE-02"},
        source=EventSource(source_id="SENSOR-RADAR-ALPHA", reliability=0.92),
    ),
    CanonicalEvent(
        event_id="EVT-P4-KINE-SPIKE-02",
        event_type="movement",
        timestamp=BASE_TIME + timedelta(minutes=5),
        location=Coordinates(latitude=26.8720, longitude=80.9720, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-KINE-02"],
        attributes={"speed": 150.0, "activity_level": 0.90, "entity_type": "VEHICLE", "callsign": "KINE-02"},
        source=EventSource(source_id="SENSOR-OPTICAL-ALPHA", reliability=0.88),
    ),
]

# 3. SPATIAL EXPANSION: Operating > 70 km away from baseline centroid
SCENARIO_P4_SPATIAL_EXPANSION: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-P4-SPAT-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=48 - i * 5),
        location=Coordinates(latitude=26.8500 + (i * 0.001), longitude=80.9500 + (i * 0.001), sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-SPAT-03"],
        attributes={"speed": 40.0, "activity_level": 0.35, "entity_type": "VEHICLE", "callsign": "SPAT-03"},
        source=EventSource(source_id="SENSOR-RADAR-ALPHA", reliability=0.90),
    )
    for i in range(8)
] + [
    CanonicalEvent(
        event_id="EVT-P4-SPAT-BREACH-01",
        event_type="movement",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=27.6500, longitude=81.8500, sector_id="SECTOR_FOXTROT"),
        entity_ids=["ENTITY-P4-SPAT-03"],
        attributes={"speed": 45.0, "activity_level": 0.60, "sector": "SECTOR_FOXTROT", "entity_type": "VEHICLE", "callsign": "SPAT-03"},
        source=EventSource(source_id="SENSOR-SATELLITE-01", reliability=0.92),
    ),
    CanonicalEvent(
        event_id="EVT-P4-SPAT-BREACH-02",
        event_type="movement",
        timestamp=BASE_TIME + timedelta(minutes=10),
        location=Coordinates(latitude=27.7000, longitude=81.9000, sector_id="SECTOR_FOXTROT"),
        entity_ids=["ENTITY-P4-SPAT-03"],
        attributes={"speed": 45.0, "activity_level": 0.60, "sector": "SECTOR_FOXTROT", "entity_type": "VEHICLE", "callsign": "SPAT-03"},
        source=EventSource(source_id="SENSOR-SATELLITE-01", reliability=0.92),
    ),
]

# 4. TEMPORAL SHIFT: Operating at 02:30 AM (historical active hours 09:00 - 17:00)
SCENARIO_P4_TEMPORAL_SHIFT: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-P4-TEMP-BASE-{i:02d}",
        event_type="movement",
        timestamp=datetime(2026, 9, 8 + (i // 3), 10 + (i % 5), 0, 0, tzinfo=timezone.utc),
        location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-TEMP-04"],
        attributes={"speed": 35.0, "activity_level": 0.30, "entity_type": "VEHICLE", "callsign": "TEMP-04"},
        source=EventSource(source_id="SENSOR-RADAR-ALPHA", reliability=0.88),
    )
    for i in range(8)
] + [
    CanonicalEvent(
        event_id="EVT-P4-TEMP-NIGHT-01",
        event_type="movement",
        timestamp=datetime(2026, 9, 11, 2, 15, 0, tzinfo=timezone.utc),
        location=Coordinates(latitude=26.8550, longitude=80.9550, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-TEMP-04"],
        attributes={"speed": 35.0, "activity_level": 0.40, "entity_type": "VEHICLE", "callsign": "TEMP-04"},
        source=EventSource(source_id="SENSOR-IR-01", reliability=0.85),
    ),
    CanonicalEvent(
        event_id="EVT-P4-TEMP-NIGHT-02",
        event_type="movement",
        timestamp=datetime(2026, 9, 11, 2, 45, 0, tzinfo=timezone.utc),
        location=Coordinates(latitude=26.8570, longitude=80.9570, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-TEMP-04"],
        attributes={"speed": 38.0, "activity_level": 0.45, "entity_type": "VEHICLE", "callsign": "TEMP-04"},
        source=EventSource(source_id="SENSOR-IR-01", reliability=0.85),
    ),
]

# 5. FREQUENCY SURGE: Burst of 7 events in 10 minutes (baseline 2 events/day)
SCENARIO_P4_FREQUENCY_SURGE: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-P4-FREQ-BASE-{i:02d}",
        event_type="patrol",
        timestamp=BASE_TIME - timedelta(days=4 - i),
        location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-FREQ-05"],
        attributes={"speed": 30.0, "activity_level": 0.25, "entity_type": "PATROL_UNIT", "callsign": "FREQ-05"},
        source=EventSource(source_id="SENSOR-RADIO-01", reliability=0.85),
    )
    for i in range(5)
] + [
    CanonicalEvent(
        event_id=f"EVT-P4-FREQ-BURST-{i:02d}",
        event_type="patrol",
        timestamp=BASE_TIME + timedelta(minutes=i * 2),
        location=Coordinates(latitude=26.8500 + i * 0.001, longitude=80.9500 + i * 0.001, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-FREQ-05"],
        attributes={"speed": 45.0, "activity_level": 0.70, "entity_type": "PATROL_UNIT", "callsign": "FREQ-05"},
        source=EventSource(source_id="SENSOR-RADIO-01", reliability=0.88),
    )
    for i in range(7)
]

# 6. NOVEL EVENT TYPE: Entity displays RADAR_JAMMING and ELECTRONIC_ATTACK
SCENARIO_P4_NOVEL_EVENT_TYPE: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-P4-EVTY-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=36 - i * 5),
        location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-EVTY-06"],
        attributes={"speed": 35.0, "activity_level": 0.30, "entity_type": "VEHICLE", "callsign": "EVTY-06"},
        source=EventSource(source_id="SENSOR-RADAR-ALPHA", reliability=0.90),
    )
    for i in range(8)
] + [
    CanonicalEvent(
        event_id="EVT-P4-EVTY-NOVEL-01",
        event_type="RADAR_JAMMING",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=26.8550, longitude=80.9550, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-EVTY-06"],
        attributes={"speed": 35.0, "activity_level": 0.90, "jamming_power_db": 45.0, "entity_type": "VEHICLE", "callsign": "EVTY-06"},
        source=EventSource(source_id="SENSOR-SIGINT-01", reliability=0.95),
    ),
    CanonicalEvent(
        event_id="EVT-P4-EVTY-NOVEL-02",
        event_type="ELECTRONIC_ATTACK",
        timestamp=BASE_TIME + timedelta(minutes=5),
        location=Coordinates(latitude=26.8560, longitude=80.9560, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-EVTY-06"],
        attributes={"speed": 35.0, "activity_level": 0.95, "frequency_ghz": 9.4, "entity_type": "VEHICLE", "callsign": "EVTY-06"},
        source=EventSource(source_id="SENSOR-SIGINT-01", reliability=0.95),
    ),
]

# 7. MULTI-DIMENSIONAL: Kinematic spike (140 km/h) + spatial breach (60 km) + novel event (AIR_STRIKE)
SCENARIO_P4_MULTI_DIMENSIONAL: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-P4-MDIM-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=36 - i * 5),
        location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-MDIM-07"],
        attributes={"speed": 40.0, "activity_level": 0.30, "entity_type": "VEHICLE", "callsign": "MDIM-07"},
        source=EventSource(source_id="SENSOR-RADAR-ALPHA", reliability=0.90),
    )
    for i in range(8)
] + [
    CanonicalEvent(
        event_id="EVT-P4-MDIM-01",
        event_type="AIR_STRIKE",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=27.4500, longitude=81.6500, sector_id="SECTOR_ZULU"),
        entity_ids=["ENTITY-P4-MDIM-07"],
        attributes={"speed": 140.0, "activity_level": 0.95, "sector": "SECTOR_ZULU", "entity_type": "VEHICLE", "callsign": "MDIM-07"},
        source=EventSource(source_id="SENSOR-SATELLITE-01", reliability=0.95),
    ),
    CanonicalEvent(
        event_id="EVT-P4-MDIM-02",
        event_type="AIR_STRIKE",
        timestamp=BASE_TIME + timedelta(minutes=5),
        location=Coordinates(latitude=27.4800, longitude=81.6800, sector_id="SECTOR_ZULU"),
        entity_ids=["ENTITY-P4-MDIM-07"],
        attributes={"speed": 145.0, "activity_level": 0.95, "sector": "SECTOR_ZULU", "entity_type": "VEHICLE", "callsign": "MDIM-07"},
        source=EventSource(source_id="SENSOR-RADAR-ZULU", reliability=0.92),
    ),
]

# 8. PERSISTENT: Elevated anomaly maintained across 4 consecutive evaluation windows
SCENARIO_P4_PERSISTENT: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-P4-PERS-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=60 - i * 6),
        location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-PERS-08"],
        attributes={"speed": 35.0, "activity_level": 0.30, "entity_type": "VEHICLE", "callsign": "PERS-08"},
        source=EventSource(source_id="SENSOR-RADAR-ALPHA", reliability=0.90),
    )
    for i in range(6)
] + [
    CanonicalEvent(
        event_id=f"EVT-P4-PERS-ANOM-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=12 - i * 3),
        location=Coordinates(latitude=27.2000 + i * 0.01, longitude=81.2000 + i * 0.01, sector_id="SECTOR_BETA"),
        entity_ids=["ENTITY-P4-PERS-08"],
        attributes={"speed": 125.0 + i * 5, "activity_level": 0.85, "entity_type": "VEHICLE", "callsign": "PERS-08"},
        source=EventSource(source_id="SENSOR-RADAR-BETA", reliability=0.90),
    )
    for i in range(4)
]

# 9. ESCALATING: Anomaly scores rising sharply across windows
SCENARIO_P4_ESCALATING: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-P4-ESCL-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=48 - i * 6),
        location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-ESCL-09"],
        attributes={"speed": 35.0, "activity_level": 0.30, "entity_type": "VEHICLE", "callsign": "ESCL-09"},
        source=EventSource(source_id="SENSOR-RADAR-ALPHA", reliability=0.90),
    )
    for i in range(6)
] + [
    CanonicalEvent(
        event_id="EVT-P4-ESCL-WIN-01",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=4),
        location=Coordinates(latitude=26.8600, longitude=80.9600, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-ESCL-09"],
        attributes={"speed": 65.0, "activity_level": 0.50, "entity_type": "VEHICLE", "callsign": "ESCL-09"},
        source=EventSource(source_id="SENSOR-RADAR-ALPHA", reliability=0.90),
    ),
    CanonicalEvent(
        event_id="EVT-P4-ESCL-WIN-02",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=2),
        location=Coordinates(latitude=26.9200, longitude=81.0200, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-ESCL-09"],
        attributes={"speed": 110.0, "activity_level": 0.75, "entity_type": "VEHICLE", "callsign": "ESCL-09"},
        source=EventSource(source_id="SENSOR-RADAR-ALPHA", reliability=0.90),
    ),
    CanonicalEvent(
        event_id="EVT-P4-ESCL-WIN-03",
        event_type="movement",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=27.2500, longitude=81.3500, sector_id="SECTOR_GAMMA"),
        entity_ids=["ENTITY-P4-ESCL-09"],
        attributes={"speed": 155.0, "activity_level": 0.95, "entity_type": "VEHICLE", "callsign": "ESCL-09"},
        source=EventSource(source_id="SENSOR-SATELLITE-01", reliability=0.92),
    ),
]

# 10. FALSE POSITIVE: Single corrupted speed reading (220 km/h) from unverified sensor
SCENARIO_P4_FALSE_POSITIVE: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-P4-FLSP-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=36 - i * 5),
        location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-FLSP-10"],
        attributes={"speed": 35.0, "activity_level": 0.30, "entity_type": "VEHICLE", "callsign": "FLSP-10"},
        source=EventSource(source_id="SENSOR-TRUSTED-01", reliability=0.90),
    )
    for i in range(8)
] + [
    CanonicalEvent(
        event_id="EVT-P4-FLSP-GLITCH",
        event_type="movement",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=26.8510, longitude=80.9510, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-FLSP-10"],
        attributes={"speed": 220.0, "activity_level": 0.30, "entity_type": "VEHICLE", "callsign": "FLSP-10"},
        source=EventSource(source_id="SENSOR-UNVERIFIED-DEV", reliability=0.30),
    ),
]

# 11. SENSOR CONFLICT: Contradicting speed readings within 20 seconds
SCENARIO_P4_SENSOR_CONFLICT: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-P4-SNCF-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=30 - i * 5),
        location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-SNCF-11"],
        attributes={"speed": 40.0, "activity_level": 0.35, "entity_type": "VEHICLE", "callsign": "SNCF-11"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability=0.88),
    )
    for i in range(6)
] + [
    CanonicalEvent(
        event_id="EVT-P4-SNCF-RDR",
        event_type="movement",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=26.8550, longitude=80.9550, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-SNCF-11"],
        attributes={"speed": 140.0, "activity_level": 0.85, "entity_type": "VEHICLE", "callsign": "SNCF-11"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability=0.85),
    ),
    CanonicalEvent(
        event_id="EVT-P4-SNCF-OPT",
        event_type="movement",
        timestamp=BASE_TIME + timedelta(seconds=20),
        location=Coordinates(latitude=26.8552, longitude=80.9551, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-SNCF-11"],
        attributes={"speed": 5.0, "activity_level": 0.20, "entity_type": "VEHICLE", "callsign": "SNCF-11"},
        source=EventSource(source_id="SENSOR-OPTICAL-01", reliability=0.85),
    ),
]

# 12. CONTEXTUAL ANOMALY: Normal individual metrics, but active in a calm/restricted sector
SCENARIO_P4_CONTEXTUAL: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-P4-CTXT-BASE-{i:02d}",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(hours=36 - i * 5),
        location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_RESTRICTED"),
        entity_ids=["ENTITY-P4-CTXT-12"],
        attributes={"speed": 45.0, "activity_level": 0.40, "sector": "SECTOR_RESTRICTED", "entity_type": "VEHICLE", "callsign": "CTXT-12"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability=0.90),
    )
    for i in range(6)
] + [
    CanonicalEvent(
        event_id="EVT-P4-CTXT-01",
        event_type="movement",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=26.8600, longitude=80.9600, sector_id="SECTOR_RESTRICTED"),
        entity_ids=["ENTITY-P4-CTXT-12"],
        attributes={"speed": 50.0, "activity_level": 0.88, "sector": "SECTOR_RESTRICTED", "entity_type": "VEHICLE", "callsign": "CTXT-12"},
        source=EventSource(source_id="SENSOR-RADAR-01", reliability=0.90),
    ),
]

# 13. RELATIONSHIP CHANGE: Sudden association with 4 new unknown peers and high-risk threat
SCENARIO_P4_RELATIONSHIP_CHANGE: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id=f"EVT-P4-RELA-BASE-{i:02d}",
        event_type="patrol",
        timestamp=BASE_TIME - timedelta(hours=36 - i * 5),
        location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-RELA-13"],
        attributes={"speed": 35.0, "activity_level": 0.30, "entity_type": "PATROL_UNIT", "callsign": "RELA-13"},
        source=EventSource(source_id="SENSOR-RADAR-ALPHA", reliability=0.90),
    )
    for i in range(6)
] + [
    CanonicalEvent(
        event_id="EVT-P4-RELA-RENDEZVOUS",
        event_type="patrol",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=26.8550, longitude=80.9550, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-RELA-13"],
        attributes={
            "speed": 35.0,
            "activity_level": 0.70,
            "entity_type": "PATROL_UNIT",
            "callsign": "RELA-13",
            "target_entity_id": "ENTITY-THREAT-ALPHA",
            "co_observed_entities": ["ENTITY-UNTRACKED-A", "ENTITY-UNTRACKED-B", "ENTITY-UNTRACKED-C", "ENTITY-UNTRACKED-D"],
        },
        source=EventSource(source_id="SENSOR-SIGINT-01", reliability=0.92),
    ),
]

# 14. NEW SENSOR ONBOARDING: Brand new entity with only 2 total observations (cold start)
SCENARIO_P4_NEW_SENSOR_ONBOARDING: List[CanonicalEvent] = [
    CanonicalEvent(
        event_id="EVT-P4-NEWS-01",
        event_type="movement",
        timestamp=BASE_TIME - timedelta(minutes=15),
        location=Coordinates(latitude=26.8500, longitude=80.9500, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-NEWS-14"],
        attributes={"speed": 40.0, "activity_level": 0.50, "entity_type": "VEHICLE", "callsign": "NEWS-14"},
        source=EventSource(source_id="SENSOR-NEW-01", reliability=0.85),
    ),
    CanonicalEvent(
        event_id="EVT-P4-NEWS-02",
        event_type="movement",
        timestamp=BASE_TIME,
        location=Coordinates(latitude=26.8550, longitude=80.9550, sector_id="SECTOR_ALPHA"),
        entity_ids=["ENTITY-P4-NEWS-14"],
        attributes={"speed": 45.0, "activity_level": 0.55, "entity_type": "VEHICLE", "callsign": "NEWS-14"},
        source=EventSource(source_id="SENSOR-NEW-01", reliability=0.85),
    ),
]

# Catalogue mapping for Phase 4 anomaly scenarios
PHASE4_SCENARIOS_MAP: Dict[str, Dict[str, Any]] = {
    "scenario_1_normal": {
        "entity_id": "ENTITY-P4-NORM-01",
        "description": "Nominal operational profile within expected envelope",
        "primary_dimension": "nominal",
        "events": SCENARIO_P4_NORMAL,
        "context": {},
    },
    "scenario_2_kinematic_spike": {
        "entity_id": "ENTITY-P4-KINE-02",
        "description": "Ground vehicle exceeding standard envelope at 145 km/h",
        "primary_dimension": "kinematic",
        "events": SCENARIO_P4_KINEMATIC_SPIKE,
        "context": {},
    },
    "scenario_3_spatial_expansion": {
        "entity_id": "ENTITY-P4-SPAT-03",
        "description": "Entity operating > 70 km away from historical operational area",
        "primary_dimension": "spatial",
        "events": SCENARIO_P4_SPATIAL_EXPANSION,
        "context": {},
    },
    "scenario_4_temporal_shift": {
        "entity_id": "ENTITY-P4-TEMP-04",
        "description": "Entity operating during off-schedule night hours (02:30 AM)",
        "primary_dimension": "temporal",
        "events": SCENARIO_P4_TEMPORAL_SHIFT,
        "context": {},
    },
    "scenario_5_frequency_surge": {
        "entity_id": "ENTITY-P4-FREQ-05",
        "description": "Burst of 7 events in 10 minutes vs baseline 2 events/day",
        "primary_dimension": "frequency",
        "events": SCENARIO_P4_FREQUENCY_SURGE,
        "context": {},
    },
    "scenario_6_novel_event_type": {
        "entity_id": "ENTITY-P4-EVTY-06",
        "description": "Entity generating unobserved electronic warfare & jamming event types",
        "primary_dimension": "event_type",
        "events": SCENARIO_P4_NOVEL_EVENT_TYPE,
        "context": {},
    },
    "scenario_7_multi_dimensional": {
        "entity_id": "ENTITY-P4-MDIM-07",
        "description": "Simultaneous kinematic spike, spatial breach, and novel event type",
        "primary_dimension": "multi_dimensional",
        "events": SCENARIO_P4_MULTI_DIMENSIONAL,
        "context": {},
    },
    "scenario_8_persistent": {
        "entity_id": "ENTITY-P4-PERS-08",
        "description": "Elevated anomaly maintained across 4 consecutive evaluation windows",
        "primary_dimension": "persistence",
        "events": SCENARIO_P4_PERSISTENT,
        "context": {},
    },
    "scenario_9_escalating": {
        "entity_id": "ENTITY-P4-ESCL-09",
        "description": "Anomaly score accelerating rapidly across consecutive observations",
        "primary_dimension": "escalating",
        "events": SCENARIO_P4_ESCALATING,
        "context": {},
    },
    "scenario_10_false_positive": {
        "entity_id": "ENTITY-P4-FLSP-10",
        "description": "Isolated single unverified sensor reading with corrupted speed value",
        "primary_dimension": "false_positive_control",
        "events": SCENARIO_P4_FALSE_POSITIVE,
        "context": {},
    },
    "scenario_11_sensor_conflict": {
        "entity_id": "ENTITY-P4-SNCF-11",
        "description": "Contradictory speeds reported by Radar and Optical sensors within 20s",
        "primary_dimension": "sensor_conflict",
        "events": SCENARIO_P4_SENSOR_CONFLICT,
        "context": {},
    },
    "scenario_12_contextual_anomaly": {
        "entity_id": "ENTITY-P4-CTXT-12",
        "description": "Normal metrics but operating inside an active restricted exclusion zone",
        "primary_dimension": "contextual",
        "events": SCENARIO_P4_CONTEXTUAL,
        "context": {
            "sector_average_activity": 0.05,
            "restricted_zone_active": True,
            "sector_threat_level": "CRITICAL",
        },
    },
    "scenario_13_relationship_change": {
        "entity_id": "ENTITY-P4-RELA-13",
        "description": "Rendezvous with 4 untracked peers and high-risk threat entity",
        "primary_dimension": "relational",
        "events": SCENARIO_P4_RELATIONSHIP_CHANGE,
        "context": {"high_risk_entities": ["ENTITY-THREAT-ALPHA"]},
    },
    "scenario_14_new_sensor_onboarding": {
        "entity_id": "ENTITY-P4-NEWS-14",
        "description": "New platform with only 2 observations subjected to cold-start confidence cap",
        "primary_dimension": "cold_start",
        "events": SCENARIO_P4_NEW_SENSOR_ONBOARDING,
        "context": {},
    },
}


def seed_entity_repository(repo: Any) -> None:
    """Populate an EntityRepository with all Phase 3 and Phase 4 synthetic scenario events."""
    # Seed Phase 3 events
    for item in ENTITY_SCENARIOS_MAP.values():
        for event in item["events"]:
            repo.add_event(event)
    # Seed Phase 4 events
    for item in PHASE4_SCENARIOS_MAP.values():
        for event in item["events"]:
            repo.add_event(event)
    # Seed canonical short IDs for Ask NETRA queries (ENTITY-01, ENTITY-02, ENTITY-03)
    if "ENTITY-01" not in repo._entity_events:
        for ev in SCENARIO_EVENTS_STABLE:
            copied = ev.model_copy(update={"event_id": ev.event_id.replace("STABLE", "01"), "entity_ids": ["ENTITY-01"]})
            repo.add_event(copied)
    if "ENTITY-02" not in repo._entity_events:
        for ev in SCENARIO_EVENTS_COLD_START:
            copied = ev.model_copy(update={"event_id": ev.event_id.replace("COLD", "02"), "entity_ids": ["ENTITY-02"]})
            repo.add_event(copied)
    if "ENTITY-03" not in repo._entity_events:
        for ev in SCENARIO_EVENTS_ACTIVITY_SURGE:
            copied = ev.model_copy(update={"event_id": ev.event_id.replace("SURGE", "03"), "entity_ids": ["ENTITY-03"]})
            repo.add_event(copied)


def get_all_entity_scenarios() -> Dict[str, Dict[str, Any]]:
    """Return catalogue of Phase 3 entity scenarios."""
    return {
        key: {
            "scenario_id": key,
            "entity_id": val["entity_id"],
            "description": val["description"],
            "event_count": len(val["events"]),
            "data_classification": "SYNTHETIC",
        }
        for key, val in ENTITY_SCENARIOS_MAP.items()
    }


def get_all_anomaly_scenarios() -> Dict[str, Dict[str, Any]]:
    """Return catalogue of Phase 4 anomaly operational scenarios."""
    return {
        key: {
            "scenario_id": key,
            "entity_id": val["entity_id"],
            "description": val["description"],
            "primary_dimension": val["primary_dimension"],
            "event_count": len(val["events"]),
            "has_context": bool(val.get("context")),
            "data_classification": "SYNTHETIC",
        }
        for key, val in PHASE4_SCENARIOS_MAP.items()
    }


def get_anomaly_scenario(scenario_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve specific Phase 4 anomaly scenario by identifier."""
    return PHASE4_SCENARIOS_MAP.get(scenario_id)


# --- Phase 5 Multi-Source Fusion Scenarios ---
from simulation.fusion_scenarios import (
    get_all_fusion_scenarios,
    get_fusion_scenario,
)

# --- Phase 6 Predictive Intelligence Scenarios ---
from simulation.prediction_scenarios import (
    get_all_prediction_scenarios,
    get_prediction_scenario,
)

# --- Phase 7 Ask NETRA Scenarios ---
from simulation.ask_scenarios import (
    get_ask_scenarios,
    get_ask_scenario_by_id,
)




