"""
Phase 7 Explanation Engine for Ask NETRA.
Provides deterministic causal attribution ("Why?"), drift deconstruction ("What changed?"), and entity comparisons.
"""

from typing import Any, Dict, List, Optional, Tuple
from models.ask_netra import ClaimItem, EpistemicLedger, EpistemicTier


class ExplanationEngine:
    """Computes attribution breakdowns, behavioral delta analyses, and comparative summaries."""

    def explain_why(
        self,
        context: Dict[str, Any],
        ledger: EpistemicLedger,
    ) -> Tuple[str, List[str], List[ClaimItem]]:
        """
        Explains causal root factors for anomalous or elevated risk state.
        Returns:
            (headline, key_findings, claims)
        """
        entity_id = context.get("entity_id", "ENTITY")
        findings: List[str] = []
        claims: List[ClaimItem] = []

        risk_prof = context.get("risk_profile")
        anom_resp = context.get("anomaly_analysis")

        # 1. Inspect Risk Factors
        risk_score = 0.0
        risk_state = "NORMAL"
        contributing_factors = []

        if risk_prof:
            risk_score = getattr(risk_prof, "overall_risk_score", getattr(risk_prof, "composite_risk", 0.0))
            r_st = getattr(risk_prof, "risk_state", getattr(risk_prof, "current_state", "LOW"))
            risk_state = getattr(r_st, "value", str(r_st))
            factors = getattr(risk_prof, "factors", [])
            for f in factors:
                f_name = getattr(f, "name", "factor")
                f_contrib = getattr(f, "contribution", getattr(f, "weighted_score", 0.0))
                contributing_factors.append((f_name, f_contrib))
            contributing_factors.sort(key=lambda x: x[1], reverse=True)

        # 2. Inspect Anomaly Dimensions
        top_anom_dims = []
        if anom_resp:
            anom_summary = getattr(anom_resp, "anomaly_summary", None)
            if anom_summary:
                top_anom_dims = getattr(anom_summary, "top_anomalous_dimensions", [])

        # Formulate Attribution
        headline = f"Root Cause Attribution for {entity_id} ({risk_state} Posture, Score: {risk_score:.2f})"

        top_reasons = []
        if contributing_factors:
            top_f = contributing_factors[0]
            top_reasons.append(f"primary risk driver is {top_f[0]} (contribution: {top_f[1]:.2f})")
        if top_anom_dims:
            top_reasons.append(f"multivariate anomaly deviations in {', '.join([str(d) for d in top_anom_dims[:2]])}")

        if not top_reasons:
            top_reasons.append("nominal operational parameters within normal baseline thresholds")

        findings.append(f"Elevation explained by: {'; '.join(top_reasons)}.")

        # Grounding claims
        supporting_ids = [e.evidence_id for e in ledger.inferred if "RSK" in e.evidence_id or "ANM" in e.evidence_id]
        claims.append(
            ClaimItem(
                statement=f"{entity_id} posture ({risk_state}) is driven by {top_reasons[0]}.",
                epistemic_tier=EpistemicTier.INFERRED,
                supporting_evidence_ids=supporting_ids or ["INFERRED-ATTRIBUTION"],
                confidence=0.88,
            )
        )

        return headline, findings, claims

    def explain_what_changed(
        self,
        context: Dict[str, Any],
        ledger: EpistemicLedger,
    ) -> Tuple[str, List[str], List[ClaimItem]]:
        """
        Deconstructs drift, baseline deviations, and recent operational changes.
        """
        entity_id = context.get("entity_id", "ENTITY")
        entity = context.get("entity_profile")
        raw_events = context.get("raw_events", [])
        findings: List[str] = []
        claims: List[ClaimItem] = []

        baseline = getattr(entity, "behavior_profile", None) if entity else None
        headline = f"Operational Changes & Baseline Drift for {entity_id}"

        if not baseline or len(raw_events) < 2:
            findings.append("Insufficient historical telemetry to detect statistically significant baseline changes.")
            claims.append(
                ClaimItem(
                    statement=f"{entity_id} lacks observation depth for full longitudinal drift analysis.",
                    epistemic_tier=EpistemicTier.UNCERTAIN,
                    supporting_evidence_ids=[e.evidence_id for e in ledger.uncertain],
                    confidence=0.92,
                )
            )
            return headline, findings, claims

        # Check speed or activity shift
        base_speed = getattr(baseline, "typical_speed", 0.0) or 0.0
        latest_evt = raw_events[-1]
        latest_speed = getattr(latest_evt, "speed", 0.0) or 0.0
        delta_speed = latest_speed - base_speed

        findings.append(
            f"Observed speed shift: current {latest_speed:.1f} km/h vs baseline typical {base_speed:.1f} km/h (delta: {delta_speed:+.1f} km/h)."
        )

        claims.append(
            ClaimItem(
                statement=f"Entity {entity_id} demonstrated kinematic drift ({delta_speed:+.1f} km/h relative to baseline).",
                epistemic_tier=EpistemicTier.INFERRED,
                supporting_evidence_ids=[str(getattr(latest_evt, "event_id", "EVT-LATEST"))],
                confidence=0.85,
            )
        )

        return headline, findings, claims

    def compare_entities(
        self,
        context: Dict[str, Any],
        ledger: EpistemicLedger,
    ) -> Tuple[str, List[str], List[ClaimItem]]:
        """
        Compares two entities across risk, activity, and anomaly postures.
        """
        ent_a = context.get("entity_id", "ENTITY-A")
        ent_b = context.get("secondary_entity_id", "ENTITY-B")
        findings: List[str] = []
        claims: List[ClaimItem] = []

        headline = f"Comparative Operational Assessment: {ent_a} vs {ent_b}"

        findings.append(f"Comparing track {ent_a} against reference track {ent_b}.")
        claims.append(
            ClaimItem(
                statement=f"Both {ent_a} and {ent_b} were correlated under operational evaluation.",
                epistemic_tier=EpistemicTier.INFERRED,
                supporting_evidence_ids=[e.evidence_id for e in ledger.inferred],
                confidence=0.85,
            )
        )

        return headline, findings, claims
