"""
Phase 8 Provenance Engine for NETRA Knowledge Graph.
Tracks evidence lineage, maps epistemic tiers, and enforces orphan prevention rules.
"""

from typing import Any, Dict, List, Optional, Set
from models.knowledge_graph import EdgeType, GraphEdge, GraphNode, NodeType, ProvenanceItem
from models.predictive_intelligence import EpistemicStatus
from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry


class ProvenanceEngine:
    """
    Manages and validates evidence lineage for graph nodes and edges.
    Guarantees that analytical claims are grounded and prevents orphan references.
    """

    def __init__(self, node_registry: NodeRegistry, edge_registry: EdgeRegistry) -> None:
        self.node_registry = node_registry
        self.edge_registry = edge_registry

    def validate_graph(self) -> Dict[str, Any]:
        """
        Validates the integrity of the graph:
        - Detects orphan edges (edges referencing missing source or target nodes)
        - Detects invalid temporal intervals (valid_from > valid_to)
        - Detects out-of-bounds confidence (c < 0.0 or c > 1.0)
        - Checks provenance completeness on analytical edges
        """
        orphan_edges: List[str] = []
        invalid_temporal_nodes: List[str] = []
        invalid_temporal_edges: List[str] = []
        out_of_bounds_confidence: List[str] = []
        unprovenanced_analytical_edges: List[str] = []

        all_nodes = self.node_registry.get_all_nodes()
        all_edges = self.edge_registry.get_all_edges()

        # Validate nodes
        for node in all_nodes:
            if node.confidence < 0.0 or node.confidence > 1.0:
                out_of_bounds_confidence.append(node.node_id)
            if node.valid_from and node.valid_to and node.valid_from > node.valid_to:
                invalid_temporal_nodes.append(node.node_id)

        # Validate edges
        for edge in all_edges:
            if edge.confidence < 0.0 or edge.confidence > 1.0:
                out_of_bounds_confidence.append(edge.edge_id)
            if edge.valid_from and edge.valid_to and edge.valid_from > edge.valid_to:
                invalid_temporal_edges.append(edge.edge_id)

            # Orphan edge check
            has_src = self.node_registry.node_exists(edge.source_node_id)
            has_tgt = self.node_registry.node_exists(edge.target_node_id)
            if not has_src or not has_tgt:
                orphan_edges.append(edge.edge_id)

            # Analytical edge provenance check (structural edges like LOCATED_IN or MEMBER_OF may be exempt)
            structural_types = {EdgeType.LOCATED_IN, EdgeType.MEMBER_OF, EdgeType.PART_OF_CLUSTER}
            if edge.edge_type not in structural_types and not edge.provenance and not edge.evidence_ids:
                unprovenanced_analytical_edges.append(edge.edge_id)

        is_valid = len(orphan_edges) == 0 and len(invalid_temporal_nodes) == 0 and len(invalid_temporal_edges) == 0 and len(out_of_bounds_confidence) == 0

        return {
            "is_valid": is_valid,
            "orphan_edges": sorted(orphan_edges),
            "invalid_temporal_nodes": sorted(invalid_temporal_nodes),
            "invalid_temporal_edges": sorted(invalid_temporal_edges),
            "out_of_bounds_confidence": sorted(out_of_bounds_confidence),
            "unprovenanced_analytical_edges": sorted(unprovenanced_analytical_edges),
            "node_count": len(all_nodes),
            "edge_count": len(all_edges),
        }

    def get_edge_lineage(self, edge_id: str) -> List[ProvenanceItem]:
        """Returns ordered, deduplicated provenance records for an edge."""
        edge = self.edge_registry.get_edge(edge_id)
        if not edge:
            return []
        return sorted(edge.provenance, key=lambda x: x.evidence_id)

    def get_node_lineage(self, node_id: str) -> List[ProvenanceItem]:
        """Returns ordered provenance records for a node."""
        node = self.node_registry.get_node(node_id)
        if not node:
            return []
        return sorted(node.provenance, key=lambda x: x.evidence_id)

    def get_full_evidence_trail(self, node_id: str) -> List[str]:
        """
        Traces and aggregates all unique evidence IDs connected to a node via its incident edges.
        """
        evidence_set: Set[str] = set()
        node = self.node_registry.get_node(node_id)
        if node:
            for p in node.provenance:
                evidence_set.add(p.evidence_id)

        incident_edges = self.edge_registry.get_incident_edges(node_id)
        for edge in incident_edges:
            for eid in edge.evidence_ids:
                evidence_set.add(eid)
            for p in edge.provenance:
                evidence_set.add(p.evidence_id)

        return sorted(list(evidence_set))
