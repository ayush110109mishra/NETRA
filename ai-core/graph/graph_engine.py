"""
Phase 8 Master Knowledge Graph Engine for NETRA.
Unifies node/edge registries, builder, temporal snapshots, relationship intelligence,
path analysis, centrality, community partitioning, and 5-tier epistemic assessments.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from config import NetraConfig, default_config
from models.knowledge_graph import (
    CentralityResult,
    CommunityResult,
    GraphAssessment,
    GraphEdge,
    GraphNode,
    GraphSnapshot,
    GraphStatistics,
    NodeType,
    PathResult,
    RelationshipChange,
    RelationshipDetail,
    RelationshipStatus,
)
from models.predictive_intelligence import EpistemicStatus
from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry
from graph.graph_builder import KnowledgeGraphBuilder
from graph.provenance import ProvenanceEngine
from graph.temporal_graph import TemporalGraphEngine
from graph.relationship_intelligence import RelationshipIntelligenceEngine
from graph.relationship_change import RelationshipChangeEngine
from graph.path_analysis import PathAnalysisEngine
from graph.centrality import CentralityEngine
from graph.community import CommunityEngine
from graph.graph_query import GraphQueryEngine


class KnowledgeGraphEngine:
    """
    Primary interface for NETRA Phase 8 Knowledge Graph & Relationship Intelligence.
    Coordinates analytical graph pipelines and strictly preserves epistemic separation.
    """

    def __init__(self, config: Optional[NetraConfig] = None) -> None:
        self.config = config or default_config
        self.node_registry = NodeRegistry()
        self.edge_registry = EdgeRegistry()
        self.builder = KnowledgeGraphBuilder(self.node_registry, self.edge_registry)
        self.provenance = ProvenanceEngine(self.node_registry, self.edge_registry)
        self.temporal = TemporalGraphEngine(self.node_registry, self.edge_registry)
        self.relationships = RelationshipIntelligenceEngine(
            self.node_registry, self.edge_registry, self.config
        )
        self.changes = RelationshipChangeEngine(self.relationships, self.config)
        self.paths = PathAnalysisEngine(
            self.node_registry, self.edge_registry, self.config
        )
        self.centrality_engine = CentralityEngine(self.node_registry, self.edge_registry)
        self.community_engine = CommunityEngine(
            self.node_registry, self.edge_registry, self.config
        )
        self.query_engine = GraphQueryEngine(
            self.node_registry, self.edge_registry, self.relationships, self.config
        )

    def get_statistics(self, as_of: Optional[datetime] = None) -> GraphStatistics:
        """Computes descriptive non-threat topological statistics for the graph."""
        nodes = self.temporal.get_snapshot(as_of).nodes if as_of else self.node_registry.get_all_nodes()
        edges = self.temporal.get_snapshot(as_of).edges if as_of else self.edge_registry.get_all_edges()

        n_count = len(nodes)
        e_count = len(edges)

        type_counts: Dict[NodeType, int] = {}
        for n in nodes:
            type_counts[n.node_type] = type_counts.get(n.node_type, 0) + 1

        communities = self.community_engine.detect_communities()
        density = (2.0 * e_count) / (n_count * (n_count - 1)) if n_count > 1 else 0.0
        avg_deg = (2.0 * e_count) / n_count if n_count > 0 else 0.0

        isolated = sum(
            1 for n in nodes if len(self.edge_registry.get_incident_edges(n.node_id)) == 0
        )

        return GraphStatistics(
            node_count=n_count,
            edge_count=e_count,
            entity_count=type_counts.get(NodeType.ENTITY, 0),
            event_count=type_counts.get(NodeType.EVENT, 0),
            source_count=type_counts.get(NodeType.SOURCE, 0),
            anomaly_count=type_counts.get(NodeType.ANOMALY, 0),
            forecast_count=type_counts.get(NodeType.FORECAST, 0),
            community_count=len(communities),
            connected_component_count=len(communities),
            graph_density=round(density, 4),
            average_degree=round(avg_deg, 4),
            isolated_node_count=isolated,
        )

    def assess(self, as_of: Optional[datetime] = None) -> GraphAssessment:
        """
        Synthesizes a structured 5-tier epistemic assessment of current graph intelligence:
        OBSERVED, FUSED, INFERRED, PREDICTED, UNCERTAIN.
        """
        eval_time = as_of or datetime.now(timezone.utc)
        nodes = self.node_registry.get_all_nodes()
        edges = self.edge_registry.get_all_edges()
        rel_details = self.relationships.evaluate_all_relationships(as_of=eval_time)

        observed: List[str] = []
        fused: List[str] = []
        inferred: List[str] = []
        predicted: List[str] = []
        uncertain: List[str] = []

        # 1. Node assessments
        entity_count = sum(1 for n in nodes if n.node_type == NodeType.ENTITY)
        event_count = sum(1 for n in nodes if n.node_type == NodeType.EVENT)
        source_count = sum(1 for n in nodes if n.node_type == NodeType.SOURCE)

        if entity_count > 0:
            observed.append(f"{entity_count} canonical operational entity/entities monitored.")
        if event_count > 0:
            observed.append(f"{event_count} discrete events registered across operational sectors.")
        if source_count > 0:
            observed.append(f"{source_count} sensor/telemetry source feeds integrated.")

        # 2. Fused observations
        fused_nodes = [n for n in nodes if n.node_type == NodeType.FUSED_OBSERVATION]
        if fused_nodes:
            fused.append(f"{len(fused_nodes)} cross-sensor fused observation track(s) corroborated.")

        # 3. Inferred relationships & anomalies
        anom_nodes = [n for n in nodes if n.node_type == NodeType.ANOMALY]
        if anom_nodes:
            inferred.append(f"{len(anom_nodes)} behavioral anomaly signature(s) attributed.")

        persistent_rels = [r for r in rel_details if r.status == RelationshipStatus.PERSISTENT]
        if persistent_rels:
            inferred.append(f"{len(persistent_rels)} persistent entity association(s) established.")

        active_rels = [r for r in rel_details if r.status == RelationshipStatus.ACTIVE]
        if active_rels:
            inferred.append(f"{len(active_rels)} active entity relationship(s) detected.")

        # 4. Predicted forecasts
        forecast_nodes = [n for n in nodes if n.node_type == NodeType.FORECAST]
        if forecast_nodes:
            predicted.append(f"{len(forecast_nodes)} predictive state forecast(s) generated.")

        # 5. Uncertain / disputed edges
        disputed_rels = [r for r in rel_details if r.is_disputed]
        if disputed_rels:
            for d in disputed_rels:
                uncertain.append(
                    f"Relationship {d.source_entity_id} <-> {d.target_entity_id} is disputed by conflicting reports."
                )

        summary = (
            f"Knowledge graph tracks {entity_count} entities with {len(rel_details)} relationships "
            f"and {len(persistent_rels)} persistent links. {len(disputed_rels)} relationship(s) disputed."
        )

        return GraphAssessment(
            observed=sorted(observed),
            fused=sorted(fused),
            inferred=sorted(inferred),
            predicted=sorted(predicted),
            uncertain=sorted(uncertain),
            summary=summary,
        )

    def entity_network(
        self,
        entity_id: str,
        depth: int = 1,
        as_of: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Convenience method for querying an entity's ego-network."""
        return self.query_engine.get_entity_network(entity_id=entity_id, depth=depth, as_of=as_of)

    def shortest_path(
        self,
        source: str,
        target: str,
        max_depth: Optional[int] = None,
        as_of: Optional[datetime] = None,
    ) -> PathResult:
        """Convenience method for finding evidence shortest path."""
        return self.paths.find_shortest_path(source_ref=source, target_ref=target, max_depth=max_depth, as_of=as_of)

    def relationship_changes(
        self,
        t1: datetime,
        t2: datetime,
        entity_id: Optional[str] = None,
    ) -> List[RelationshipChange]:
        """Convenience method for detecting relationship deltas."""
        return self.changes.detect_changes(t1=t1, t2=t2, entity_id=entity_id)

    def centrality(self) -> List[CentralityResult]:
        """Convenience method for computing network centrality."""
        return self.centrality_engine.calculate_centralities()

    def communities(self) -> List[CommunityResult]:
        """Convenience method for detecting network communities."""
        return self.community_engine.detect_communities()

    def snapshot(self, as_of: datetime) -> GraphSnapshot:
        """Convenience method for capturing a point-in-time snapshot."""
        return self.temporal.get_snapshot(as_of)

    def clear(self) -> None:
        """Resets the graph registries and caches."""
        self.node_registry.clear()
        self.edge_registry.clear()
        self.temporal._snapshot_cache.clear()
