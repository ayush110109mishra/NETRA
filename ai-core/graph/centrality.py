"""
Phase 8 Centrality Analysis Engine for NETRA Knowledge Graph.
Computes degree, weighted degree, and betweenness centrality.
Note: Centrality denotes purely structural importance within the graph topology, NOT threat level.
"""

from collections import deque
from typing import Dict, List, Set
from models.knowledge_graph import CentralityResult, GraphNode
from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry


class CentralityEngine:
    """
    Computes structural topology metrics across the knowledge graph.
    Employs deterministic Brandes algorithm for betweenness centrality.
    """

    def __init__(self, node_registry: NodeRegistry, edge_registry: EdgeRegistry) -> None:
        self.node_registry = node_registry
        self.edge_registry = edge_registry

    def calculate_centralities(self) -> List[CentralityResult]:
        """
        Calculates degree, weighted degree, and betweenness centrality for all nodes.
        Guarantees deterministic execution and sorted output.
        """
        nodes = self.node_registry.get_all_nodes()
        n_count = len(nodes)
        if n_count == 0:
            return []

        # Build adjacency mapping for betweenness
        # adj[u] = sorted list of neighbor node IDs
        adj: Dict[str, List[str]] = {}
        weighted_degrees: Dict[str, float] = {n.node_id: 0.0 for n in nodes}

        for node in nodes:
            incident = self.edge_registry.get_incident_edges(node.node_id)
            neighbors: Set[str] = set()
            w_sum = 0.0
            for e in incident:
                nbr = e.target_node_id if e.source_node_id == node.node_id else e.source_node_id
                if nbr != node.node_id:
                    neighbors.add(nbr)
                w_sum += e.strength

            adj[node.node_id] = sorted(list(neighbors))
            weighted_degrees[node.node_id] = round(w_sum, 4)

        # 1. Degree Centrality (normalized by N - 1)
        norm_factor = (n_count - 1) if n_count > 1 else 1.0
        degree_centrality: Dict[str, float] = {
            nid: round(len(adj[nid]) / norm_factor, 4) for nid in adj
        }

        # 2. Betweenness Centrality (Brandes Algorithm)
        betweenness: Dict[str, float] = {n.node_id: 0.0 for n in nodes}

        # Iterate through nodes in deterministic sorted order
        for s in sorted([n.node_id for n in nodes]):
            stack: List[str] = []
            predecessors: Dict[str, List[str]] = {n.node_id: [] for n in nodes}
            sigma: Dict[str, int] = {n.node_id: 0 for n in nodes}
            sigma[s] = 1
            dist: Dict[str, int] = {n.node_id: -1 for n in nodes}
            dist[s] = 0

            queue = deque([s])
            while queue:
                v = queue.popleft()
                stack.append(v)
                for w in adj[v]:
                    if dist[w] < 0:
                        dist[w] = dist[v] + 1
                        queue.append(w)
                    if dist[w] == dist[v] + 1:
                        sigma[w] += sigma[v]
                        predecessors[w].append(v)

            delta: Dict[str, float] = {n.node_id: 0.0 for n in nodes}
            while stack:
                w = stack.pop()
                for v in predecessors[w]:
                    if sigma[w] > 0:
                        delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
                if w != s:
                    betweenness[w] += delta[w]

        # Normalize betweenness for undirected graph: divide by ((N-1)(N-2)/2)
        if n_count > 2:
            scale = 2.0 / ((n_count - 1) * (n_count - 2))
            for nid in betweenness:
                betweenness[nid] = round(betweenness[nid] * scale, 4)
        else:
            for nid in betweenness:
                betweenness[nid] = 0.0

        # Classify structural role
        results: List[CentralityResult] = []
        for node in nodes:
            deg = degree_centrality[node.node_id]
            bet = betweenness[node.node_id]
            w_deg = weighted_degrees[node.node_id]

            if bet >= 0.15 and bet >= deg:
                role = "BRIDGE"
            elif deg >= 0.40:
                role = "HUB"
            else:
                role = "PERIPHERAL"

            results.append(
                CentralityResult(
                    node_id=node.node_id,
                    node_type=node.node_type,
                    label=node.label,
                    degree_centrality=deg,
                    weighted_degree=w_deg,
                    betweenness_centrality=bet,
                    structural_role=role,
                )
            )

        return sorted(results, key=lambda c: (c.node_id, c.label))
