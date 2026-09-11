"""
Phase 7 Grounded Evidence Ledger for Ask NETRA.
Indexes evidence items and categorizes them into the strict 5-tier epistemic ledger:
OBSERVED, FUSED, INFERRED, PREDICTED, UNCERTAIN.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from models.ask_netra import EpistemicLedger, EpistemicTier, EvidenceReference


class EvidenceLedgerBuilder:
    """Extracts, indexes, and categorizes evidence references across execution contexts."""

    def build_ledger(self, context: Dict[str, Any], max_items: int = 20) -> EpistemicLedger:
        ledger = EpistemicLedger()

        # 1. OBSERVED: Raw Events & Sensor Telemetry
        raw_events = context.get("raw_events", [])
        for evt in raw_events[:max_items]:
            evt_id = getattr(evt, "event_id", None) or getattr(evt, "id", None) or f"EVT-{id(evt)}"
            evt_type = getattr(evt, "event_type", "OBSERVATION")
            ts = getattr(evt, "timestamp", None)
            src = getattr(evt, "source", "SENSOR")
            src_str = getattr(src, "value", str(src)) if hasattr(src, "value") else str(src)
            conf = getattr(evt, "confidence", 0.90) or 0.90

            desc = f"{evt_type} recorded by {src_str}"
            if hasattr(evt, "location") and evt.location:
                desc += f" at ({evt.location.latitude:.3f}, {evt.location.longitude:.3f})"

            ledger.observed.append(
                EvidenceReference(
                    evidence_id=str(evt_id),
                    epistemic_tier=EpistemicTier.OBSERVED,
                    source=src_str,
                    description=desc,
                    confidence=round(float(conf), 2),
                    timestamp=ts,
                    metadata={"event_type": str(evt_type)},
                )
            )

        # 2. FUSED: Multi-Source Fusion
        fusion = context.get("fusion_analysis")
        if fusion:
            fused_obs = getattr(fusion, "fused_observations", [])
            for f_obs in fused_obs[:max_items]:
                f_id = getattr(f_obs, "fused_id", f"FUS-{id(f_obs)}")
                c_sources = getattr(f_obs, "contributing_sources", [])
                c_conf = getattr(f_obs, "fusion_confidence", 0.85)
                f_ts = getattr(f_obs, "timestamp", None)
                ledger.fused.append(
                    EvidenceReference(
                        evidence_id=str(f_id),
                        epistemic_tier=EpistemicTier.FUSED,
                        source=f"FUSION({','.join([str(s) for s in c_sources])})",
                        description=f"Corroborated track from {len(c_sources)} sensors (agreement: {c_conf:.2f})",
                        confidence=round(float(c_conf), 2),
                        timestamp=f_ts,
                        metadata={"contributing_sources": [str(s) for s in c_sources]},
                    )
                )

        # 3. INFERRED: Anomalies and Risk Assessments
        anom = context.get("anomaly_analysis")
        if anom:
            anom_summary = getattr(anom, "anomaly", getattr(anom, "anomaly_summary", None))
            if anom_summary:
                score = getattr(anom_summary, "combined_anomaly_score", 0.0)
                classification = getattr(anom_summary, "anomaly_classification", "NOMINAL")
                class_str = getattr(classification, "value", str(classification))
                top_dims = getattr(anom_summary, "top_anomalous_dimensions", [])
                ledger.inferred.append(
                    EvidenceReference(
                        evidence_id=f"ANM-{getattr(anom, 'entity_id', 'ENT')}-SCORE",
                        epistemic_tier=EpistemicTier.INFERRED,
                        source="ANOMALY_ENGINE",
                        description=f"8D Anomaly evaluation: {class_str} ({score:.2f}) led by {', '.join([str(d) for d in top_dims[:2]])}",
                        confidence=0.88,
                        timestamp=context.get("as_of"),
                        metadata={"score": score, "classification": class_str},
                    )
                )

        risk = context.get("risk_profile")
        if risk:
            r_score = getattr(risk, "overall_risk_score", getattr(risk, "composite_risk", 0.0))
            r_state = getattr(risk, "risk_state", getattr(risk, "current_state", "LOW"))
            r_state_str = getattr(r_state, "value", str(r_state))
            ledger.inferred.append(
                EvidenceReference(
                    evidence_id=f"RSK-{context.get('entity_id', 'ENT')}-PROFILE",
                    epistemic_tier=EpistemicTier.INFERRED,
                    source="RISK_ENGINE",
                    description=f"Explainable 7-factor composite risk: {r_state_str} ({r_score:.2f})",
                    confidence=0.90,
                    timestamp=context.get("as_of"),
                    metadata={"risk_score": r_score, "state": r_state_str},
                )
            )

        # 4. PREDICTED: Phase 6 Forecasts
        pred = context.get("forecast_response")
        if pred:
            f_cast = getattr(pred, "forecast", None)
            if f_cast:
                p_state = getattr(f_cast, "forecast_state", "UNKNOWN")
                p_state_str = getattr(p_state, "value", str(p_state))
                p_prob = getattr(f_cast, "probability", 0.5)
                p_conf = getattr(f_cast, "confidence", 0.5)
                p_target = getattr(f_cast, "target", "ACTIVITY")
                p_target_str = getattr(p_target, "value", str(p_target))
                p_horizon = getattr(f_cast, "horizon", "MEDIUM")
                p_horizon_str = getattr(p_horizon, "value", str(p_horizon))
                ledger.predicted.append(
                    EvidenceReference(
                        evidence_id=f"PRD-{getattr(pred, 'prediction_id', 'FCST')}",
                        epistemic_tier=EpistemicTier.PREDICTED,
                        source="PREDICTION_ENGINE",
                        description=f"Forecast {p_target_str} -> {p_state_str} over {p_horizon_str} horizon (P={p_prob:.2f}, Conf={p_conf:.2f})",
                        confidence=round(float(p_conf), 2),
                        timestamp=context.get("as_of"),
                        metadata={"probability": p_prob, "state": p_state_str, "horizon": p_horizon_str},
                    )
                )

        # 5. UNCERTAIN: Conflicts, Gaps, Contradictions, Cold Starts
        if fusion:
            conflicts = getattr(fusion, "conflicts", [])
            for c in conflicts[:max_items]:
                c_id = getattr(c, "conflict_id", f"UNC-{id(c)}")
                c_desc = getattr(c, "description", "Sensor discrepancy detected")
                c_sources = getattr(c, "conflicting_sources", [])
                ledger.uncertain.append(
                    EvidenceReference(
                        evidence_id=str(c_id),
                        epistemic_tier=EpistemicTier.UNCERTAIN,
                        source="CONFLICT_DETECTOR",
                        description=f"{c_desc} between {','.join([str(s) for s in c_sources])}",
                        confidence=0.75,
                        timestamp=context.get("as_of"),
                        metadata={"sources": [str(s) for s in c_sources]},
                    )
                )

        if not raw_events and context.get("entity_id"):
            ledger.uncertain.append(
                EvidenceReference(
                    evidence_id=f"UNC-COLD-{context.get('entity_id')}",
                    epistemic_tier=EpistemicTier.UNCERTAIN,
                    source="SYSTEM",
                    description=f"Cold start limit: Entity {context.get('entity_id')} has sparse or no historical observations.",
                    confidence=0.95,
                    timestamp=context.get("as_of"),
                )
            )

        return ledger
