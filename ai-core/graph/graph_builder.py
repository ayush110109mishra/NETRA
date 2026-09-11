"""
Phase 8 Knowledge Graph Builder for NETRA.
Bridges Phase 1-7 analytical outputs into a unified, evidence-grounded knowledge graph.
Guarantees determinism, idempotency, and reference integrity.
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set
from models.knowledge_graph import EdgeType, GraphEdge, GraphNode, NodeType, ProvenanceItem
from models.predictive_intelligence import EpistemicStatus
from graph.node_registry import NodeRegistry, generate_node_id
from graph.edge_registry import EdgeRegistry


class KnowledgeGraphBuilder:
    """
    Constructs and updates the NETRA knowledge graph by ingesting outputs
    from Events (P1), Correlations (P2), Entities (P3), Anomalies & Risk (P4),
    Fusion (P5), Forecasting (P6), and Evidence (P7).
    """

    def __init__(self, node_registry: NodeRegistry, edge_registry: EdgeRegistry) -> None:
        self.node_registry = node_registry
        self.edge_registry = edge_registry

    def ingest_entity(
        self,
        entity_id: str,
        entity_type: str = "PLATFORM",
        label: Optional[str] = None,
        allegiance: str = "UNKNOWN",
        status: str = "ACTIVE",
        first_observed: Optional[datetime] = None,
        last_observed: Optional[datetime] = None,
        observation_count: int = 1,
        event_count: int = 1,
        attributes: Optional[Dict[str, Any]] = None,
        provenance: Optional[List[ProvenanceItem]] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        sector_id: Optional[str] = None,
        associated_entity_ids: Optional[List[str]] = None,
    ) -> GraphNode:
        """Ingests an entity and creates ASSOCIATED_WITH edges if associated entities are listed."""
        now = datetime.now(timezone.utc)
        first_obs = first_observed or now
        last_obs = last_observed or now

        attrs = attributes or {}
        attrs.update({
            "entity_type": entity_type,
            "allegiance": allegiance,
            "status": status,
            "observation_count": observation_count,
            "event_count": event_count,
        })

        node = self.node_registry.add_node(
            node_type=NodeType.ENTITY,
            label=label or entity_id,
            canonical_reference=entity_id,
            created_at=first_obs,
            valid_from=first_obs,
            valid_to=None,  # Persistent unless explicitly expired
            confidence=1.0,
            epistemic_status=EpistemicStatus.OBSERVED,
            attributes=attrs,
            provenance=provenance or [],
            latitude=latitude,
            longitude=longitude,
            sector_id=sector_id,
        )

        # Ingest sector node if sector_id is given
        if sector_id:
            sec_node = self.node_registry.add_node(
                node_type=NodeType.SECTOR,
                label=sector_id,
                canonical_reference=sector_id,
                created_at=first_obs,
                epistemic_status=EpistemicStatus.OBSERVED,
            )
            self.edge_registry.add_edge(
                source_node_id=node.node_id,
                target_node_id=sec_node.node_id,
                edge_type=EdgeType.LOCATED_IN,
                confidence=1.0,
                is_directional=True,
            )

        # Ingest associated entities
        if associated_entity_ids:
            for assoc_id in associated_entity_ids:
                if not assoc_id or assoc_id == entity_id:
                    continue
                # Ensure partner entity node exists
                partner_node = self.node_registry.get_node_by_reference(assoc_id)
                if not partner_node:
                    partner_node = self.node_registry.add_node(
                        node_type=NodeType.ENTITY,
                        label=assoc_id,
                        canonical_reference=assoc_id,
                        created_at=first_obs,
                        valid_from=first_obs,
                        epistemic_status=EpistemicStatus.INFERRED,
                    )
                self.edge_registry.add_edge(
                    source_node_id=node.node_id,
                    target_node_id=partner_node.node_id,
                    edge_type=EdgeType.ASSOCIATED_WITH,
                    strength=0.75,
                    confidence=0.85,
                    epistemic_status=EpistemicStatus.INFERRED,
                    first_observed_at=first_obs,
                    last_observed_at=last_obs,
                    is_directional=False,
                )

        return node

    def ingest_event(
        self,
        event_id: str,
        event_type: str,
        description: str,
        timestamp: datetime,
        entity_id: Optional[str] = None,
        priority_hint: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        sector_id: Optional[str] = None,
        provenance: Optional[List[ProvenanceItem]] = None,
    ) -> GraphNode:
        """Ingests an operational event and connects to its parent entity and sector."""
        attrs = {
            "event_type": event_type,
            "description": description,
            "priority_hint": priority_hint,
        }
        event_node = self.node_registry.add_node(
            node_type=NodeType.EVENT,
            label=f"{event_type}: {event_id}",
            canonical_reference=event_id,
            created_at=timestamp,
            valid_from=timestamp,
            valid_to=timestamp + timedelta(hours=6),
            confidence=1.0,
            epistemic_status=EpistemicStatus.OBSERVED,
            attributes=attrs,
            provenance=provenance or [],
            latitude=latitude,
            longitude=longitude,
            sector_id=sector_id,
        )

        if entity_id:
            # Ensure entity node exists
            ent_node = self.node_registry.get_node_by_reference(entity_id)
            if not ent_node:
                ent_node = self.ingest_entity(entity_id=entity_id, first_observed=timestamp, last_observed=timestamp)
            # Edge: Entity GENERATED Event
            self.edge_registry.add_edge(
                source_node_id=ent_node.node_id,
                target_node_id=event_node.node_id,
                edge_type=EdgeType.GENERATED,
                confidence=1.0,
                first_observed_at=timestamp,
                last_observed_at=timestamp,
                is_directional=True,
            )

        if sector_id:
            sec_node = self.node_registry.add_node(
                node_type=NodeType.SECTOR,
                label=sector_id,
                canonical_reference=sector_id,
                created_at=timestamp,
                epistemic_status=EpistemicStatus.OBSERVED,
            )
            self.edge_registry.add_edge(
                source_node_id=event_node.node_id,
                target_node_id=sec_node.node_id,
                edge_type=EdgeType.LOCATED_IN,
                confidence=1.0,
                is_directional=True,
            )

        return event_node

    def ingest_correlation(
        self,
        event_id_a: str,
        event_id_b: str,
        correlation_score: float,
        correlation_type: str = "TEMPORAL_SPATIAL",
        evidence_ids: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None,
    ) -> Optional[GraphEdge]:
        """Creates a CORRELATED_WITH edge between two events."""
        node_a = self.node_registry.get_node_by_reference(event_id_a)
        node_b = self.node_registry.get_node_by_reference(event_id_b)
        if not node_a or not node_b:
            return None

        now = timestamp or datetime.now(timezone.utc)
        return self.edge_registry.add_edge(
            source_node_id=node_a.node_id,
            target_node_id=node_b.node_id,
            edge_type=EdgeType.CORRELATED_WITH,
            strength=max(0.0, min(1.0, correlation_score)),
            confidence=0.90,
            epistemic_status=EpistemicStatus.INFERRED,
            first_observed_at=now,
            last_observed_at=now,
            evidence_ids=evidence_ids or [event_id_a, event_id_b],
            attributes={"correlation_type": correlation_type},
            is_directional=False,
        )

    def ingest_cluster(
        self,
        cluster_id: str,
        member_event_ids: List[str],
        member_entity_ids: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None,
    ) -> GraphNode:
        """Ingests an activity CLUSTER node and links members."""
        now = timestamp or datetime.now(timezone.utc)
        cluster_node = self.node_registry.add_node(
            node_type=NodeType.CLUSTER,
            label=f"Cluster {cluster_id}",
            canonical_reference=cluster_id,
            created_at=now,
            epistemic_status=EpistemicStatus.INFERRED,
            attributes={"event_count": len(member_event_ids)},
        )

        for eid in member_event_ids:
            ev_node = self.node_registry.get_node_by_reference(eid)
            if ev_node:
                self.edge_registry.add_edge(
                    source_node_id=ev_node.node_id,
                    target_node_id=cluster_node.node_id,
                    edge_type=EdgeType.PART_OF_CLUSTER,
                    confidence=1.0,
                    is_directional=True,
                )

        if member_entity_ids:
            for ent_id in member_entity_ids:
                ent_node = self.node_registry.get_node_by_reference(ent_id)
                if not ent_node:
                    ent_node = self.ingest_entity(entity_id=ent_id, first_observed=now, last_observed=now)
                self.edge_registry.add_edge(
                    source_node_id=ent_node.node_id,
                    target_node_id=cluster_node.node_id,
                    edge_type=EdgeType.MEMBER_OF,
                    confidence=1.0,
                    is_directional=True,
                )

        return cluster_node

    def ingest_anomaly(
        self,
        anomaly_id: str,
        entity_id: str,
        anomaly_score: float,
        dimensions: Optional[Dict[str, float]] = None,
        timestamp: Optional[datetime] = None,
        evidence_ids: Optional[List[str]] = None,
    ) -> GraphNode:
        """Ingests an ANOMALY node and links Entity HAS_ANOMALY."""
        now = timestamp or datetime.now(timezone.utc)
        ent_node = self.node_registry.get_node_by_reference(entity_id)
        if not ent_node:
            ent_node = self.ingest_entity(entity_id=entity_id, first_observed=now, last_observed=now)

        anom_node = self.node_registry.add_node(
            node_type=NodeType.ANOMALY,
            label=f"Anomaly: {anomaly_id}",
            canonical_reference=anomaly_id,
            created_at=now,
            confidence=0.92,
            epistemic_status=EpistemicStatus.INFERRED,
            attributes={"score": anomaly_score, "dimensions": dimensions or {}},
        )

        self.edge_registry.add_edge(
            source_node_id=ent_node.node_id,
            target_node_id=anom_node.node_id,
            edge_type=EdgeType.HAS_ANOMALY,
            strength=anomaly_score,
            confidence=0.92,
            epistemic_status=EpistemicStatus.INFERRED,
            first_observed_at=now,
            last_observed_at=now,
            evidence_ids=evidence_ids or [anomaly_id],
            is_directional=True,
        )

        return anom_node

    def ingest_risk(
        self,
        risk_id: str,
        entity_id: str,
        risk_score: float,
        risk_level: str = "MEDIUM",
        timestamp: Optional[datetime] = None,
        contributing_anomaly_id: Optional[str] = None,
    ) -> GraphNode:
        """Ingests a RISK node and links Entity HAS_RISK."""
        now = timestamp or datetime.now(timezone.utc)
        ent_node = self.node_registry.get_node_by_reference(entity_id)
        if not ent_node:
            ent_node = self.ingest_entity(entity_id=entity_id, first_observed=now, last_observed=now)

        risk_node = self.node_registry.add_node(
            node_type=NodeType.RISK,
            label=f"Risk: {risk_level} ({risk_score:.2f})",
            canonical_reference=risk_id,
            created_at=now,
            epistemic_status=EpistemicStatus.INFERRED,
            attributes={"score": risk_score, "level": risk_level},
        )

        self.edge_registry.add_edge(
            source_node_id=ent_node.node_id,
            target_node_id=risk_node.node_id,
            edge_type=EdgeType.HAS_RISK,
            strength=risk_score,
            confidence=0.90,
            epistemic_status=EpistemicStatus.INFERRED,
            first_observed_at=now,
            last_observed_at=now,
            is_directional=True,
        )

        if contributing_anomaly_id:
            anom_node = self.node_registry.get_node_by_reference(contributing_anomaly_id)
            if anom_node:
                self.edge_registry.add_edge(
                    source_node_id=anom_node.node_id,
                    target_node_id=risk_node.node_id,
                    edge_type=EdgeType.CONTRIBUTES_TO,
                    strength=0.85,
                    is_directional=True,
                )

        return risk_node

    def ingest_fusion(
        self,
        fusion_id: str,
        entity_id: str,
        source_ids: List[str],
        raw_observation_ids: List[str],
        timestamp: Optional[datetime] = None,
        conflicting_sources: Optional[List[str]] = None,
    ) -> GraphNode:
        """Ingests a FUSED_OBSERVATION and links SOURCE, OBSERVATION, and ENTITY."""
        now = timestamp or datetime.now(timezone.utc)
        fused_node = self.node_registry.add_node(
            node_type=NodeType.FUSED_OBSERVATION,
            label=f"Fused: {fusion_id}",
            canonical_reference=fusion_id,
            created_at=now,
            epistemic_status=EpistemicStatus.FUSED,
            attributes={"source_count": len(source_ids)},
        )

        ent_node = self.node_registry.get_node_by_reference(entity_id)
        if not ent_node:
            ent_node = self.ingest_entity(entity_id=entity_id, first_observed=now, last_observed=now)

        self.edge_registry.add_edge(
            source_node_id=fused_node.node_id,
            target_node_id=ent_node.node_id,
            edge_type=EdgeType.RESOLVED_AS,
            confidence=0.95,
            epistemic_status=EpistemicStatus.FUSED,
            evidence_ids=raw_observation_ids,
            is_directional=True,
        )

        for src_id in source_ids:
            src_node = self.node_registry.add_node(
                node_type=NodeType.SOURCE,
                label=f"Source {src_id}",
                canonical_reference=src_id,
                created_at=now,
                epistemic_status=EpistemicStatus.OBSERVED,
            )
            self.edge_registry.add_edge(
                source_node_id=src_node.node_id,
                target_node_id=fused_node.node_id,
                edge_type=EdgeType.SUPPORTS,
                confidence=0.90,
                epistemic_status=EpistemicStatus.OBSERVED,
                is_directional=True,
            )

        if conflicting_sources:
            for c_src in conflicting_sources:
                c_node = self.node_registry.add_node(
                    node_type=NodeType.SOURCE,
                    label=f"Source {c_src}",
                    canonical_reference=c_src,
                    created_at=now,
                    epistemic_status=EpistemicStatus.OBSERVED,
                )
                self.edge_registry.add_edge(
                    source_node_id=c_node.node_id,
                    target_node_id=fused_node.node_id,
                    edge_type=EdgeType.CONTRADICTS,
                    confidence=0.80,
                    epistemic_status=EpistemicStatus.UNCERTAIN,
                    contradicting_evidence_ids=[f"CONFLICT-{c_src}"],
                    is_directional=True,
                )

        return fused_node

    def ingest_forecast(
        self,
        forecast_id: str,
        entity_id: str,
        horizon: str,
        probability: float,
        predicted_state: str,
        supporting_evidence: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None,
    ) -> GraphNode:
        """Ingests a FORECAST node and links Entity HAS_FORECAST and PREDICTS."""
        now = timestamp or datetime.now(timezone.utc)
        ent_node = self.node_registry.get_node_by_reference(entity_id)
        if not ent_node:
            ent_node = self.ingest_entity(entity_id=entity_id, first_observed=now, last_observed=now)

        forecast_node = self.node_registry.add_node(
            node_type=NodeType.FORECAST,
            label=f"Forecast {horizon}: {predicted_state}",
            canonical_reference=forecast_id,
            created_at=now,
            confidence=probability,
            epistemic_status=EpistemicStatus.PREDICTED,
            attributes={"horizon": horizon, "state": predicted_state, "probability": probability},
        )

        self.edge_registry.add_edge(
            source_node_id=ent_node.node_id,
            target_node_id=forecast_node.node_id,
            edge_type=EdgeType.HAS_FORECAST,
            strength=probability,
            confidence=probability,
            epistemic_status=EpistemicStatus.PREDICTED,
            evidence_ids=supporting_evidence or [],
            is_directional=True,
        )

        self.edge_registry.add_edge(
            source_node_id=forecast_node.node_id,
            target_node_id=ent_node.node_id,
            edge_type=EdgeType.PREDICTS,
            strength=probability,
            confidence=probability,
            epistemic_status=EpistemicStatus.PREDICTED,
            evidence_ids=supporting_evidence or [],
            is_directional=True,
        )

        return forecast_node
