"""
Phase 4 Risk Aggregation Engine for NETRA (phase4-v1).
Implements the 7-factor explainable risk equation:
Risk = 0.20*Event + 0.15*Dev + 0.25*Anom + 0.15*Cluster + 0.10*Persist + 0.10*Trend + 0.05*Evidence.
"""

from typing import List, Dict, Optional, Any
from config import Phase4RiskWeights, HysteresisConfig, default_config
from models.common import RiskLevel
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from models.anomaly_intelligence import (
    AnomalySummary,
    AnomalyTrend,
    AnomalyPersistence,
    AnomalyPersistenceState,
    TrendDirection,
)
from models.risk_intelligence import (
    RiskState,
    RiskTrendDirection,
    Phase4RiskFactor,
    RiskPersistenceProfile,
    Phase4RiskProfile,
)
from events.models import EVENT_TYPE_SEVERITY_BASELINE


class Phase4RiskAggregator:
    """Computes explainable, mathematically consistent phase4-v1 risk profiles."""

    def __init__(
        self,
        weights: Optional[Phase4RiskWeights] = None,
        hysteresis: Optional[HysteresisConfig] = None,
    ):
        self.weights = weights or default_config.phase4_risk_weights
        self.hysteresis = hysteresis or default_config.hysteresis

    def compute_risk(
        self,
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        anomaly_summary: AnomalySummary,
        anomaly_trend: AnomalyTrend,
        anomaly_persistence: AnomalyPersistence,
        baseline: Optional[EntityBehaviorProfile] = None,
        context: Optional[Dict[str, Any]] = None,
        previous_risk: Optional[float] = None,
        previous_state: Optional[RiskState] = None,
        risk_history: Optional[List[float]] = None,
    ) -> Phase4RiskProfile:
        """
        Evaluate Phase 4 analytical risk (phase4-v1).
        Returns fully attributed Phase4RiskProfile.
        """
        # 1. Factor: Event Risk [0.0 - 1.0]
        if events:
            event_severities = []
            for e in events:
                evt_type = e.event_type.lower()
                base_sev = EVENT_TYPE_SEVERITY_BASELINE.get(evt_type, 0.25)
                # Check priority hint if present
                priority = getattr(e, "priority_hint", None)
                if priority:
                    p_weights = {"INFO": 0.1, "LOW": 0.3, "MEDIUM": 0.6, "HIGH": 0.8, "CRITICAL": 1.0}
                    pval = p_weights.get(priority.value if hasattr(priority, "value") else str(priority), base_sev)
                    base_sev = round((base_sev * 0.5) + (pval * 0.5), 3)
                event_severities.append(base_sev)
            event_risk_score = min(1.0, round(sum(event_severities) / len(event_severities), 4))
        else:
            event_risk_score = 0.10

        # 2. Factor: Behavioral Deviation [0.0 - 1.0]
        if baseline and events:
            curr_act = [
                float(e.attributes.get("activity_level", 0.5))
                for e in events
                if "activity_level" in e.attributes
            ]
            if curr_act:
                avg_act = sum(curr_act) / len(curr_act)
                act_dev = abs(avg_act - baseline.average_activity)
            else:
                act_dev = 0.10
            behavioral_score = min(1.0, round(act_dev, 4))
        else:
            behavioral_score = 0.10

        # 3. Factor: Anomaly Score [0.0 - 1.0]
        anomaly_factor_score = round(anomaly_summary.score, 4)

        # 4. Factor: Cluster Context [0.0 - 1.0]
        cluster_score = 0.10
        if context:
            if "cluster_risk" in context:
                cluster_score = float(context["cluster_risk"])
            elif "cluster_cohesion" in context:
                cluster_score = min(1.0, float(context["cluster_cohesion"]) * 0.8)
        # Check event cluster affiliation
        for e in events:
            if e.attributes.get("cluster_id"):
                cluster_score = max(cluster_score, 0.50)
                break
        cluster_score = min(1.0, round(cluster_score, 4))

        # 5. Factor: Anomaly Persistence [0.0 - 1.0]
        p_state_map = {
            AnomalyPersistenceState.ESCALATING: 1.00,
            AnomalyPersistenceState.PERSISTENT: 0.80,
            AnomalyPersistenceState.RECURRING: 0.65,
            AnomalyPersistenceState.DECLINING: 0.30,
            AnomalyPersistenceState.TRANSIENT: 0.20,
        }
        persistence_score = p_state_map.get(anomaly_persistence.state, 0.20)

        # 6. Factor: Anomaly Trend [0.0 - 1.0]
        if anomaly_trend.direction == TrendDirection.INCREASE:
            trend_score = min(1.0, round(0.70 + max(0.0, anomaly_trend.delta) * 0.6, 4))
        elif anomaly_trend.direction == TrendDirection.DECREASE:
            trend_score = 0.20
        elif anomaly_trend.direction == TrendDirection.STABLE:
            trend_score = 0.40
        else:
            trend_score = 0.30

        # 7. Factor: Evidence Quality [0.0 - 1.0]
        # Direct evidence confirmation weighting
        conf_map = {
            "STRONGLY_CORROBORATED": 0.90,
            "CORROBORATED": 0.75,
            "SUPPORTED": 0.50,
            "UNCONFIRMED": 0.20,
        }
        evidence_score = conf_map.get(anomaly_summary.confirmation.value, 0.50)

        # Calculate contributions
        f_event = Phase4RiskFactor(
            name="event_risk",
            score=event_risk_score,
            weight=self.weights.event_risk,
            contribution=round(event_risk_score * self.weights.event_risk, 4),
            description=f"Tactical severity of recent events ({event_risk_score:.2f})",
        )
        f_dev = Phase4RiskFactor(
            name="behavioral_deviation",
            score=behavioral_score,
            weight=self.weights.behavioral_deviation,
            contribution=round(behavioral_score * self.weights.behavioral_deviation, 4),
            description=f"Behavioral baseline drift ({behavioral_score:.2f})",
        )
        f_anom = Phase4RiskFactor(
            name="anomaly_score",
            score=anomaly_factor_score,
            weight=self.weights.anomaly_score,
            contribution=round(anomaly_factor_score * self.weights.anomaly_score, 4),
            description=f"Multi-dimensional anomaly evaluation ({anomaly_factor_score:.2f})",
        )
        f_cluster = Phase4RiskFactor(
            name="cluster_context",
            score=cluster_score,
            weight=self.weights.cluster_context,
            contribution=round(cluster_score * self.weights.cluster_context, 4),
            description=f"Operational cluster and formation correlation ({cluster_score:.2f})",
        )
        f_persist = Phase4RiskFactor(
            name="anomaly_persistence",
            score=persistence_score,
            weight=self.weights.anomaly_persistence,
            contribution=round(persistence_score * self.weights.anomaly_persistence, 4),
            description=f"Anomaly persistence profile ({anomaly_persistence.state.value})",
        )
        f_trend = Phase4RiskFactor(
            name="anomaly_trend",
            score=trend_score,
            weight=self.weights.anomaly_trend,
            contribution=round(trend_score * self.weights.anomaly_trend, 4),
            description=f"Anomaly trajectory direction ({anomaly_trend.direction.value})",
        )
        f_evidence = Phase4RiskFactor(
            name="evidence_quality",
            score=evidence_score,
            weight=self.weights.evidence_quality,
            contribution=round(evidence_score * self.weights.evidence_quality, 4),
            description=f"Corroboration level ({anomaly_summary.confirmation.value})",
        )

        factors = [f_event, f_dev, f_anom, f_cluster, f_persist, f_trend, f_evidence]
        raw_risk = sum(f.contribution for f in factors)
        final_risk = min(1.0, max(0.0, round(raw_risk, 4)))

        # Categorical Risk Level
        if final_risk < 0.25:
            level = RiskLevel.LOW
        elif final_risk < 0.50:
            level = RiskLevel.MEDIUM
        elif final_risk < 0.75:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.CRITICAL

        # Hysteresis-buffered Risk State
        state = self._determine_hysteresis_state(
            current_risk=final_risk,
            previous_state=previous_state,
        )

        # Risk Trend Direction
        if previous_risk is None:
            trend_dir = RiskTrendDirection.UNKNOWN
        else:
            delta = final_risk - previous_risk
            if delta > 0.05:
                trend_dir = RiskTrendDirection.RISING
            elif delta < -0.05:
                trend_dir = RiskTrendDirection.FALLING
            else:
                trend_dir = RiskTrendDirection.STABLE

        # Risk Persistence Profile
        hist = list(risk_history) if risk_history else []
        if not hist or hist[-1] != final_risk:
            hist.append(final_risk)

        elevated_wins = sum(1 for r in hist if r >= 0.30)
        consec_wins = 0
        for r in reversed(hist):
            if r >= 0.30:
                consec_wins += 1
            else:
                break

        peak = round(max(hist), 4)
        avg_r = round(sum(hist) / len(hist), 4)
        est_duration = round(consec_wins * 1.5, 1)  # 1.5 hours per evaluation window estimate

        risk_persistence = RiskPersistenceProfile(
            elevated_windows=elevated_wins,
            consecutive_windows=consec_wins,
            peak_score=peak,
            average_risk=avg_r,
            duration_hours=est_duration,
        )

        return Phase4RiskProfile(
            score=final_risk,
            level=level,
            state=state,
            trend=trend_dir,
            model_version="phase4-v1",
            factors=factors,
            persistence=risk_persistence,
        )

    def _determine_hysteresis_state(
        self,
        current_risk: float,
        previous_state: Optional[RiskState] = None,
    ) -> RiskState:
        """
        Applies hysteresis buffer to prevent rapid boundary oscillation.
        Thresholds:
        NORMAL -> ELEVATED: 0.30
        ELEVATED -> HIGH: 0.60
        HIGH -> CRITICAL: 0.80
        """
        buf = self.hysteresis.buffer  # 0.03

        if previous_state is None or previous_state == RiskState.UNKNOWN:
            # Baseline entry
            if current_risk >= 0.80:
                return RiskState.CRITICAL
            elif current_risk >= 0.60:
                return RiskState.HIGH
            elif current_risk >= 0.30:
                return RiskState.ELEVATED
            else:
                return RiskState.NORMAL

        # State transition with hysteresis buffer
        if previous_state == RiskState.NORMAL:
            if current_risk >= (0.30 + buf):
                return RiskState.ELEVATED
            return RiskState.NORMAL

        elif previous_state == RiskState.ELEVATED:
            if current_risk >= (0.60 + buf):
                return RiskState.HIGH
            elif current_risk < (0.30 - buf):
                return RiskState.NORMAL
            return RiskState.ELEVATED

        elif previous_state == RiskState.HIGH:
            if current_risk >= (0.80 + buf):
                return RiskState.CRITICAL
            elif current_risk < (0.60 - buf):
                return RiskState.ELEVATED
            return RiskState.HIGH

        elif previous_state == RiskState.CRITICAL:
            if current_risk < (0.80 - buf):
                return RiskState.HIGH
            return RiskState.CRITICAL

        return RiskState.NORMAL
