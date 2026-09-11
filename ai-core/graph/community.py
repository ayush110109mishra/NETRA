"""
Phase 8 Community Analysis Engine for NETRA Knowledge Graph.
Deterministic connected components and community partitioning.
Note: Community clustering is purely structural topology; it does not infer real-world allegiance.
"""

import hashlib
from typing import Dict, List, Optional, Set
from config import NetraConfig, default_config
from models.knowledge_graph import CommunityResult, NodeType
from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry


class CommunityEngine:
    """
    Partitions the knowledge graph into deterministic structural communities.
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

    def detect_communities(self) -> List[CommunityResult]:
        """
        Detects connected components and structural communities deterministically.
        """
        nodes = self.node_registry.get_all_nodes()
        if not nodes:
            return []

        # Find connected components via BFS starting from canonically sorted unvisited nodes
        visited: Set[str] = set()
        components: List[List[str]] = []

        for node in sorted(nodes, key=lambda n: n.node_id):
            if node.node_id in visited:
                continue

            # BFS for component
            comp_members: List[str] = []
            queue = [node.node_id]
            visited.add(node.node_id)

            while queue:
                # Deterministic pop
                curr_id = queue.pop(0)
                comp_members.append(curr_id)

                incident = self.edge_registry.get_incident_edges(curr_id)
                # Sort neighbors deterministically
                neighbors = set()
                for e in incident:
                    nbr = e.target_node_id if e.source_node_id == curr_id else e.source_node_id
                    neighbors.add(nbr)

                for nbr_id in sorted(list(neighbors)):
                    if nbr_id not in visited and self.node_registry.node_exists(nbr_id):
                        visited.add(nbr_id)
                        queue.append(nbr_id)

            components.append(sorted(comp_members))

        # Build CommunityResults
        communities: List[CommunityResult] = []
        min_size = self.config.community_config.min_community_size

        for member_ids in components:
            if len(member_ids) < min_size:
                continue

            member_set = set(member_ids)
            member_nodes = [self.node_registry.get_node(mid) for mid in member_ids if self.node_registry.get_node(mid)]
            entity_members = [
                n.label for n in member_nodes if n.node_type == NodeType.ENTITY
            ]

            # Internal vs External edges
            internal_edges = []
            external_edge_count = 0
            all_evidence = set()
            edge_strengths = []

            for mid in member_ids:
                incident = self.edge_registry.get_incident_edges(mid)
                for e in incident:
                    nbr = e.target_node_id if e.source_node_id == mid else e.source_node_id
                    if nbr in member_set:
                        # Only count once by ordering
                        if e.source_node_id <= e.target_node_id:
                            internal_edges.append(e)
                            all_evidence.update(e.evidence_ids)
                            edge_strengths.append(e.strength)
                    else:
                        external_edge_count += 1

            n_v = len(member_ids)
            density = 0.0
            if n_v > 1:
                max_edges = (n_v * (n_v - 1)) / 2.0
                density = round(len(internal_edges) / max_edges, 4)

            avg_strength = round(sum(edge_strengths) / len(edge_strengths), 4) if edge_strengths else 0.0

            # Deterministic community ID
            digest = hashlib.sha256(",".join(member_ids).encode("utf-8")).hexdigest()[:12]
            comm_id = f"COMM-{digest}"

            communities.append(
                CommunityResult(
                    community_id=comm_id,
                    member_nodes=sorted(member_ids),
                    member_entities=sorted(entity_members),
                    internal_edge_count=len(internal_edges),
                    external_edge_count=external_edge_count,
                    density=density,
                    average_relationship_strength=avg_strength,
                    supporting_evidence=sorted(list(all_evidence)),
                    confidence=1.0,
                )
            )

        return sorted(communities, key=lambda c: (c.community_id, -len(c.member_nodes)))
