"""
Phase 8 Temporal Graph Engine for NETRA.
Point-in-time snapshot generation, temporal validity filtering, and reproducible snapshot IDs.
"""

import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional
from models.knowledge_graph import GraphEdge, GraphNode, GraphSnapshot
from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry


class TemporalGraphEngine:
    """
    Evaluates graph states at arbitrary point-in-time timestamps (as_of)
    and produces deterministic, bit-for-bit reproducible graph snapshots.
    """

    def __init__(self, node_registry: NodeRegistry, edge_registry: EdgeRegistry) -> None:
        self.node_registry = node_registry
        self.edge_registry = edge_registry
        self._snapshot_cache: Dict[str, GraphSnapshot] = {}

    def get_snapshot(self, as_of: datetime) -> GraphSnapshot:
        """
        Generates a point-in-time snapshot of the graph active at `as_of`.
        Ensures active edges only connect active nodes at that timestamp.
        """
        # Canonical string key for cache
        as_of_key = as_of.isoformat()
        if as_of_key in self._snapshot_cache:
            return self._snapshot_cache[as_of_key]

        active_nodes = self.node_registry.get_active_nodes(as_of)
        active_node_ids = {n.node_id for n in active_nodes}

        raw_active_edges = self.edge_registry.get_active_edges(as_of)
        # Filter edges to ensure both endpoints are active
        active_edges = [
            e for e in raw_active_edges
            if e.source_node_id in active_node_ids and e.target_node_id in active_node_ids
        ]

        # Sort canonically
        active_nodes = sorted(active_nodes, key=lambda n: n.node_id)
        active_edges = sorted(active_edges, key=lambda e: (e.source_node_id, e.edge_type.value, e.target_node_id, e.edge_id))

        # Compute deterministic snapshot ID
        hash_payload = f"{as_of_key}:" + ",".join(n.node_id for n in active_nodes) + ":" + ",".join(e.edge_id for e in active_edges)
        snapshot_id = f"SNAP-{hashlib.sha256(hash_payload.encode('utf-8')).hexdigest()[:16]}"

        snapshot = GraphSnapshot(
            snapshot_id=snapshot_id,
            as_of=as_of,
            nodes=active_nodes,
            edges=active_edges,
            node_count=len(active_nodes),
            edge_count=len(active_edges),
            created_at=as_of,
        )

        self._snapshot_cache[as_of_key] = snapshot
        return snapshot

    def get_edges_in_window(self, start_time: datetime, end_time: datetime) -> List[GraphEdge]:
        """
        Returns all edges whose validity or observation overlaps with [start_time, end_time].
        """
        all_edges = self.edge_registry.get_all_edges()
        window_edges = []
        for e in all_edges:
            # Check valid_from / valid_to
            e_start = e.valid_from or e.first_observed_at
            e_end = e.valid_to or e.last_observed_at

            if e_start and e_start > end_time:
                continue
            if e_end and e_end < start_time:
                continue
            window_edges.append(e)

        return sorted(window_edges, key=lambda e: (e.source_node_id, e.edge_type.value, e.target_node_id, e.edge_id))
