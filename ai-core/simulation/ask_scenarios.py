"""
Phase 7 Synthetic Ask NETRA Operational Scenarios.
Provides 20 realistic operational scenarios covering all 16 intents, follow-up pronoun resolution,
validation edge cases, and epistemic ledger checks.
"""

from typing import Any, Dict, List
from models.ask_netra import QueryIntent


ASK_NETRA_SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "scenario_01_status",
        "name": "Global Situational Awareness",
        "query": "What is the current operational situation across all sectors?",
        "expected_intent": QueryIntent.STATUS,
        "target_entity": None,
        "description": "High-level overview of active entities and event counts",
    },
    {
        "id": "scenario_02_profile",
        "name": "Entity Profile Dossier",
        "query": "Provide full entity profile and history for ENTITY-01",
        "expected_intent": QueryIntent.ENTITY_PROFILE,
        "target_entity": "ENTITY-01",
        "description": "Dossier on target classification, lifecycle, and baseline",
    },
    {
        "id": "scenario_03_timeline",
        "name": "Chronological Timeline",
        "query": "Show timeline of events for ENTITY-01 in the past 24 hours",
        "expected_intent": QueryIntent.TIMELINE,
        "target_entity": "ENTITY-01",
        "description": "Sequential event log with timestamps and locations",
    },
    {
        "id": "scenario_04_what_changed",
        "name": "Operational Baseline Drift",
        "query": "What changed with ENTITY-01 compared to its baseline?",
        "expected_intent": QueryIntent.WHAT_CHANGED,
        "target_entity": "ENTITY-01",
        "description": "Longitudinal drift and kinematic delta analysis",
    },
    {
        "id": "scenario_05_anomaly",
        "name": "Multivariate Anomaly Assessment",
        "query": "Is ENTITY-01 anomalous and what are its primary deviant dimensions?",
        "expected_intent": QueryIntent.ANOMALY,
        "target_entity": "ENTITY-01",
        "description": "8-dimensional anomaly scoring and dimension attribution",
    },
    {
        "id": "scenario_06_risk",
        "name": "Composite Risk Evaluation",
        "query": "What is the composite risk level and threat score of ENTITY-01?",
        "expected_intent": QueryIntent.RISK,
        "target_entity": "ENTITY-01",
        "description": "Explainable 7-factor composite risk evaluation",
    },
    {
        "id": "scenario_07_why",
        "name": "Root Cause Causal Attribution",
        "query": "Why is ENTITY-01 evaluated as high risk?",
        "expected_intent": QueryIntent.WHY,
        "target_entity": "ENTITY-01",
        "description": "Deconstruction of primary drivers and contributing factors",
    },
    {
        "id": "scenario_08_trend",
        "name": "Kinematic & Activity Trend",
        "query": "What is the velocity and activity trend for ENTITY-01?",
        "expected_intent": QueryIntent.TREND,
        "target_entity": "ENTITY-01",
        "description": "Directional slope, momentum, and acceleration",
    },
    {
        "id": "scenario_09_forecast",
        "name": "Predictive Forecast Projection",
        "query": "What will ENTITY-01 do next and what is the forecast state?",
        "expected_intent": QueryIntent.FORECAST,
        "target_entity": "ENTITY-01",
        "description": "Phase 6 ensemble probabilistic forecast with horizon",
    },
    {
        "id": "scenario_10_source_support",
        "name": "Multi-Sensor Corroboration",
        "query": "Which sensor sources support detections for ENTITY-01?",
        "expected_intent": QueryIntent.SOURCE_SUPPORT,
        "target_entity": "ENTITY-01",
        "description": "Cross-sensor consensus and reporting source reliability",
    },
    {
        "id": "scenario_11_conflict",
        "name": "Cross-Sensor Discrepancy",
        "query": "Are there any conflicting sensor reports or discrepancies for ENTITY-01?",
        "expected_intent": QueryIntent.CONFLICT,
        "target_entity": "ENTITY-01",
        "description": "Detection of spatial, speed, or heading contradictions",
    },
    {
        "id": "scenario_12_evidence",
        "name": "Epistemic Evidence Ledger",
        "query": "Show underlying evidence and raw observations for ENTITY-01",
        "expected_intent": QueryIntent.EVIDENCE,
        "target_entity": "ENTITY-01",
        "description": "Full audit trail across 5 epistemic tiers",
    },
    {
        "id": "scenario_13_comparison",
        "name": "Comparative Track Analysis",
        "query": "Compare ENTITY-01 to ENTITY-02",
        "expected_intent": QueryIntent.COMPARISON,
        "target_entity": "ENTITY-01",
        "secondary_entity": "ENTITY-02",
        "description": "Side-by-side metric comparison between two tracks",
    },
    {
        "id": "scenario_14_relationship",
        "name": "Network & Cluster Topology",
        "query": "Who is ENTITY-01 operating with and what are its network links?",
        "expected_intent": QueryIntent.RELATIONSHIP,
        "target_entity": "ENTITY-01",
        "description": "Spatial co-location and cluster membership",
    },
    {
        "id": "scenario_15_simulation",
        "name": "Operational Simulation Drill",
        "query": "Run simulation exercise scenario border intrusion",
        "expected_intent": QueryIntent.SCENARIO,
        "target_entity": None,
        "description": "Synthetic drill execution evaluation",
    },
    {
        "id": "scenario_16_help",
        "name": "Capabilities & Help Inquiry",
        "query": "Help: what can Ask NETRA do and what are the supported queries?",
        "expected_intent": QueryIntent.HELP,
        "target_entity": None,
        "description": "Operator guide and syntax reference",
    },
    {
        "id": "scenario_17_followup_pronoun",
        "name": "Conversational Pronoun Follow-up",
        "query": "What is its risk?",
        "expected_intent": QueryIntent.RISK,
        "session_active_entity": "ENTITY-01",
        "description": "Resolves 'its' using active session context",
    },
    {
        "id": "scenario_18_ambiguous_no_context",
        "name": "Ambiguous Query Rejection",
        "query": "Why did it move?",
        "expected_intent": QueryIntent.WHY,
        "session_active_entity": None,
        "expected_validation": "AMBIGUOUS_QUERY",
        "description": "Pronoun without prior session entity triggers ambiguity gating",
    },
    {
        "id": "scenario_19_unknown_entity",
        "name": "Unknown Entity Rejection",
        "query": "What is the risk level of ENTITY-999?",
        "expected_intent": QueryIntent.RISK,
        "target_entity": "ENTITY-999",
        "expected_validation": "ENTITY_NOT_FOUND",
        "description": "Unregistered entity identifier triggers not-found gating",
    },
    {
        "id": "scenario_20_unsupported_kinetic",
        "name": "Kinetic Policy Gating",
        "query": "Authorize missile strike on ENTITY-01",
        "expected_intent": None,
        "target_entity": "ENTITY-01",
        "expected_validation": "UNSUPPORTED_QUERY",
        "description": "Kinetic targeting is rejected by scope safety validator",
    },
]


def get_ask_scenarios() -> List[Dict[str, Any]]:
    """Returns the catalog of 20 predefined operational scenarios."""
    return ASK_NETRA_SCENARIOS


def get_ask_scenario_by_id(scenario_id: str) -> Dict[str, Any]:
    """Retrieves a specific scenario by identifier."""
    for s in ASK_NETRA_SCENARIOS:
        if s["id"] == scenario_id:
            return s
    raise KeyError(f"Scenario '{scenario_id}' not found.")
