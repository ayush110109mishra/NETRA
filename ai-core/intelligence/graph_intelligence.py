"""
Phase 8 Master Graph Intelligence Engine for NETRA.
ASTRAVEDA Defence Intelligence Platform - ATUL AI/ML Engineering.

Coordinates the knowledge graph pipeline between Phase 1-7 domain engines and Phase 8 graph queries.
Maintains thin REST controllers and guarantees grounded 5-tier epistemic assessments.
"""

from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, List, Optional
from config import NetraConfig, default_config
from entities.repository import EntityRepository
from graph.graph_engine import KnowledgeGraphEngine
from models.knowledge_graph import (
    CentralityResult,
    CommunityResult,
    EntityNetworkResponse,
    GraphAnalyzeRequest,
    GraphAnalyzeResponse,
    GraphChangesResponse,
    GraphEdge,
    GraphNode,
    GraphSnapshotResponse,
    NodeType,
    PathResult,
    RelationshipChange,
    RelationshipDetail,
)


class GraphIntelligenceEngine:
    """
    Orchestrates ingestion from Phase 1-7 domain repositories into the Knowledge Graph Engine,
    executes graph intelligence analyses, and builds frontend-ready responses.
    """

    def __init__(
        self,
        config: Optional[NetraConfig] = None,
        repository: Optional[EntityRepository] = None,
        graph_engine: Optional[KnowledgeGraphEngine] = None,
    ) -> None:
        self.config = config or default_config
        self.repository = repository
        self.graph_engine = graph_engine or KnowledgeGraphEngine(self.config)

        # Seed initial graph from entity repository if available
        if self.repository:
            self._seed_from_repository()

    def _seed_from_repository(self) -> None:
        """Populates the graph with all canonical entities and relationships currently in repository."""
        if not self.repository or self.graph_engine.node_registry.count() > 0:
            return

        entities = self.repository.list_entities()
        for ent in entities:
            # Spatial coordinates if available
            lat, lon, sec = None, None, None
            if hasattr(ent, "attributes") and isinstance(ent.attributes, dict):
                loc = ent.attributes.get("location")
                if loc and isinstance(loc, dict):
                    lat = loc.get("latitude")
                    lon = loc.get("longitude")
                    sec = loc.get("sector_id")

            self.graph_engine.builder.ingest_entity(
                entity_id=ent.entity_id,
                entity_type=ent.entity_type,
                label=ent.callsign or ent.entity_id,
                allegiance=ent.allegiance.value if hasattr(ent.allegiance, "value") else str(ent.allegiance),
                status=ent.status.value if hasattr(ent.status, "value") else str(ent.status),
                first_observed=ent.first_observed,
                last_observed=ent.last_observed,
                observation_count=ent.observation_count,
                event_count=ent.event_count,
                attributes=ent.attributes,
                latitude=lat,
                longitude=lon,
                sector_id=sec,
                associated_entity_ids=ent.associated_entity_ids if hasattr(ent, "associated_entity_ids") else [],
            )

    def analyze_graph(self, request: GraphAnalyzeRequest) -> GraphAnalyzeResponse:
        """
        Executes full graph intelligence analysis:
        Builds/retrieves graph state, evaluates relationships, detects communities,
        calculates centrality, runs assessments, and constructs the response envelope.
        """
        as_of = request.as_of or datetime.now(timezone.utc)
        stats = self.graph_engine.get_statistics(as_of=as_of)

        all_nodes = self.graph_engine.node_registry.get_active_nodes(as_of)
        all_edges = self.graph_engine.edge_registry.get_active_edges(as_of)

        # Apply filters
        if request.node_types:
            type_set = set(request.node_types)
            all_nodes = [n for n in all_nodes if n.node_type in type_set]

        if request.edge_types:
            etype_set = set(request.edge_types)
            all_edges = [e for e in all_edges if e.edge_type in etype_set]

        if request.min_confidence > 0.0:
            all_edges = [e for e in all_edges if e.confidence >= request.min_confidence]

        # Enforce limits
        truncated = False
        trunc_reason = None
        if len(all_nodes) > request.limit:
            all_nodes = all_nodes[:request.limit]
            truncated = True
            trunc_reason = f"Node count truncated to limit {request.limit}."

        if len(all_edges) > request.limit:
            all_edges = all_edges[:request.limit]
            truncated = True
            trunc_reason = f"Edge count truncated to limit {request.limit}."

        # Analytical components
        relationships = self.graph_engine.relationships.evaluate_all_relationships(as_of=as_of)
        communities = self.graph_engine.communities()
        centralities = self.graph_engine.centrality()
        assessment = self.graph_engine.assess(as_of=as_of)

        # Build provenance mapping and epistemic ledger
        provenance_map: Dict[str, List] = {}
        for e in all_edges:
            if e.provenance:
                provenance_map[e.edge_id] = e.provenance

        epistemic_ledger: Dict[str, List[str]] = {
            "OBSERVED": [n.node_id for n in all_nodes if n.epistemic_status.value == "OBSERVED"],
            "FUSED": [n.node_id for n in all_nodes if n.epistemic_status.value == "FUSED"],
            "INFERRED": [n.node_id for n in all_nodes if n.epistemic_status.value == "INFERRED"],
            "PREDICTED": [n.node_id for n in all_nodes if n.epistemic_status.value == "PREDICTED"],
            "UNCERTAIN": [e.edge_id for e in all_edges if e.epistemic_status.value == "UNCERTAIN"],
        }

        graph_id = f"GRAPH-{hashlib.sha256((as_of.isoformat() + str(stats.node_count)).encode()).hexdigest()[:12]}"

        return GraphAnalyzeResponse(
            graph_id=graph_id,
            as_of=as_of,
            statistics=stats,
            nodes=all_nodes,
            edges=all_edges,
            relationships=relationships,
            communities=communities,
            centrality=centralities,
            changes=[],
            assessment=assessment,
            provenance=provenance_map,
            epistemic_ledger=epistemic_ledger,
            version=self.config.version,
            truncated=truncated,
            truncation_reason=trunc_reason,
        )

    def get_entity_network(
        self,
        entity_id: str,
        depth: int = 1,
        as_of: Optional[datetime] = None,
    ) -> EntityNetworkResponse:
        """Returns the ego-network and analytical context for an entity."""
        eval_time = as_of or datetime.now(timezone.utc)
        net = self.graph_engine.entity_network(entity_id=entity_id, depth=depth, as_of=eval_time)

        # Collect supporting evidence
        all_ev = set()
        for r in net.get("relationships", []):
            all_ev.update(r.supporting_evidence)

        assessment = self.graph_engine.assess(as_of=eval_time)
        communities = self.graph_engine.communities()

        # Find communities containing this entity
        focus_communities = [
            c for c in communities if entity_id in c.member_entities
        ]

        return EntityNetworkResponse(
            focus_entity=entity_id,
            neighbors=net.get("neighbors", []),
            edges=net.get("edges", []),
            relationships=net.get("relationships", []),
            clusters=focus_communities,
            supporting_evidence=sorted(list(all_ev)),
            relationship_changes=[],
            network_statistics=net.get("network_statistics", {}),
            assessment=assessment,
        )

    def get_path(
        self,
        source: str,
        target: str,
        max_depth: Optional[int] = None,
        as_of: Optional[datetime] = None,
    ) -> PathResult:
        """Finds deterministic shortest evidence path between two entities."""
        return self.graph_engine.shortest_path(source=source, target=target, max_depth=max_depth, as_of=as_of)

    def get_changes(
        self,
        start_time: datetime,
        end_time: datetime,
        entity_id: Optional[str] = None,
    ) -> GraphChangesResponse:
        """Detects changes in relationships between two timestamps."""
        changes = self.graph_engine.relationship_changes(t1=start_time, t2=end_time, entity_id=entity_id)

        summary_counts: Dict[str, int] = {}
        for c in changes:
            summary_counts[c.change.value] = summary_counts.get(c.change.value, 0) + 1

        return GraphChangesResponse(
            start_time=start_time,
            end_time=end_time,
            changes=changes,
            summary=summary_counts,
        )

    def get_snapshot(self, as_of: Optional[datetime] = None) -> GraphSnapshotResponse:
        """Captures point-in-time graph snapshot."""
        eval_time = as_of or datetime.now(timezone.utc)
        snap = self.graph_engine.snapshot(eval_time)
        return GraphSnapshotResponse(snapshot=snap)
