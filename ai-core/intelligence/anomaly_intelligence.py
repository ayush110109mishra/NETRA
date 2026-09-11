"""
Master Anomaly Intelligence Orchestrator for NETRA (Phase 4).
Coordinates multi-dimensional anomaly assessment, attribution, persistence,
phase4-v1 risk modeling, sector heat indexing, hotspot clustering, and synthetic scenario execution.
"""

import time
import hashlib
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any

from config import NetraConfig, default_config
from models.common import Coordinates
from models.event_intelligence import CanonicalEvent, EventSource
from models.entity_intelligence import (
    CanonicalEntity,
    FourTierAssessment,
)
from models.anomaly_intelligence import (
    AnomalyAnalyzeRequest,
    AnomalyAnalyzeResponse,
    AnomalySummary,
    AnomalyHistoryItem,
    AnomalyHistoryResponse,
    SectorAnomalyHeatIndex,
    AnomalyHotspot,
)
from models.risk_intelligence import (
    RiskHistoryItem,
    RiskHistoryResponse,
)

from entities.repository import EntityRepository
from entities.baseline import BehavioralBaselineEngine
from anomaly.engine import AnomalyEngine
from risk.aggregation import Phase4RiskAggregator
from risk.propagation import RiskPropagator
from risk.trend import RiskTrendAnalyzer


class AnomalyIntelligenceEngine:
    """Master orchestrator for Phase 4 Anomaly & Risk Intelligence."""

    def __init__(
        self,
        config: Optional[NetraConfig] = None,
        repository: Optional[EntityRepository] = None,
    ):
        self.cfg = config or default_config
        self.repository = repository or EntityRepository(self.cfg.entity)
        self.baseline_engine = BehavioralBaselineEngine(self.cfg.entity)
        self.anomaly_engine = AnomalyEngine(self.cfg)
        self.risk_aggregator = Phase4RiskAggregator(
            weights=self.cfg.phase4_risk_weights,
            hysteresis=self.cfg.hysteresis,
        )
        self.risk_propagator = RiskPropagator()
        self.risk_trend_analyzer = RiskTrendAnalyzer()

    def analyze_entity_anomaly(
        self,
        request: AnomalyAnalyzeRequest,
    ) -> AnomalyAnalyzeResponse:
        """
        Execute full Phase 4 Anomaly & Risk assessment for the requested entity.
        Deterministic, evidence-based, and explainable.
        """
        start_time = time.perf_counter()
        now_utc = request.as_of or datetime.now(timezone.utc)
        entity_id = request.entity_id

        # 1. Retrieve or construct entity
        entity = self.repository.get_entity(entity_id, as_of=now_utc)
        historical_events = self.repository.get_events_for_entity(entity_id)

        # Parse request events if provided
        request_events: List[CanonicalEvent] = []
        if request.events:
            for ev_dict in request.events:
                if isinstance(ev_dict, CanonicalEvent):
                    request_events.append(ev_dict)
                elif isinstance(ev_dict, dict):
                    request_events.append(self._dict_to_canonical_event(ev_dict))

        # Combined event pool
        if request_events:
            all_events = sorted(historical_events + request_events, key=lambda x: x.timestamp)
            current_eval_events = request_events
        else:
            all_events = sorted(historical_events, key=lambda x: x.timestamp)
            recent_hours = self.cfg.entity.recent_analysis_window_hours
            if all_events:
                latest_ts = all_events[-1].timestamp
                current_eval_events = [
                    e for e in all_events
                    if (latest_ts - e.timestamp).total_seconds() <= recent_hours * 3600.0
                ]
                if not current_eval_events:
                    current_eval_events = [all_events[-1]]
            else:
                current_eval_events = []

        if not entity:
            # Construct transient entity representation if not in repo
            first_obs = all_events[0].timestamp if all_events else now_utc
            last_obs = all_events[-1].timestamp if all_events else now_utc
            entity = CanonicalEntity(
                entity_id=entity_id,
                entity_type="UNKNOWN",
                first_observed=first_obs,
                last_observed=last_obs,
                observation_count=len(all_events),
                associated_entity_ids=[],
                attributes={},
            )

        # 2. Compute behavioral baseline
        # Baseline is built on historical events prior to the current evaluation window
        baseline_events = [e for e in all_events if e not in current_eval_events]
        if not baseline_events and all_events:
            baseline_events = all_events
        baseline = self.baseline_engine.compute_baseline(entity, baseline_events)

        # 3. Multi-dimensional anomaly evaluation
        (
            anomaly_summary,
            multi_dim,
            dim_details,
            attribution,
            trend,
            persistence,
            conf_bundle,
            evidence,
        ) = self.anomaly_engine.evaluate_entity_anomaly(
            entity=entity,
            events=current_eval_events,
            baseline=baseline,
            context=request.context,
        )

        # 4. Phase 4 Explainable Risk Modeling (phase4-v1)
        risk_profile = self.risk_aggregator.compute_risk(
            entity=entity,
            events=current_eval_events,
            anomaly_summary=anomaly_summary,
            anomaly_trend=trend,
            anomaly_persistence=persistence,
            baseline=baseline,
            context=request.context,
        )

        # 5. Four-Tier Intelligence Assessment
        assessment = self._generate_four_tier_assessment(
            entity=entity,
            summary=anomaly_summary,
            multi_dim=multi_dim,
            attribution=attribution,
            risk_profile=risk_profile,
            current_events=current_eval_events,
        )

        # Generate deterministic analysis identifier
        hash_seed = f"{entity_id}:{now_utc.isoformat()}:{anomaly_summary.score:.4f}:{risk_profile.score:.4f}"
        analysis_id = "ANOM-" + hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()[:12].upper()

        exec_duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return AnomalyAnalyzeResponse(
            analysis_id=analysis_id,
            entity_id=entity_id,
            timestamp=now_utc,
            anomaly=anomaly_summary,
            dimensions=multi_dim,
            dimension_details=dim_details,
            attribution=attribution,
            trend=trend,
            persistence=persistence,
            risk=risk_profile,
            confidence=conf_bundle,
            assessment=assessment,
            evidence=evidence,
            metadata={
                "processing_duration_ms": exec_duration_ms,
                "model_version": "phase4-v1",
                "ruleset_version": "4.0.0",
                "evaluation_events_count": len(current_eval_events),
                "baseline_samples_count": baseline.sample_count,
            },
        )

    def get_entity_anomalies_history(
        self,
        entity_id: str,
        limit: int = 50,
    ) -> AnomalyHistoryResponse:
        """
        Retrieve chronological point-in-time anomaly records for an entity.
        """
        entity = self.repository.get_entity(entity_id)
        if not entity:
            raise ValueError(f"Entity '{entity_id}' not found.")

        events = sorted(self.repository.get_events_for_entity(entity_id), key=lambda x: x.timestamp)
        if not events:
            return AnomalyHistoryResponse(
                entity_id=entity_id,
                anomalies=[],
                metadata={"total_records": 0},
            )

        # Build chronological sliding windows
        history_items: List[AnomalyHistoryItem] = []
        step_size = max(1, len(events) // min(limit, 10))

        for i in range(1, len(events) + 1, step_size):
            window_events = events[:i]
            eval_events = window_events[-3:] if len(window_events) >= 3 else window_events
            base_events = window_events[:-3] if len(window_events) > 3 else window_events
            baseline = self.baseline_engine.compute_baseline(entity, base_events)

            summary, _, dim_details, attribution, _, _, _, _ = self.anomaly_engine.evaluate_entity_anomaly(
                entity=entity,
                events=eval_events,
                baseline=baseline,
            )

            history_items.append(
                AnomalyHistoryItem(
                    timestamp=window_events[-1].timestamp,
                    score=summary.score,
                    level=summary.level,
                    primary_dimension=attribution.primary_dimension,
                    status=summary.lifecycle.value,
                    evidence_event_ids=[e.event_id for e in eval_events],
                )
            )

        if len(history_items) > limit:
            history_items = history_items[-limit:]

        return AnomalyHistoryResponse(
            entity_id=entity_id,
            anomalies=history_items,
            metadata={"total_records": len(history_items)},
        )

    def get_entity_risk_history(
        self,
        entity_id: str,
        limit: int = 50,
    ) -> RiskHistoryResponse:
        """
        Retrieve chronological point-in-time risk trajectory for an entity.
        """
        entity = self.repository.get_entity(entity_id)
        if not entity:
            raise ValueError(f"Entity '{entity_id}' not found.")

        events = sorted(self.repository.get_events_for_entity(entity_id), key=lambda x: x.timestamp)
        if not events:
            return RiskHistoryResponse(
                entity_id=entity_id,
                history=[],
                metadata={"total_records": 0},
            )

        history_items: List[RiskHistoryItem] = []
        step_size = max(1, len(events) // min(limit, 10))

        for i in range(1, len(events) + 1, step_size):
            window_events = events[:i]
            eval_events = window_events[-3:] if len(window_events) >= 3 else window_events
            base_events = window_events[:-3] if len(window_events) > 3 else window_events
            baseline = self.baseline_engine.compute_baseline(entity, base_events)

            summary, _, _, _, trend, persistence, conf, _ = self.anomaly_engine.evaluate_entity_anomaly(
                entity=entity,
                events=eval_events,
                baseline=baseline,
            )

            risk_profile = self.risk_aggregator.compute_risk(
                entity=entity,
                events=eval_events,
                anomaly_summary=summary,
                anomaly_trend=trend,
                anomaly_persistence=persistence,
                baseline=baseline,
            )

            history_items.append(
                RiskHistoryItem(
                    timestamp=window_events[-1].timestamp,
                    risk=risk_profile.score,
                    anomaly=summary.score,
                    confidence=conf.get("calibrated_confidence", 0.75),
                    state=risk_profile.state,
                )
            )

        if len(history_items) > limit:
            history_items = history_items[-limit:]

        return RiskHistoryResponse(
            entity_id=entity_id,
            history=history_items,
            metadata={"total_records": len(history_items)},
        )

    def get_sector_anomaly_index(
        self,
        sector_id: str,
    ) -> SectorAnomalyHeatIndex:
        """
        Calculates aggregate anomaly heat index for an operational sector.
        """
        all_entities = self.repository.list_entities()
        sector_entities = []
        for ent in all_entities:
            ent_sector = ent.attributes.get("sector") or ent.attributes.get("registered_sector")
            if ent_sector == sector_id:
                sector_entities.append(ent)

        if not sector_entities:
            # Check events with this sector
            all_events = self.repository.get_all_events()
            matching_ids = {
                e.entity_id for e in all_events
                if e.attributes.get("sector") == sector_id or e.attributes.get("sector_id") == sector_id
            }
            sector_entities = [e for e in all_entities if e.entity_id in matching_ids]

        if not sector_entities:
            return SectorAnomalyHeatIndex(
                sector_id=sector_id,
                anomaly_index=0.05,
                entity_count=0,
                high_anomaly_entities=0,
                confidence=0.50,
                metadata={"status": "NO_ENTITIES_IN_SECTOR"},
            )

        entity_scores: List[float] = []
        high_count = 0

        for ent in sector_entities:
            events = self.repository.get_events_for_entity(ent.entity_id)
            if events:
                baseline = self.baseline_engine.compute_baseline(ent, events)
                summary, _, _, _, _, _, _, _ = self.anomaly_engine.evaluate_entity_anomaly(
                    entity=ent,
                    events=events[-5:],
                    baseline=baseline,
                )
                score = summary.score
            else:
                score = 0.05

            entity_scores.append(score)
            if score >= 0.70:
                high_count += 1

        avg_score = round(sum(entity_scores) / len(entity_scores), 4)
        # Weight sector heat by proportion of high-anomaly entities
        heat_index = min(1.0, round(avg_score * 0.70 + (high_count / len(sector_entities)) * 0.30, 4))
        confidence = round(min(0.95, 0.50 + (len(sector_entities) * 0.08)), 2)

        return SectorAnomalyHeatIndex(
            sector_id=sector_id,
            anomaly_index=heat_index,
            entity_count=len(sector_entities),
            high_anomaly_entities=high_count,
            confidence=confidence,
            metadata={"evaluated_entities": [e.entity_id for e in sector_entities]},
        )

    def get_anomaly_hotspots(
        self,
        min_score: float = 0.50,
    ) -> List[AnomalyHotspot]:
        """
        Geospatially clusters anomalous events and entities into actionable operational hotspots.
        """
        all_entities = self.repository.list_entities()
        anomalous_points: List[Dict[str, Any]] = []

        for ent in all_entities:
            events = self.repository.get_events_for_entity(ent.entity_id)
            if not events:
                continue
            baseline = self.baseline_engine.compute_baseline(ent, events)
            summary, multi_dim, _, attribution, _, _, conf, _ = self.anomaly_engine.evaluate_entity_anomaly(
                entity=ent,
                events=events[-5:],
                baseline=baseline,
            )
            if summary.score >= min_score:
                last_ev = events[-1]
                anomalous_points.append({
                    "entity_id": ent.entity_id,
                    "score": summary.score,
                    "confidence": conf.get("calibrated_confidence", 0.75),
                    "coordinates": last_ev.coordinates,
                    "primary_dimension": attribution.primary_dimension,
                    "event": last_ev,
                })

        if not anomalous_points:
            return []

        # Simple deterministic spatial grouping (distance threshold ~ 50 km)
        from models.geo import haversine_distance_km
        clusters: List[List[Dict[str, Any]]] = []

        for pt in anomalous_points:
            assigned = False
            for c in clusters:
                dist = haversine_distance_km(c[0]["coordinates"], pt["coordinates"])
                if dist <= 50.0:
                    c.append(pt)
                    assigned = True
                    break
            if not assigned:
                clusters.append([pt])

        hotspots: List[AnomalyHotspot] = []
        for cluster in clusters:
            lats = [p["coordinates"].latitude for p in cluster]
            lons = [p["coordinates"].longitude for p in cluster]
            centroid = Coordinates(
                latitude=round(sum(lats) / len(lats), 6),
                longitude=round(sum(lons) / len(lons), 6),
            )

            # Radius km
            radius_km = max(
                [haversine_distance_km(centroid, p["coordinates"]) for p in cluster]
            )
            radius_km = max(5.0, round(radius_km, 2))

            mean_score = round(sum(p["score"] for p in cluster) / len(cluster), 4)
            mean_conf = round(sum(p["confidence"] for p in cluster) / len(cluster), 4)
            dims = list(dict.fromkeys([p["primary_dimension"] for p in cluster]))

            hotspots.append(
                AnomalyHotspot(
                    centroid=centroid,
                    radius_km=radius_km,
                    event_count=len(cluster),
                    anomaly_index=mean_score,
                    confidence=mean_conf,
                    primary_dimensions=dims,
                )
            )

        hotspots.sort(key=lambda x: x.anomaly_index, reverse=True)
        return hotspots

    def _generate_four_tier_assessment(
        self,
        entity: CanonicalEntity,
        summary: AnomalySummary,
        multi_dim: Any,
        attribution: Any,
        risk_profile: Any,
        current_events: List[CanonicalEvent],
    ) -> FourTierAssessment:
        """Constructs an explainable four-tier intelligence assessment."""
        # Tier 1: Operational Summary
        op_summary = (
            f"Entity {entity.entity_id} ({entity.entity_type}) exhibits {summary.level.value} "
            f"anomaly intensity (score: {summary.score:.2f}) in persistence state {summary.state.value}. "
            f"Primary operational driver is {attribution.primary_dimension.upper()}. "
            f"Phase 4 analytical risk is evaluated as {risk_profile.level.value} (score: {risk_profile.score:.2f}, "
            f"state: {risk_profile.state.value})."
        )

        # Tier 2: Observed Facts
        facts = [
            f"Total evaluation events: {len(current_events)}",
            f"Observed persistence state: {summary.state.value}",
            f"Evidence confirmation level: {summary.confirmation.value}",
            f"Primary anomalous dimension: {attribution.primary_dimension}",
        ]
        for tf in attribution.top_factors[:3]:
            facts.append(f"Dimension '{tf.factor}': raw score {tf.score:.2f}, contribution {tf.contribution:.3f}")

        # Tier 3: Analytical Inferences
        inferences = [
            f"Deviation pattern indicates {summary.state.value.lower()} operational behavior rather than random sensor jitter.",
            f"Attribution indicates primary analytical concern stems from {attribution.primary_dimension.lower()} metrics.",
            f"Risk state machine registers {risk_profile.state.value} posture under hysteresis buffer control.",
        ]
        if summary.score >= 0.70:
            inferences.append("High multi-dimensional deviation warrants elevated monitoring and sensor tasking.")
        else:
            inferences.append("Entity behavior remains within tolerable operational divergence parameters.")

        # Tier 4: Predictions & Projections
        predictions = []
        if summary.state.value == "ESCALATING":
            predictions.append("Trajectory projects potential operational boundary breach in upcoming observation cycles.")
        elif summary.state.value == "DECLINING":
            predictions.append("Projected regression to nominal baseline within next evaluation window.")
        else:
            predictions.append("Behavior projected to maintain current state under standard conditions.")

        # Operational Caveats / Uncertainties
        uncertainties = [
            f"Assessment confirmation level: {summary.confirmation.value}.",
            "All findings are analytical models over synthetic operational data; not for direct kinetic tasking.",
        ]

        return FourTierAssessment(
            summary=op_summary,
            observed=facts,
            inferred=inferences,
            predicted=predictions,
            uncertain=uncertainties,
        )

    def _dict_to_canonical_event(self, d: Dict[str, Any]) -> CanonicalEvent:
        """Converts raw dictionary into CanonicalEvent."""
        coords = d.get("location") or d.get("coordinates")
        if isinstance(coords, dict):
            coords_obj = Coordinates(
                latitude=coords["latitude"],
                longitude=coords["longitude"],
                altitude_m=coords.get("altitude_m"),
                sector_id=coords.get("sector_id"),
            )
        elif isinstance(coords, Coordinates):
            coords_obj = coords
        else:
            coords_obj = Coordinates(latitude=0.0, longitude=0.0)

        ts = d.get("timestamp")
        if isinstance(ts, str):
            ts_obj = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        elif isinstance(ts, datetime):
            ts_obj = ts
        else:
            ts_obj = datetime.now(timezone.utc)

        src = d.get("source")
        if isinstance(src, dict):
            src_obj = EventSource(
                source_id=src.get("source_id", "SRC-GEN"),
                source_type=src.get("source_type", "OSINT"),
                reliability=src.get("reliability", 0.80),
            )
        elif isinstance(src, EventSource):
            src_obj = src
        else:
            src_obj = EventSource(source_id="SRC-GEN", source_type="RADAR", reliability=0.85)

        ent_ids = d.get("entity_ids")
        if not ent_ids:
            ent_id = d.get("entity_id", "UNKNOWN")
            ent_ids = [ent_id]

        return CanonicalEvent(
            event_id=d.get("event_id", f"EVT-{hashlib.sha256(str(ts_obj).encode()).hexdigest()[:8]}"),
            event_type=d.get("event_type", "PATROL"),
            timestamp=ts_obj,
            location=coords_obj,
            source=src_obj,
            entity_ids=ent_ids,
            attributes=d.get("attributes", {}),
        )
