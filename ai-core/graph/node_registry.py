"""
Phase 8 Node Registry for NETRA Knowledge Graph.
Deterministic identity, deduplication, type indexing, and temporal validity management.
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Set
from models.knowledge_graph import GraphNode, NodeType, ProvenanceItem
from models.predictive_intelligence import EpistemicStatus


def generate_node_id(node_type: NodeType, canonical_reference: str) -> str:
    """
    Generates a deterministic canonical node ID.
    Ensures identical logical inputs produce identical node IDs across runs.
    """
    raw_key = f"{node_type.value}:{canonical_reference.strip()}"
    digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]
    return f"NODE-{node_type.value}-{digest}"


class NodeRegistry:
    """
    In-memory canonical storage and indexing for knowledge graph nodes.
    Guarantees idempotency, deduplication, and deterministic sorted access.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, GraphNode] = {}
        self._type_index: Dict[NodeType, Set[str]] = {t: set() for t in NodeType}
        self._ref_index: Dict[str, str] = {}  # canonical_reference -> node_id

    def add_node(
        self,
        node_type: NodeType,
        label: str,
        canonical_reference: str,
        created_at: datetime,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        confidence: float = 1.0,
        epistemic_status: EpistemicStatus = EpistemicStatus.OBSERVED,
        attributes: Optional[Dict] = None,
        provenance: Optional[List[ProvenanceItem]] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        sector_id: Optional[str] = None,
    ) -> GraphNode:
        """
        Adds or idempotently updates a node in the registry.
        """
        node_id = generate_node_id(node_type, canonical_reference)
        attributes = attributes or {}
        provenance = provenance or []

        if node_id in self._nodes:
            existing = self._nodes[node_id]
            # Merge attributes
            merged_attrs = dict(existing.attributes)
            merged_attrs.update(attributes)

            # Merge provenance (deduplicated by evidence_id)
            existing_ev_ids = {p.evidence_id for p in existing.provenance}
            merged_provenance = list(existing.provenance)
            for p in provenance:
                if p.evidence_id not in existing_ev_ids:
                    merged_provenance.append(p)
                    existing_ev_ids.add(p.evidence_id)

            # Sort merged provenance deterministically
            merged_provenance.sort(key=lambda x: x.evidence_id)

            # Update temporal bounds
            new_valid_from = min(existing.valid_from, valid_from) if existing.valid_from and valid_from else (existing.valid_from or valid_from)
            new_valid_to = max(existing.valid_to, valid_to) if existing.valid_to and valid_to else (existing.valid_to or valid_to)

            # Update spatial if provided
            lat = latitude if latitude is not None else existing.latitude
            lon = longitude if longitude is not None else existing.longitude
            sec = sector_id if sector_id is not None else existing.sector_id

            updated_node = GraphNode(
                node_id=node_id,
                node_type=node_type,
                label=label or existing.label,
                created_at=min(existing.created_at, created_at),
                valid_from=new_valid_from,
                valid_to=new_valid_to,
                confidence=max(existing.confidence, confidence),
                epistemic_status=existing.epistemic_status if existing.epistemic_status == epistemic_status else epistemic_status,
                attributes=merged_attrs,
                provenance=merged_provenance,
                latitude=lat,
                longitude=lon,
                sector_id=sec,
            )
            self._nodes[node_id] = updated_node
            return updated_node

        # New node
        new_node = GraphNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            created_at=created_at,
            valid_from=valid_from,
            valid_to=valid_to,
            confidence=max(0.0, min(1.0, confidence)),
            epistemic_status=epistemic_status,
            attributes=attributes,
            provenance=sorted(provenance, key=lambda x: x.evidence_id),
            latitude=latitude,
            longitude=longitude,
            sector_id=sector_id,
        )
        self._nodes[node_id] = new_node
        self._type_index[node_type].add(node_id)
        self._ref_index[canonical_reference] = node_id
        return new_node

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Retrieves a node by canonical ID."""
        return self._nodes.get(node_id)

    def get_node_by_reference(self, canonical_reference: str) -> Optional[GraphNode]:
        """Retrieves a node by its raw domain reference."""
        node_id = self._ref_index.get(canonical_reference)
        if node_id:
            return self._nodes.get(node_id)
        return None

    def get_all_nodes(self) -> List[GraphNode]:
        """Returns all nodes sorted canonically by node_id."""
        return [self._nodes[k] for k in sorted(self._nodes.keys())]

    def get_nodes_by_type(self, node_type: NodeType) -> List[GraphNode]:
        """Returns all nodes of a specific type sorted by node_id."""
        node_ids = sorted(self._type_index.get(node_type, set()))
        return [self._nodes[nid] for nid in node_ids]

    def get_active_nodes(self, as_of: datetime) -> List[GraphNode]:
        """
        Returns all nodes temporally active at the specified timestamp.
        valid_from <= as_of <= valid_to.
        """
        active = []
        for nid in sorted(self._nodes.keys()):
            node = self._nodes[nid]
            if node.valid_from and node.valid_from > as_of:
                continue
            if node.valid_to and node.valid_to < as_of:
                continue
            active.append(node)
        return active

    def node_exists(self, node_id: str) -> bool:
        """Checks if a node exists."""
        return node_id in self._nodes

    def count(self) -> int:
        """Returns total registered nodes."""
        return len(self._nodes)

    def clear(self) -> None:
        """Resets the registry."""
        self._nodes.clear()
        for t in self._type_index:
            self._type_index[t].clear()
        self._ref_index.clear()
