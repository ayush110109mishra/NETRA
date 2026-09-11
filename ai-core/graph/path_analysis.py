"""
Phase 8 Path Analysis Engine for NETRA Knowledge Graph.
Evidence-grounded traversable path finding with deterministic tie-breaking and weakest-link confidence modeling.
"""

from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from config import NetraConfig, default_config
from models.knowledge_graph import EdgeType, GraphEdge, GraphNode, NodeType, PathResult
from models.predictive_intelligence import EpistemicStatus
from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry


class PathAnalysisEngine:
    """
    Finds traversable paths between entities with multi-tier deterministic tie-breaking:
    1. Shortest hop count
    2. Highest bottleneck path confidence
    3. Highest average evidence quality
    4. Lexicographical canonical node sequence
    """

    def __init__(
        self,
        node_registry: NodeRegistry,
        edge_registry: EdgeRegistry,
        config: Optional[NetraConfig] = None,
    ) -> None:
        self.node_registry = node_registry
        self.edge_registry = edge_registry
        self.config = config or default_config

    def find_shortest_path(
        self,
        source_ref: str,
        target_ref: str,
        max_depth: Optional[int] = None,
        as_of: Optional[datetime] = None,
    ) -> PathResult:
        """
        Computes the evidence-supported deterministic shortest path between source and target entities.
        """
        node_src = self.node_registry.get_node_by_reference(source_ref) or self.node_registry.get_node(source_ref)
        node_tgt = self.node_registry.get_node_by_reference(target_ref) or self.node_registry.get_node(target_ref)

        if not node_src or not node_tgt:
            return PathResult(
                path_found=False,
                source=source_ref,
                target=target_ref,
                explanation=f"One or both entities ({source_ref}, {target_ref}) not found in the knowledge graph.",
            )

        if node_src.node_id == node_tgt.node_id:
            return PathResult(
                path_found=True,
                source=source_ref,
                target=target_ref,
                nodes=[node_src.node_id],
                edges=[],
                hop_count=0,
                path_confidence=1.0,
                weakest_link=None,
                supporting_evidence=[],
                explanation=f"Source and target refer to the same node ({node_src.label}).",
            )

        limit_depth = max_depth or self.config.path_config.max_search_depth
        min_edge_conf = self.config.path_config.min_edge_confidence

        # Breadth-First Search to discover all candidate shortest paths
        # Queue item: (current_node_id, [node_ids], [edge_ids])
        queue = deque([(node_src.node_id, [node_src.node_id], [])])
        shortest_hop_len = None
        candidate_paths: List[Tuple[List[str], List[str]]] = []
        visited_at_depth: Dict[str, int] = {node_src.node_id: 0}

        while queue:
            curr_id, path_nodes, path_edges = queue.popleft()
            curr_depth = len(path_edges)

            if shortest_hop_len is not None and curr_depth > shortest_hop_len:
                break
            if curr_depth >= limit_depth:
                continue

            # Incident edges
            incident = self.edge_registry.get_incident_edges(curr_id)
            for edge in incident:
                # Temporal filtering if as_of is provided
                if as_of:
                    if edge.valid_from and edge.valid_from > as_of:
                        continue
                    if edge.valid_to and edge.valid_to < as_of:
                        continue
                if edge.confidence < min_edge_conf:
                    continue

                neighbor_id = edge.target_node_id if edge.source_node_id == curr_id else edge.source_node_id
                if not edge.is_directional or edge.source_node_id == curr_id:
                    pass  # Traversable
                else:
                    # Directional edge: can only traverse in source -> target direction
                    continue

                if neighbor_id in path_nodes:
                    continue  # Avoid loops

                next_depth = curr_depth + 1
                if neighbor_id in visited_at_depth and visited_at_depth[neighbor_id] < next_depth:
                    continue
                visited_at_depth[neighbor_id] = next_depth

                new_nodes = path_nodes + [neighbor_id]
                new_edges = path_edges + [edge.edge_id]

                if neighbor_id == node_tgt.node_id:
                    shortest_hop_len = next_depth
                    candidate_paths.append((new_nodes, new_edges))
                else:
                    queue.append((neighbor_id, new_nodes, new_edges))

        if not candidate_paths:
            return PathResult(
                path_found=False,
                source=source_ref,
                target=target_ref,
                explanation=f"No evidence-supported path was found between {source_ref} and {target_ref} within the requested graph scope.",
            )

        # Deterministic multi-tier tie-breaking among candidate paths
        best_path = self._select_best_path(candidate_paths)
        nodes_seq, edges_seq = best_path

        # Compute metrics along the chosen path
        edges = [self.edge_registry.get_edge(eid) for eid in edges_seq if self.edge_registry.get_edge(eid)]
        confidences = [e.confidence for e in edges]
        min_conf = min(confidences) if confidences else 1.0
        weakest_edge = edges[confidences.index(min_conf)].edge_id if edges else None

        all_evidence = set()
        epistemic_counts: Dict[str, int] = {}
        explanation_parts = []

        for i, edge in enumerate(edges):
            all_evidence.update(edge.evidence_ids)
            tier = edge.epistemic_status.value
            epistemic_counts[tier] = epistemic_counts.get(tier, 0) + 1

            src_n = self.node_registry.get_node(edge.source_node_id)
            tgt_n = self.node_registry.get_node(edge.target_node_id)
            src_lbl = src_n.label if src_n else edge.source_node_id
            tgt_lbl = tgt_n.label if tgt_n else edge.target_node_id
            explanation_parts.append(f"{src_lbl} --[{edge.edge_type.value}]--> {tgt_lbl}")

        explanation = " Path: " + " -> ".join(explanation_parts) if explanation_parts else "Direct connection"

        return PathResult(
            path_found=True,
            source=source_ref,
            target=target_ref,
            nodes=nodes_seq,
            edges=edges_seq,
            hop_count=len(edges_seq),
            path_confidence=round(min_conf, 4),
            weakest_link=weakest_edge,
            supporting_evidence=sorted(list(all_evidence)),
            epistemic_breakdown=epistemic_counts,
            explanation=f"Evidence path found between {source_ref} and {target_ref} ({len(edges_seq)} hops, confidence: {min_conf:.2f}).{explanation}",
        )

    def _select_best_path(self, candidates: List[Tuple[List[str], List[str]]]) -> Tuple[List[str], List[str]]:
        """
        Sorts candidates by:
        1. Minimal hop count
        2. Highest bottleneck confidence (descending)
        3. Highest average confidence (descending)
        4. Canonical node IDs string (ascending)
        """
        def score_path(cand: Tuple[List[str], List[str]]) -> Tuple[int, float, float, str]:
            nodes, edge_ids = cand
            hop_count = len(edge_ids)
            edges = [self.edge_registry.get_edge(eid) for eid in edge_ids if self.edge_registry.get_edge(eid)]
            confs = [e.confidence for e in edges] if edges else [1.0]
            bottleneck = min(confs)
            avg_conf = sum(confs) / len(confs)
            canonical_str = "-".join(nodes)
            # Invert values for descending sort where lower key is better
            return (hop_count, -bottleneck, -avg_conf, canonical_str)

        return min(candidates, key=score_path)
