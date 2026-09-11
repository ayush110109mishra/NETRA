"""
Phase 8 Graph Query Engine for NETRA Knowledge Graph.
Hop-bounded ego-networks, subgraphs, neighbor traversals, and query safeguards.
"""

from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from config import NetraConfig, default_config
from models.knowledge_graph import (
    EdgeType,
    GraphEdge,
    GraphNode,
    NodeType,
    RelationshipDetail,
)
from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry
from graph.relationship_intelligence import RelationshipIntelligenceEngine


class GraphQueryEngine:
    """
    Executes bounded, deterministic queries against the knowledge graph.
    Prevents unbounded expansion and enforces maximum node and edge limits.
    """

    def __init__(
        self,
        node_registry: NodeRegistry,
        edge_registry: EdgeRegistry,
        rel_engine: RelationshipIntelligenceEngine,
        config: Optional[NetraConfig] = None,
    ) -> None:
        self.node_registry = node_registry
        self.edge_registry = edge_registry
        self.rel_engine = rel_engine
        self.config = config or default_config

    def get_neighbors(
        self,
        node_id: str,
        depth: int = 1,
        as_of: Optional[datetime] = None,
    ) -> Tuple[List[GraphNode], List[GraphEdge], bool, Optional[str]]:
        """
        Traverses outbound and incident connections up to `depth` hops (clamped to max_depth).
        Returns (nodes, edges, truncated, truncation_reason).
        """
        max_d = min(depth, self.config.graph.max_depth)
        max_nodes = self.config.graph.max_nodes
        max_edges = self.config.graph.max_edges

        visited_nodes: Set[str] = {node_id}
        collected_edges: Set[str] = set()
        queue = deque([(node_id, 0)])

        truncated = False
        truncation_reason = None

        while queue:
            curr_id, curr_d = queue.popleft()
            if curr_d >= max_d:
                continue

            incident = self.edge_registry.get_incident_edges(curr_id)
            for edge in incident:
                if as_of:
                    if edge.valid_from and edge.valid_from > as_of:
                        continue
                    if edge.valid_to and edge.valid_to < as_of:
                        continue

                collected_edges.add(edge.edge_id)
                nbr_id = edge.target_node_id if edge.source_node_id == curr_id else edge.source_node_id

                if nbr_id not in visited_nodes:
                    if len(visited_nodes) >= max_nodes:
                        truncated = True
                        truncation_reason = f"Exceeded maximum node traversal limit ({max_nodes})."
                        break
                    visited_nodes.add(nbr_id)
                    queue.append((nbr_id, curr_d + 1))

            if len(collected_edges) >= max_edges:
                truncated = True
                truncation_reason = f"Exceeded maximum edge traversal limit ({max_edges})."
                break

        # Retrieve objects
        nodes = [self.node_registry.get_node(nid) for nid in sorted(list(visited_nodes)) if self.node_registry.get_node(nid)]
        edges = [self.edge_registry.get_edge(eid) for eid in sorted(list(collected_edges)) if self.edge_registry.get_edge(eid)]

        return nodes, edges, truncated, truncation_reason

    def get_entity_network(
        self,
        entity_id: str,
        depth: int = 1,
        as_of: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Queries the ego-network centered around an entity.
        """
        target_node = self.node_registry.get_node_by_reference(entity_id) or self.node_registry.get_node(entity_id)
        if not target_node:
            return {
                "focus_entity": entity_id,
                "neighbors": [],
                "edges": [],
                "relationships": [],
                "network_statistics": {"node_count": 0, "edge_count": 0},
            }

        nodes, edges, truncated, reason = self.get_neighbors(target_node.node_id, depth=depth, as_of=as_of)

        # Retrieve relationship details for entity neighbors
        neighbor_entities = [n.label for n in nodes if n.node_type == NodeType.ENTITY and n.label != entity_id]
        rel_details = []
        for n_ent in neighbor_entities:
            detail = self.rel_engine.evaluate_relationship(entity_id, n_ent, as_of=as_of)
            if detail:
                rel_details.append(detail)

        return {
            "focus_entity": entity_id,
            "neighbors": nodes,
            "edges": edges,
            "relationships": sorted(rel_details, key=lambda r: (r.source_entity_id, r.target_entity_id)),
            "truncated": truncated,
            "truncation_reason": reason,
            "network_statistics": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "neighbor_entity_count": len(neighbor_entities),
            },
        }
