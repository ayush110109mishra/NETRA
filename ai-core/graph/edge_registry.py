"""
Phase 8 Edge Registry for NETRA Knowledge Graph.
Deterministic edge identity, deduplication, contradiction preservation, and adjacency indexing.
"""

import hashlib
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from models.knowledge_graph import EdgeType, GraphEdge, ProvenanceItem
from models.predictive_intelligence import EpistemicStatus


def generate_edge_id(
    source_node_id: str,
    target_node_id: str,
    edge_type: EdgeType,
    is_directional: bool = True,
    discriminator: str = "",
) -> str:
    """
    Generates a deterministic canonical edge ID.
    Symmetric relationships canonicalize endpoint ordering to prevent duplicate reverse edges.
    """
    if not is_directional:
        s, t = sorted([source_node_id, target_node_id])
    else:
        s, t = source_node_id, target_node_id

    raw_key = f"{s}:{edge_type.value}:{t}:{discriminator.strip()}"
    digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:12]
    s_short = s.split("-")[-1][:8]
    t_short = t.split("-")[-1][:8]
    return f"EDGE-{s_short}-{edge_type.value[:8]}-{t_short}-{digest}"


class EdgeRegistry:
    """
    In-memory canonical storage and adjacency indexing for knowledge graph edges.
    Supports contradiction preservation, symmetric canonicalization, and deterministic ordering.
    """

    def __init__(self) -> None:
        self._edges: Dict[str, GraphEdge] = {}
        # Key: (canonical_src, canonical_tgt, edge_type_str) -> edge_id
        self._lookup_key_index: Dict[Tuple[str, str, str], str] = {}
        self._outbound: Dict[str, Set[str]] = defaultdict(set)
        self._inbound: Dict[str, Set[str]] = defaultdict(set)
        self._type_index: Dict[EdgeType, Set[str]] = {t: set() for t in EdgeType}

    def _canonical_endpoints(self, source_id: str, target_id: str, is_directional: bool) -> Tuple[str, str]:
        if not is_directional:
            s, t = sorted([source_id, target_id])
            return s, t
        return source_id, target_id

    def add_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        edge_type: EdgeType,
        strength: float = 1.0,
        confidence: float = 1.0,
        epistemic_status: EpistemicStatus = EpistemicStatus.OBSERVED,
        valid_from: Optional[datetime] = None,
        valid_to: Optional[datetime] = None,
        first_observed_at: Optional[datetime] = None,
        last_observed_at: Optional[datetime] = None,
        evidence_ids: Optional[List[str]] = None,
        supporting_sources: Optional[List[str]] = None,
        contradicting_evidence_ids: Optional[List[str]] = None,
        attributes: Optional[Dict] = None,
        provenance: Optional[List[ProvenanceItem]] = None,
        is_directional: bool = True,
        discriminator: str = "",
    ) -> GraphEdge:
        """
        Adds or idempotently merges an edge.
        If relationship already exists, merges supporting evidence and contradictions.
        """
        s, t = self._canonical_endpoints(source_node_id, target_node_id, is_directional)
        lookup_key = (s, t, edge_type.value)

        evidence_ids = evidence_ids or []
        supporting_sources = supporting_sources or []
        contradicting_evidence_ids = contradicting_evidence_ids or []
        attributes = attributes or {}
        provenance = provenance or []

        if lookup_key in self._lookup_key_index:
            edge_id = self._lookup_key_index[lookup_key]
            existing = self._edges[edge_id]

            # Merge evidence IDs
            merged_evidence = sorted(list(set(existing.evidence_ids).union(set(evidence_ids))))
            merged_sources = sorted(list(set(existing.supporting_sources).union(set(supporting_sources))))
            merged_contradictions = sorted(list(set(existing.contradicting_evidence_ids).union(set(contradicting_evidence_ids))))

            # Merge provenance
            existing_prov_ids = {p.evidence_id for p in existing.provenance}
            merged_provenance = list(existing.provenance)
            for p in provenance:
                if p.evidence_id not in existing_prov_ids:
                    merged_provenance.append(p)
                    existing_prov_ids.add(p.evidence_id)
            merged_provenance.sort(key=lambda x: x.evidence_id)

            # Temporal boundaries
            obs_dates = [d for d in [existing.first_observed_at, existing.last_observed_at, first_observed_at, last_observed_at] if d is not None]
            new_first = min(obs_dates) if obs_dates else None
            new_last = max(obs_dates) if obs_dates else None

            # Validity
            v_from = min(existing.valid_from, valid_from) if existing.valid_from and valid_from else (existing.valid_from or valid_from)
            v_to = max(existing.valid_to, valid_to) if existing.valid_to and valid_to else (existing.valid_to or valid_to)

            merged_attrs = dict(existing.attributes)
            merged_attrs.update(attributes)

            # If contradictions are introduced, mark epistemic_status accordingly
            new_status = existing.epistemic_status
            if merged_contradictions and existing.epistemic_status != EpistemicStatus.UNCERTAIN:
                new_status = EpistemicStatus.UNCERTAIN

            updated_edge = GraphEdge(
                edge_id=edge_id,
                source_node_id=existing.source_node_id,
                target_node_id=existing.target_node_id,
                edge_type=edge_type,
                strength=max(existing.strength, strength),
                confidence=max(existing.confidence, confidence),
                epistemic_status=new_status,
                valid_from=v_from,
                valid_to=v_to,
                first_observed_at=new_first,
                last_observed_at=new_last,
                evidence_ids=merged_evidence,
                supporting_sources=merged_sources,
                contradicting_evidence_ids=merged_contradictions,
                attributes=merged_attrs,
                provenance=merged_provenance,
                is_directional=is_directional,
            )
            self._edges[edge_id] = updated_edge
            return updated_edge

        # New edge
        edge_id = generate_edge_id(s, t, edge_type, is_directional, discriminator)
        new_edge = GraphEdge(
            edge_id=edge_id,
            source_node_id=s if not is_directional else source_node_id,
            target_node_id=t if not is_directional else target_node_id,
            edge_type=edge_type,
            strength=max(0.0, min(1.0, strength)),
            confidence=max(0.0, min(1.0, confidence)),
            epistemic_status=EpistemicStatus.UNCERTAIN if contradicting_evidence_ids else epistemic_status,
            valid_from=valid_from,
            valid_to=valid_to,
            first_observed_at=first_observed_at,
            last_observed_at=last_observed_at,
            evidence_ids=sorted(list(set(evidence_ids))),
            supporting_sources=sorted(list(set(supporting_sources))),
            contradicting_evidence_ids=sorted(list(set(contradicting_evidence_ids))),
            attributes=attributes,
            provenance=sorted(provenance, key=lambda x: x.evidence_id),
            is_directional=is_directional,
        )

        self._edges[edge_id] = new_edge
        self._lookup_key_index[lookup_key] = edge_id
        self._type_index[edge_type].add(edge_id)

        # Index in adjacency
        src = new_edge.source_node_id
        tgt = new_edge.target_node_id
        self._outbound[src].add(edge_id)
        self._inbound[tgt].add(edge_id)

        if not is_directional:
            self._outbound[tgt].add(edge_id)
            self._inbound[src].add(edge_id)

        return new_edge

    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        """Retrieves an edge by canonical ID."""
        return self._edges.get(edge_id)

    def get_outbound_edges(self, node_id: str) -> List[GraphEdge]:
        """Retrieves outbound edges from node_id, sorted deterministically."""
        edge_ids = self._outbound.get(node_id, set())
        edges = [self._edges[eid] for eid in edge_ids if eid in self._edges]
        return self._sort_edges(edges)

    def get_inbound_edges(self, node_id: str) -> List[GraphEdge]:
        """Retrieves inbound edges to node_id, sorted deterministically."""
        edge_ids = self._inbound.get(node_id, set())
        edges = [self._edges[eid] for eid in edge_ids if eid in self._edges]
        return self._sort_edges(edges)

    def get_incident_edges(self, node_id: str) -> List[GraphEdge]:
        """Retrieves all incident edges (both in and out), deduplicated and sorted."""
        edge_ids = self._outbound.get(node_id, set()).union(self._inbound.get(node_id, set()))
        edges = [self._edges[eid] for eid in edge_ids if eid in self._edges]
        return self._sort_edges(edges)

    def get_edges_between(self, node_a: str, node_b: str) -> List[GraphEdge]:
        """Retrieves all edges between node_a and node_b in either direction."""
        incident_a = self._outbound.get(node_a, set()).union(self._inbound.get(node_a, set()))
        result = []
        for eid in incident_a:
            edge = self._edges.get(eid)
            if edge and ((edge.source_node_id == node_a and edge.target_node_id == node_b) or
                         (edge.source_node_id == node_b and edge.target_node_id == node_a)):
                result.append(edge)
        return self._sort_edges(result)

    def get_all_edges(self) -> List[GraphEdge]:
        """Returns all edges sorted deterministically."""
        return self._sort_edges(list(self._edges.values()))

    def get_edges_by_type(self, edge_type: EdgeType) -> List[GraphEdge]:
        """Returns all edges of specific type sorted deterministically."""
        edge_ids = self._type_index.get(edge_type, set())
        return self._sort_edges([self._edges[eid] for eid in edge_ids if eid in self._edges])

    def get_active_edges(self, as_of: datetime) -> List[GraphEdge]:
        """
        Returns all edges temporally active at the specified timestamp.
        valid_from <= as_of <= valid_to.
        """
        active = []
        for edge in self._edges.values():
            if edge.valid_from and edge.valid_from > as_of:
                continue
            if edge.valid_to and edge.valid_to < as_of:
                continue
            active.append(edge)
        return self._sort_edges(active)

    def _sort_edges(self, edges: List[GraphEdge]) -> List[GraphEdge]:
        """Canonical deterministic sort ordering for edges."""
        return sorted(edges, key=lambda e: (e.source_node_id, e.edge_type.value, e.target_node_id, e.edge_id))

    def count(self) -> int:
        """Returns total registered edges."""
        return len(self._edges)

    def clear(self) -> None:
        """Resets the registry."""
        self._edges.clear()
        self._lookup_key_index.clear()
        self._outbound.clear()
        self._inbound.clear()
        for t in self._type_index:
            self._type_index[t].clear()
