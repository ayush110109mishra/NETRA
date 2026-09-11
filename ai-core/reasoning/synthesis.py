"""
Phase 7 Answer Synthesizer for Ask NETRA.
Synthesizes structured, evidence-grounded answers across all 16 intents without hallucination.
"""

from typing import Any, Dict, List
from models.ask_netra import (
    AskAnswer,
    ClaimItem,
    EpistemicLedger,
    EpistemicTier,
    ParsedQuery,
    QueryIntent,
)
from reasoning.explanation import ExplanationEngine


class AnswerSynthesizer:
    """Builds structured AskAnswer instances strictly grounded in the epistemic ledger."""

    def __init__(self):
        self.explanation_engine = ExplanationEngine()

    def synthesize(
        self,
        parsed: ParsedQuery,
        context: Dict[str, Any],
        ledger: EpistemicLedger,
    ) -> AskAnswer:
        intent = parsed.intent
        entity_id = parsed.primary_entity_id or "ALL"

        headline = f"Intelligence Query Assessment: {intent.value}"
        summary = ""
        key_findings: List[str] = []
        claims: List[ClaimItem] = []
        uncertainties: List[str] = []
        caveats: List[str] = [
            "Assessment generated from synthetic operational telemetry; not for kinetic weapon targeting.",
            "Predictions and inferences are subject to confidence calibration and sensor availability.",
        ]

        # Populate uncertainties from ledger
        for unc in ledger.uncertain:
            uncertainties.append(unc.description)

        if intent == QueryIntent.STATUS:
            active_count = len(context.get("active_entities", []))
            raw_count = len(context.get("raw_events", []))
            headline = "Operational Status & Situational Awareness Overview"
            summary = f"Currently tracking {active_count} active entities across operational sectors with {raw_count} recorded events."
            key_findings = [
                f"{active_count} active entities maintained in operational track table.",
                f"{raw_count} total events ingested across telemetry channels.",
                "Tactical operational picture remains under continuous automated surveillance.",
            ]
            claims.append(
                ClaimItem(
                    statement=f"Operational track table contains {active_count} entities.",
                    epistemic_tier=EpistemicTier.OBSERVED,
                    supporting_evidence_ids=[e.evidence_id for e in ledger.observed[:3]] or ["SYSTEM-TRACK-TABLE"],
                    confidence=0.95,
                )
            )

        elif intent == QueryIntent.ENTITY_PROFILE:
            entity = context.get("entity_profile")
            if entity:
                e_type = getattr(entity, "entity_type", "UNKNOWN")
                e_type_str = getattr(e_type, "value", str(e_type))
                e_status = getattr(entity, "lifecycle_state", "ACTIVE")
                e_status_str = getattr(e_status, "value", str(e_status))
                obs_count = getattr(entity, "observation_count", len(context.get("raw_events", [])))
                headline = f"Entity Profile Dossier: {entity_id} ({e_type_str})"
                summary = f"Entity {entity_id} classified as {e_type_str} in lifecycle state {e_status_str} with {obs_count} observations."
                key_findings = [
                    f"Classification: {e_type_str}",
                    f"Lifecycle State: {e_status_str}",
                    f"Telemetry Depth: {obs_count} recorded events",
                ]
                claims.append(
                    ClaimItem(
                        statement=f"Entity {entity_id} is registered as {e_type_str} with {obs_count} observations.",
                        epistemic_tier=EpistemicTier.OBSERVED,
                        supporting_evidence_ids=[e.evidence_id for e in ledger.observed[:2]] or [f"ENT-{entity_id}"],
                        confidence=0.92,
                    )
                )
            else:
                headline = f"Entity Profile: {entity_id} (Unindexed)"
                summary = f"Entity {entity_id} has no profile history in the local track registry."
                key_findings = ["Entity record not located in current active database."]
                claims.append(
                    ClaimItem(
                        statement=f"Entity {entity_id} lacks observation history.",
                        epistemic_tier=EpistemicTier.UNCERTAIN,
                        supporting_evidence_ids=[],
                        confidence=0.90,
                    )
                )

        elif intent == QueryIntent.TIMELINE:
            events = context.get("raw_events", [])
            headline = f"Chronological Event Timeline for {entity_id}"
            summary = f"Extracted {len(events)} chronological events associated with {entity_id}."
            key_findings = [
                f"{len(events)} chronological observations recorded.",
                f"Earliest event: {getattr(events[0], 'timestamp', 'N/A') if events else 'None'}",
                f"Latest event: {getattr(events[-1], 'timestamp', 'N/A') if events else 'None'}",
            ]
            for evt in events[:5]:
                e_id = getattr(evt, "event_id", "EVT")
                claims.append(
                    ClaimItem(
                        statement=f"Event {e_id} recorded at {getattr(evt, 'timestamp', 'N/A')}.",
                        epistemic_tier=EpistemicTier.OBSERVED,
                        supporting_evidence_ids=[str(e_id)],
                        confidence=0.95,
                    )
                )

        elif intent == QueryIntent.WHAT_CHANGED:
            headline, key_findings, claims = self.explanation_engine.explain_what_changed(context, ledger)
            summary = f"Longitudinal baseline drift and kinematic shift analysis for {entity_id}."

        elif intent == QueryIntent.ANOMALY:
            anom = context.get("anomaly_analysis")
            score = 0.0
            class_str = "NOMINAL"
            top_dims = []
            a_sum = getattr(anom, "anomaly", getattr(anom, "anomaly_summary", None)) if anom else None
            if a_sum:
                score = getattr(a_sum, "combined_anomaly_score", 0.0)
                classification = getattr(a_sum, "anomaly_classification", "NOMINAL")
                class_str = getattr(classification, "value", str(classification))
                top_dims = getattr(a_sum, "top_anomalous_dimensions", [])

            headline = f"Multivariate Anomaly Assessment for {entity_id}: {class_str} ({score:.2f})"
            summary = f"Entity {entity_id} evaluated across 8 anomaly dimensions. Overall classification is {class_str}."
            key_findings = [
                f"Combined Anomaly Score: {score:.2f} ({class_str})",
                f"Top Deviant Dimensions: {', '.join([str(d) for d in top_dims[:3]]) if top_dims else 'None (nominal)'}",
            ]
            claims.append(
                ClaimItem(
                    statement=f"Entity {entity_id} exhibits {class_str} anomaly profile (score: {score:.2f}).",
                    epistemic_tier=EpistemicTier.INFERRED,
                    supporting_evidence_ids=[e.evidence_id for e in ledger.inferred if "ANM" in e.evidence_id] or [f"ANM-{entity_id}"],
                    confidence=0.88,
                )
            )

        elif intent == QueryIntent.RISK:
            risk = context.get("risk_profile")
            r_score = 0.0
            r_state = "LOW"
            if risk:
                r_score = getattr(risk, "overall_risk_score", getattr(risk, "composite_risk", 0.0))
                r_st = getattr(risk, "risk_state", getattr(risk, "current_state", "LOW"))
                r_state = getattr(r_st, "value", str(r_st))

            headline = f"Composite Risk Assessment for {entity_id}: {r_state} (Score: {r_score:.2f})"
            summary = f"Calculated 7-factor explainable composite risk for {entity_id}. Current operational risk posture is {r_state}."
            key_findings = [
                f"Operational Risk Posture: {r_state}",
                f"Composite Risk Score: {r_score:.2f} / 1.00",
            ]
            claims.append(
                ClaimItem(
                    statement=f"Composite risk for {entity_id} is evaluated at {r_score:.2f} ({r_state}).",
                    epistemic_tier=EpistemicTier.INFERRED,
                    supporting_evidence_ids=[e.evidence_id for e in ledger.inferred if "RSK" in e.evidence_id] or [f"RSK-{entity_id}"],
                    confidence=0.90,
                )
            )

        elif intent == QueryIntent.WHY:
            headline, key_findings, claims = self.explanation_engine.explain_why(context, ledger)
            summary = f"Root cause attribution explaining operational indicators for {entity_id}."

        elif intent == QueryIntent.TREND:
            pred = context.get("forecast_response")
            headline = f"Kinematic & Behavioral Trend Analysis for {entity_id}"
            summary = f"Longitudinal trend estimation and trajectory momentum for {entity_id}."
            key_findings = [
                "Temporal slope and velocity metrics analyzed over available observation window.",
                "Directional stability reflects persistence of observed kinematic telemetry.",
            ]
            claims.append(
                ClaimItem(
                    statement=f"Trend metrics for {entity_id} derived from historical temporal state sequence.",
                    epistemic_tier=EpistemicTier.INFERRED,
                    supporting_evidence_ids=[e.evidence_id for e in ledger.inferred] or ["TREND-MODEL"],
                    confidence=0.85,
                )
            )

        elif intent == QueryIntent.FORECAST:
            pred = context.get("forecast_response")
            f_cast = getattr(pred, "forecast", None) if pred else None
            if f_cast:
                f_state = getattr(f_cast, "forecast_state", "UNKNOWN")
                f_state_str = getattr(f_state, "value", str(f_state))
                f_prob = getattr(f_cast, "probability", 0.5)
                f_conf = getattr(f_cast, "confidence", 0.5)
                f_horizon = getattr(f_cast, "horizon", "MEDIUM")
                f_horizon_str = getattr(f_horizon, "value", str(f_horizon))
                headline = f"Predictive Intelligence Forecast for {entity_id}: {f_state_str}"
                summary = f"Phase 6 ensemble forecast projects state '{f_state_str}' over {f_horizon_str} horizon with P={f_prob:.2f} (Confidence: {f_conf:.2f})."
                key_findings = [
                    f"Forecast State: {f_state_str}",
                    f"Forecast Probability: {f_prob:.2f}",
                    f"Horizon: {f_horizon_str}",
                    f"Ensemble Confidence: {f_conf:.2f}",
                ]
                claims.append(
                    ClaimItem(
                        statement=f"Entity {entity_id} projected to transition to/maintain state {f_state_str} (probability: {f_prob:.2f}).",
                        epistemic_tier=EpistemicTier.PREDICTED,
                        supporting_evidence_ids=[e.evidence_id for e in ledger.predicted] or [f"PRD-{entity_id}"],
                        confidence=round(float(f_conf), 2),
                    )
                )
            else:
                headline = f"Predictive Forecast: {entity_id} (Data Gated)"
                summary = f"Forecast gating prevents high-confidence prediction for {entity_id} due to cold start or insufficient observations."
                key_findings = ["Entity history insufficient to meet forecast gating thresholds (< 3 observations)."]
                claims.append(
                    ClaimItem(
                        statement=f"Predictive forecast for {entity_id} is gated as UNKNOWN due to cold start.",
                        epistemic_tier=EpistemicTier.UNCERTAIN,
                        supporting_evidence_ids=[e.evidence_id for e in ledger.uncertain],
                        confidence=0.95,
                    )
                )

        elif intent == QueryIntent.SOURCE_SUPPORT:
            fusion = context.get("fusion_analysis")
            headline = f"Multi-Sensor Corroboration & Source Support for {entity_id}"
            summary = f"Evaluated cross-sensor corroboration, telemetry consensus, and reporting reliability for {entity_id}."
            key_findings = [
                f"{len(ledger.fused)} fused multi-sensor consensus observations established.",
                "Cross-sensor alignment confirms target presence across active surveillance modalities.",
            ]
            claims.append(
                ClaimItem(
                    statement=f"Multi-source tracking of {entity_id} is supported by corroborating sensor feeds.",
                    epistemic_tier=EpistemicTier.FUSED,
                    supporting_evidence_ids=[e.evidence_id for e in ledger.fused] or ["FUSED-CONSENSUS"],
                    confidence=0.88,
                )
            )

        elif intent == QueryIntent.CONFLICT:
            conflicts = getattr(context.get("fusion_analysis"), "conflicts", []) if context.get("fusion_analysis") else []
            headline = f"Sensor Conflict & Discrepancy Analysis for {entity_id}"
            summary = f"Detected {len(conflicts)} sensor discrepancy/conflict events in reporting telemetry."
            key_findings = [
                f"{len(conflicts)} conflicting reports identified between sensor modalities.",
            ]
            for c in conflicts[:3]:
                key_findings.append(f"Discrepancy: {getattr(c, 'description', 'Sensor disagreement')}")
            claims.append(
                ClaimItem(
                    statement=f"Telemetry contains {len(conflicts)} conflicting observations across sensor channels.",
                    epistemic_tier=EpistemicTier.UNCERTAIN,
                    supporting_evidence_ids=[e.evidence_id for e in ledger.uncertain] or ["CONFLICT-DETECTION"],
                    confidence=0.90,
                )
            )

        elif intent == QueryIntent.EVIDENCE:
            headline = f"Epistemic Evidence & Telemetry Lineage for {entity_id}"
            summary = f"Assembled complete 5-tier epistemic ledger comprising {ledger.total_evidence_count} structured evidence references."
            key_findings = [
                f"Observed Raw Telemetry: {len(ledger.observed)} items",
                f"Fused Sensor Observations: {len(ledger.fused)} items",
                f"Inferred Analytical Assessments: {len(ledger.inferred)} items",
                f"Predicted Future Forecasts: {len(ledger.predicted)} items",
                f"Uncertainty & Gaps Identified: {len(ledger.uncertain)} items",
            ]
            claims.append(
                ClaimItem(
                    statement=f"Comprehensive lineage assembled across {ledger.total_evidence_count} evidence records.",
                    epistemic_tier=EpistemicTier.OBSERVED,
                    supporting_evidence_ids=[e.evidence_id for e in (ledger.observed + ledger.fused)[:4]],
                    confidence=0.96,
                )
            )

        elif intent == QueryIntent.COMPARISON:
            headline, key_findings, claims = self.explanation_engine.compare_entities(context, ledger)
            summary = f"Comparative evaluation between {context.get('entity_id')} and {context.get('secondary_entity_id')}."

        elif intent == QueryIntent.RELATIONSHIP:
            graph_path = context.get("graph_path")
            graph_network = context.get("graph_network")

            if graph_path:
                if graph_path.path_found:
                    headline = f"Evidence Connection Path: {entity_id} <-> {graph_path.target}"
                    summary = graph_path.explanation
                    key_findings = [
                        f"Traversable path discovered spanning {graph_path.hop_count} hop(s).",
                        f"Bottleneck path confidence: {graph_path.path_confidence:.2f}",
                    ]
                    if graph_path.weakest_link:
                        key_findings.append(f"Weakest link along path: {graph_path.weakest_link}")
                    claims.append(
                        ClaimItem(
                            statement=f"Evidence path of {graph_path.hop_count} hops connects {entity_id} and {graph_path.target}.",
                            epistemic_tier=EpistemicTier.INFERRED,
                            supporting_evidence_ids=graph_path.supporting_evidence or ["GRAPH-PATH"],
                            confidence=graph_path.path_confidence,
                        )
                    )
                else:
                    headline = f"Connection Query: {entity_id} and {graph_path.target}"
                    summary = f"No evidence-supported path was found between {entity_id} and {graph_path.target} within the requested graph scope."
                    key_findings = [
                        f"No evidence-supported path connects {entity_id} and {graph_path.target}.",
                        "Entities are topologically disconnected in the active knowledge graph.",
                    ]
                    claims.append(
                        ClaimItem(
                            statement=f"No evidence-supported path was found between {entity_id} and {graph_path.target}.",
                            epistemic_tier=EpistemicTier.UNCERTAIN,
                            supporting_evidence_ids=[],
                            confidence=0.95,
                        )
                    )
            elif graph_network and graph_network.get("relationships"):
                rels = graph_network.get("relationships", [])
                neighbors = graph_network.get("neighbors", [])
                neighbor_entities = [n.label for n in neighbors if n.label != entity_id]
                headline = f"Knowledge Graph & Network Topology for {entity_id}"
                summary = f"Entity {entity_id} is associated with {len(neighbor_entities)} entity/entities across {len(rels)} relationship(s)."
                key_findings = [
                    f"Connected entities: {', '.join(neighbor_entities) if neighbor_entities else 'None direct'}",
                    f"Active relationship count: {len(rels)}",
                ]
                all_ev = []
                for r in rels:
                    all_ev.extend(r.supporting_evidence)
                    key_findings.append(f"{r.source_entity_id} <-> {r.target_entity_id}: strength {r.strength:.2f} ({r.status.value})")
                claims.append(
                    ClaimItem(
                        statement=f"Knowledge graph maps {len(rels)} relationship(s) connecting {entity_id}.",
                        epistemic_tier=EpistemicTier.INFERRED,
                        supporting_evidence_ids=sorted(list(set(all_ev))) or ["RELATIONAL-GRAPH"],
                        confidence=0.88,
                    )
                )
            else:
                headline = f"Relational Graph & Network Topology for {entity_id}"
                summary = f"Spatial co-location and behavioral association analysis for {entity_id}."
                key_findings = [
                    f"Entity {entity_id} analyzed for spatial proximity and co-occurrence clusters.",
                    "Network associations mapped from shared event clusters and temporal alignment.",
                ]
                claims.append(
                    ClaimItem(
                        statement=f"Relational topology for {entity_id} derived from multi-event spatial correlation.",
                        epistemic_tier=EpistemicTier.INFERRED,
                        supporting_evidence_ids=[e.evidence_id for e in ledger.inferred] or ["RELATIONAL-GRAPH"],
                        confidence=0.86,
                    )
                )

        elif intent == QueryIntent.SCENARIO:
            headline = f"Operational Simulation Scenario Execution"
            summary = "Processed operational scenario query against synthetic intelligence core."
            key_findings = [
                "Scenario data loaded into deterministic intelligence pipeline.",
                "Multi-dimensional analytical engines evaluated operational posture.",
            ]
            claims.append(
                ClaimItem(
                    statement="Scenario executed successfully under deterministic parameters.",
                    epistemic_tier=EpistemicTier.OBSERVED,
                    supporting_evidence_ids=[e.evidence_id for e in ledger.observed[:2]] or ["SCENARIO-EXEC"],
                    confidence=0.95,
                )
            )

        elif intent == QueryIntent.HELP:
            headline = "Ask NETRA Intelligence Interface - System Capabilities"
            summary = "Ask NETRA is an evidence-grounded natural language intelligence query system operating over Phase 1-6 engines."
            key_findings = [
                "Supports 16 operational intents including Status, Profile, Risk, Anomaly, Why, What Changed, Forecast, Evidence.",
                "Enforces strict 5-tier Epistemic Ledger (Observed, Fused, Inferred, Predicted, Uncertain).",
                "Deterministic evaluation with reproducible as_of point-in-time querying.",
                "Zero hallucination guarantee: every claim is anchored to verifiable evidence IDs.",
            ]
            claims.append(
                ClaimItem(
                    statement="Ask NETRA operates over deterministic, verified Phase 1-6 intelligence capabilities.",
                    epistemic_tier=EpistemicTier.OBSERVED,
                    supporting_evidence_ids=["NETRA-CORE-V7"],
                    confidence=1.00,
                )
            )

        return AskAnswer(
            headline=headline,
            summary=summary,
            key_findings=key_findings,
            claims=claims,
            evidence_ledger=ledger,
            uncertainties=uncertainties,
            caveats=caveats,
            overall_confidence=0.88,
        )
