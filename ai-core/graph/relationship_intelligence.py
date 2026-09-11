"""
Phase 8 Relationship Intelligence Engine for NETRA.
Calculates multi-factor relationship scores, assigns lifecycle status, and produces explainable attribution.
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from config import NetraConfig, default_config
from models.knowledge_graph import (
    EdgeType,
    GraphEdge,
    NodeType,
    RelationshipDetail,
    RelationshipStatus,
)
from graph.node_registry import NodeRegistry
from graph.edge_registry import EdgeRegistry


class RelationshipIntelligenceEngine:
    """
    Evaluates entity-to-entity relationships with explicit configuration weights,
    contradiction penalties, lifecycle status tracking, and explainability.
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

    def evaluate_relationship(
        self,
        source_entity_id: str,
        target_entity_id: str,
        as_of: Optional[datetime] = None,
    ) -> Optional[RelationshipDetail]:
        """
        Evaluates the relationship between two entities.
        """
        evaluation_time = as_of or datetime.now(timezone.utc)

        node_a = self.node_registry.get_node_by_reference(source_entity_id)
        node_b = self.node_registry.get_node_by_reference(target_entity_id)
        if not node_a or not node_b:
            return None

        # Look up incident edges between these two entities
        edges = self.edge_registry.get_edges_between(node_a.node_id, node_b.node_id)
        if not edges:
            return None

        # Aggregate evidence across edges connecting A and B
        all_evidence_ids = set()
        all_sources = set()
        all_contradictions = set()
        edge_strengths = []
        edge_confidences = []
        first_seen = None
        last_seen = None

        dominant_type = "ASSOCIATED_WITH"
        active_edges = []
        for e in edges:
            if e.valid_from and e.valid_from > evaluation_time:
                continue
            if e.first_observed_at and e.first_observed_at > evaluation_time:
                continue
            active_edges.append(e)
            all_evidence_ids.update(e.evidence_ids)
            all_sources.update(e.supporting_sources)
            all_contradictions.update(e.contradicting_evidence_ids)
            edge_strengths.append(e.strength)
            edge_confidences.append(e.confidence)

            if e.first_observed_at:
                first_seen = min(first_seen, e.first_observed_at) if first_seen else e.first_observed_at
            if e.last_observed_at:
                last_seen = max(last_seen, e.last_observed_at) if last_seen else e.last_observed_at
            dominant_type = e.edge_type.value

        if not active_edges:
            return None

        first_seen = first_seen or node_a.created_at
        effective_last_seen = min(last_seen or evaluation_time, evaluation_time)

        obs_count = max(1, len(all_evidence_ids))
        indep_sources = max(1, len(all_sources))
        contradiction_count = len(all_contradictions)

        # 1. Correlation Strength
        s_corr = sum(edge_strengths) / len(edge_strengths) if edge_strengths else 0.5

        # 2. Temporal Persistence
        persistence_duration = max(0.0, (effective_last_seen - first_seen).total_seconds())
        min_persist = self.config.relationship_intelligence.persistent_min_duration_seconds
        s_persist = min(1.0, persistence_duration / max(1.0, min_persist * 2.0))

        # 3. Repetition
        s_rep = min(1.0, obs_count / 5.0)

        # 4. Source Independence
        s_indep = min(1.0, indep_sources / 3.0)

        # 5. Evidence Quality
        s_quality = sum(edge_confidences) / len(edge_confidences) if edge_confidences else 0.5

        # 6. Recency
        inactivity_sec = max(0.0, (evaluation_time - effective_last_seen).total_seconds())
        stale_sec = self.config.relationship_intelligence.stale_threshold_seconds
        s_recency = max(0.0, 1.0 - (inactivity_sec / stale_sec))

        # Weighted calculation
        weights = self.config.relationship_intelligence.weights
        raw_score = (
            weights.correlation_strength * s_corr
            + weights.persistence * s_persist
            + weights.repetition * s_rep
            + weights.source_independence * s_indep
            + weights.evidence_quality * s_quality
            + weights.recency * s_recency
        )

        # Contradiction penalty
        penalty = 0.0
        if contradiction_count > 0:
            penalty = min(
                self.config.relationship_intelligence.contradiction_penalty_factor,
                contradiction_count * 0.15,
            )

        final_strength = round(max(0.0, min(1.0, raw_score - penalty)), 4)
        final_confidence = round(max(0.0, min(1.0, s_quality * (1.0 - (0.5 * penalty)))), 4)

        # Determine Lifecycle Status
        status = self._determine_status(
            final_strength=final_strength,
            persistence_duration=persistence_duration,
            inactivity_sec=inactivity_sec,
            obs_count=obs_count,
            contradiction_count=contradiction_count,
            evaluation_time=evaluation_time,
            valid_to=edges[0].valid_to,
        )

        # Explainability "Why"
        why_points = self._generate_why(
            s_corr=s_corr,
            obs_count=obs_count,
            indep_sources=indep_sources,
            persistence_duration=persistence_duration,
            inactivity_sec=inactivity_sec,
            contradiction_count=contradiction_count,
            status=status,
        )

        rel_id = f"REL-{source_entity_id}-{target_entity_id}"
        return RelationshipDetail(
            relationship_id=rel_id,
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relationship_type=dominant_type,
            strength=final_strength,
            confidence=final_confidence,
            first_seen=first_seen,
            last_seen=last_seen,
            observation_count=obs_count,
            supporting_event_count=obs_count,
            independent_source_count=indep_sources,
            supporting_evidence=sorted(list(all_evidence_ids)),
            contradicting_evidence=sorted(list(all_contradictions)),
            temporal_persistence_seconds=persistence_duration,
            recency_score=round(s_recency, 4),
            status=status,
            why=why_points,
            is_disputed=contradiction_count > 0,
        )

    def evaluate_all_relationships(self, as_of: Optional[datetime] = None) -> List[RelationshipDetail]:
        """Evaluates all entity-to-entity relationships in the graph."""
        evaluation_time = as_of or datetime.now(timezone.utc)
        entity_nodes = self.node_registry.get_nodes_by_type(NodeType.ENTITY)
        evaluated_pairs = set()
        details = []

        for i, na in enumerate(entity_nodes):
            for nb in entity_nodes[i + 1:]:
                pair_key = tuple(sorted([na.label, nb.label]))
                if pair_key in evaluated_pairs:
                    continue
                detail = self.evaluate_relationship(na.label, nb.label, as_of=evaluation_time)
                if detail:
                    details.append(detail)
                    evaluated_pairs.add(pair_key)

        return sorted(details, key=lambda r: (r.source_entity_id, r.target_entity_id))

    def _determine_status(
        self,
        final_strength: float,
        persistence_duration: float,
        inactivity_sec: float,
        obs_count: int,
        contradiction_count: int,
        evaluation_time: datetime,
        valid_to: Optional[datetime],
    ) -> RelationshipStatus:
        if valid_to and valid_to < evaluation_time:
            return RelationshipStatus.ENDED
        if contradiction_count > 0:
            return RelationshipStatus.DISPUTED
        if inactivity_sec > self.config.relationship_intelligence.stale_threshold_seconds:
            return RelationshipStatus.STALE
        if (
            persistence_duration >= self.config.relationship_intelligence.persistent_min_duration_seconds
            and obs_count >= self.config.relationship_intelligence.persistent_min_windows
        ):
            return RelationshipStatus.PERSISTENT
        if final_strength >= self.config.relationship_intelligence.active_threshold:
            return RelationshipStatus.ACTIVE
        if obs_count <= 1:
            return RelationshipStatus.NEW
        return RelationshipStatus.WEAKENING

    def _generate_why(
        self,
        s_corr: float,
        obs_count: int,
        indep_sources: int,
        persistence_duration: float,
        inactivity_sec: float,
        contradiction_count: int,
        status: RelationshipStatus,
    ) -> List[str]:
        points = []
        if obs_count > 0:
            points.append(f"{obs_count} supporting observation(s) recorded")
        if indep_sources > 1:
            points.append(f"Corroborated by {indep_sources} independent sensor feeds")
        if persistence_duration >= 3600.0:
            hours = persistence_duration / 3600.0
            points.append(f"Association persisted across {hours:.1f} hours")
        if contradiction_count > 0:
            points.append(f"Disputed by {contradiction_count} conflicting telemetry report(s)")
        if status == RelationshipStatus.STALE:
            hours_inactive = inactivity_sec / 3600.0
            points.append(f"No recent telemetry for {hours_inactive:.1f} hours (classified STALE)")
        return points
