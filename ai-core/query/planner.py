"""
Phase 7 Query Planner for Ask NETRA.
Constructs inspectable, multi-step execution plans mapping query intents to Phase 1-6 engines.
"""

import hashlib
from typing import List
from models.ask_netra import ParsedQuery, QueryIntent, QueryPlan, QueryPlanStep


class QueryPlanner:
    """Generates deterministic execution plans composed of modular engine steps."""

    def plan(self, parsed: ParsedQuery) -> QueryPlan:
        """Constructs an ordered DAG plan of execution steps for the parsed query."""
        plan_id = f"PLN-{hashlib.sha256((parsed.query_id + parsed.intent.value).encode()).hexdigest()[:10]}"
        steps: List[QueryPlanStep] = []
        entity_id = parsed.primary_entity_id or "ALL"
        sector_id = parsed.sector_id

        if parsed.intent == QueryIntent.STATUS:
            steps = [
                QueryPlanStep(step_id="step_1", engine="event_engine", action="fetch_recent_events", parameters={"limit": parsed.filters.limit}),
                QueryPlanStep(step_id="step_2", engine="entity_engine", action="fetch_active_entities", parameters={"sector_id": sector_id}, depends_on=["step_1"]),
                QueryPlanStep(step_id="step_3", engine="risk_engine", action="evaluate_sector_risk", parameters={"sector_id": sector_id}, depends_on=["step_2"]),
                QueryPlanStep(step_id="step_4", engine="reasoning_engine", action="synthesize_status", parameters={}, depends_on=["step_3"]),
            ]
        elif parsed.intent == QueryIntent.ENTITY_PROFILE:
            steps = [
                QueryPlanStep(step_id="step_1", engine="entity_engine", action="get_profile", parameters={"entity_id": entity_id}),
                QueryPlanStep(step_id="step_2", engine="risk_engine", action="get_entity_risk", parameters={"entity_id": entity_id}, depends_on=["step_1"]),
                QueryPlanStep(step_id="step_3", engine="reasoning_engine", action="synthesize_profile", parameters={"entity_id": entity_id}, depends_on=["step_2"]),
            ]
        elif parsed.intent == QueryIntent.TIMELINE:
            steps = [
                QueryPlanStep(step_id="step_1", engine="event_engine", action="get_entity_timeline", parameters={"entity_id": entity_id, "time_range": parsed.time_range}),
                QueryPlanStep(step_id="step_2", engine="reasoning_engine", action="synthesize_timeline", parameters={"entity_id": entity_id}, depends_on=["step_1"]),
            ]
        elif parsed.intent == QueryIntent.WHAT_CHANGED:
            steps = [
                QueryPlanStep(step_id="step_1", engine="entity_engine", action="get_baseline_drift", parameters={"entity_id": entity_id}),
                QueryPlanStep(step_id="step_2", engine="anomaly_engine", action="get_recent_anomalies", parameters={"entity_id": entity_id}, depends_on=["step_1"]),
                QueryPlanStep(step_id="step_3", engine="reasoning_engine", action="explain_changes", parameters={"entity_id": entity_id}, depends_on=["step_2"]),
            ]
        elif parsed.intent == QueryIntent.ANOMALY:
            steps = [
                QueryPlanStep(step_id="step_1", engine="entity_engine", action="get_entity_observations", parameters={"entity_id": entity_id}),
                QueryPlanStep(step_id="step_2", engine="anomaly_engine", action="analyze_8d_anomalies", parameters={"entity_id": entity_id}, depends_on=["step_1"]),
                QueryPlanStep(step_id="step_3", engine="reasoning_engine", action="ground_anomalies", parameters={"entity_id": entity_id}, depends_on=["step_2"]),
            ]
        elif parsed.intent == QueryIntent.RISK:
            steps = [
                QueryPlanStep(step_id="step_1", engine="entity_engine", action="get_profile", parameters={"entity_id": entity_id}),
                QueryPlanStep(step_id="step_2", engine="risk_engine", action="calculate_phase4_risk", parameters={"entity_id": entity_id}, depends_on=["step_1"]),
                QueryPlanStep(step_id="step_3", engine="reasoning_engine", action="synthesize_risk", parameters={"entity_id": entity_id}, depends_on=["step_2"]),
            ]
        elif parsed.intent == QueryIntent.WHY:
            steps = [
                QueryPlanStep(step_id="step_1", engine="risk_engine", action="get_risk_breakdown", parameters={"entity_id": entity_id}),
                QueryPlanStep(step_id="step_2", engine="anomaly_engine", action="get_anomaly_attribution", parameters={"entity_id": entity_id}, depends_on=["step_1"]),
                QueryPlanStep(step_id="step_3", engine="reasoning_engine", action="explain_root_causes", parameters={"entity_id": entity_id}, depends_on=["step_2"]),
            ]
        elif parsed.intent == QueryIntent.TREND:
            steps = [
                QueryPlanStep(step_id="step_1", engine="prediction_engine", action="calculate_trend_metrics", parameters={"entity_id": entity_id}),
                QueryPlanStep(step_id="step_2", engine="reasoning_engine", action="explain_trend", parameters={"entity_id": entity_id}, depends_on=["step_1"]),
            ]
        elif parsed.intent == QueryIntent.FORECAST:
            steps = [
                QueryPlanStep(step_id="step_1", engine="prediction_engine", action="generate_forecast", parameters={"entity_id": entity_id}),
                QueryPlanStep(step_id="step_2", engine="reasoning_engine", action="synthesize_forecast", parameters={"entity_id": entity_id}, depends_on=["step_1"]),
            ]
        elif parsed.intent == QueryIntent.SOURCE_SUPPORT:
            steps = [
                QueryPlanStep(step_id="step_1", engine="fusion_engine", action="get_source_corroboration", parameters={"entity_id": entity_id}),
                QueryPlanStep(step_id="step_2", engine="reasoning_engine", action="synthesize_source_support", parameters={"entity_id": entity_id}, depends_on=["step_1"]),
            ]
        elif parsed.intent == QueryIntent.CONFLICT:
            steps = [
                QueryPlanStep(step_id="step_1", engine="fusion_engine", action="get_source_conflicts", parameters={"entity_id": entity_id}),
                QueryPlanStep(step_id="step_2", engine="reasoning_engine", action="synthesize_conflicts", parameters={"entity_id": entity_id}, depends_on=["step_1"]),
            ]
        elif parsed.intent == QueryIntent.EVIDENCE:
            steps = [
                QueryPlanStep(step_id="step_1", engine="fusion_engine", action="get_evidence_lineage", parameters={"entity_id": entity_id}),
                QueryPlanStep(step_id="step_2", engine="reasoning_engine", action="build_epistemic_audit_trail", parameters={"entity_id": entity_id}, depends_on=["step_1"]),
            ]
        elif parsed.intent == QueryIntent.COMPARISON:
            secondary_id = parsed.secondary_entity_id or "BASELINE"
            steps = [
                QueryPlanStep(step_id="step_1", engine="entity_engine", action="get_profile", parameters={"entity_id": entity_id}),
                QueryPlanStep(step_id="step_2", engine="entity_engine", action="get_profile", parameters={"entity_id": secondary_id}),
                QueryPlanStep(step_id="step_3", engine="reasoning_engine", action="compare_entities", parameters={"entity_a": entity_id, "entity_b": secondary_id}, depends_on=["step_1", "step_2"]),
            ]
        elif parsed.intent == QueryIntent.RELATIONSHIP:
            steps = [
                QueryPlanStep(step_id="step_1", engine="entity_engine", action="get_entity_clusters", parameters={"entity_id": entity_id}),
                QueryPlanStep(step_id="step_2", engine="reasoning_engine", action="synthesize_relationships", parameters={"entity_id": entity_id}, depends_on=["step_1"]),
            ]
        elif parsed.intent == QueryIntent.SCENARIO:
            steps = [
                QueryPlanStep(step_id="step_1", engine="simulation_engine", action="evaluate_scenario", parameters={"query": parsed.raw_query}),
                QueryPlanStep(step_id="step_2", engine="reasoning_engine", action="synthesize_scenario_output", parameters={}, depends_on=["step_1"]),
            ]
        elif parsed.intent == QueryIntent.HELP:
            steps = [
                QueryPlanStep(step_id="step_1", engine="reasoning_engine", action="provide_capabilities_help", parameters={}),
            ]
        else:
            steps = [
                QueryPlanStep(step_id="step_1", engine="reasoning_engine", action="general_inquiry", parameters={"query": parsed.raw_query}),
            ]

        return QueryPlan(
            plan_id=plan_id,
            query_id=parsed.query_id,
            intent=parsed.intent,
            steps=steps,
            estimated_cost_ms=len(steps) * 1.5,
        )
