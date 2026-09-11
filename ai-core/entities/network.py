"""
Entity Network and Relationship Builder for NETRA Entity Intelligence.
Identifies evidence-backed relationships between entities including co-occurrence,
repeated association, shared cluster membership, and spatio-temporal proximity.
"""

from typing import List, Dict, Tuple, Optional
from models.common import RelationshipType
from models.geo import haversine_distance_km
from models.event_intelligence import CanonicalEvent, EventCluster
from models.entity_intelligence import (
    EntityRelationshipEdge,
    EntityClusterMembership,
)


class EntityNetworkBuilder:
    """Builds relational network edges and cluster memberships for an entity."""

    @staticmethod
    def build_relationships(
        target_entity_id: str,
        all_events: List[CanonicalEvent],
        clusters: Optional[List[EventCluster]] = None,
        spatial_threshold_km: float = 15.0,
        temporal_threshold_seconds: float = 3600.0,
    ) -> List[EntityRelationshipEdge]:
        """Detect deterministic relational edges for the target entity."""
        clusters = clusters or []
        # other_entity_id -> Dict of relationship details
        relationships: Dict[str, Dict] = {}

        # 1. Direct Event Co-Occurrence / Shared Event
        target_events = [e for e in all_events if target_entity_id in e.entity_ids]
        target_event_ids = {e.event_id for e in target_events}

        for e in target_events:
            for other_id in e.entity_ids:
                if other_id == target_entity_id:
                    continue

                if other_id not in relationships:
                    relationships[other_id] = {
                        "type": RelationshipType.CO_OCCURRENCE,
                        "co_occurrences": 0,
                        "evidence_ids": set(),
                        "score": 0.50,
                        "confidence": 0.60,
                    }

                rel = relationships[other_id]
                rel["co_occurrences"] += 1
                rel["evidence_ids"].add(e.event_id)

                if rel["co_occurrences"] >= 2:
                    rel["type"] = RelationshipType.REPEATED_ASSOCIATION
                    rel["score"] = min(1.0, round(0.50 + rel["co_occurrences"] * 0.15, 2))
                    rel["confidence"] = min(1.0, round(0.60 + rel["co_occurrences"] * 0.10, 2))
                else:
                    rel["type"] = RelationshipType.SHARED_EVENT
                    rel["score"] = 0.55
                    rel["confidence"] = 0.65

        # 2. Shared Cluster Membership
        for c in clusters:
            cluster_entities = getattr(c, "unique_entities", getattr(c, "entity_ids", []))
            if cluster_entities and target_entity_id in cluster_entities:
                c_cohesion = getattr(c, "cohesion_score", getattr(c, "cohesion", 0.85))
                c_conf = getattr(c, "average_confidence", getattr(c, "confidence", 0.85))
                for other_id in cluster_entities:
                    if other_id == target_entity_id:
                        continue

                    cluster_score = round(min(1.0, c_cohesion * 0.85), 2)
                    cluster_conf = round(min(1.0, c_conf * 0.90), 2)

                    if other_id not in relationships:
                        relationships[other_id] = {
                            "type": RelationshipType.SHARED_CLUSTER,
                            "co_occurrences": 1,
                            "evidence_ids": set(c.event_ids),
                            "score": cluster_score,
                            "confidence": cluster_conf,
                        }
                    else:
                        rel = relationships[other_id]
                        rel["evidence_ids"].update(c.event_ids)
                        rel["score"] = max(rel["score"], cluster_score)
                        rel["confidence"] = max(rel["confidence"], cluster_conf)

        # 3. Spatio-Temporal Proximity Check
        other_events = [e for e in all_events if target_entity_id not in e.entity_ids]
        for te in target_events:
            for oe in other_events:
                time_diff = abs((te.timestamp - oe.timestamp).total_seconds())
                if time_diff <= temporal_threshold_seconds:
                    dist = haversine_distance_km(te.location, oe.location)
                    if dist <= spatial_threshold_km:
                        for other_id in oe.entity_ids:
                            if other_id == target_entity_id:
                                continue

                            prox_score = round(max(0.45, 0.90 - (dist / spatial_threshold_km) * 0.40), 2)
                            prox_conf = round(max(0.50, 0.80 - (time_diff / temporal_threshold_seconds) * 0.25), 2)

                            if other_id not in relationships:
                                relationships[other_id] = {
                                    "type": RelationshipType.SPATIAL_ASSOCIATION,
                                    "co_occurrences": 1,
                                    "evidence_ids": {te.event_id, oe.event_id},
                                    "score": prox_score,
                                    "confidence": prox_conf,
                                }
                            else:
                                rel = relationships[other_id]
                                rel["evidence_ids"].add(te.event_id)
                                rel["evidence_ids"].add(oe.event_id)
                                rel["score"] = max(rel["score"], prox_score)

        # Convert to sorted List[EntityRelationshipEdge]
        edges: List[EntityRelationshipEdge] = []
        for other_id, data in relationships.items():
            edges.append(
                EntityRelationshipEdge(
                    entity_id=other_id,
                    relationship_type=data["type"],
                    score=data["score"],
                    confidence=data["confidence"],
                    co_occurrence_count=data["co_occurrences"],
                    evidence_event_ids=sorted(list(data["evidence_ids"])),
                )
            )

        # Deterministic sort: score descending, entity_id ascending
        edges.sort(key=lambda x: (-x.score, x.entity_id))
        return edges

    @staticmethod
    def extract_cluster_memberships(
        target_entity_id: str,
        clusters: List[EventCluster],
    ) -> List[EntityClusterMembership]:
        """Filter clusters in which the target entity participated."""
        memberships: List[EntityClusterMembership] = []
        for c in clusters:
            cluster_entities = getattr(c, "unique_entities", getattr(c, "entity_ids", []))
            if cluster_entities and target_entity_id in cluster_entities:
                c_cohesion = getattr(c, "cohesion_score", getattr(c, "cohesion", 0.85))
                c_conf = getattr(c, "average_confidence", getattr(c, "confidence", 0.85))
                memberships.append(
                    EntityClusterMembership(
                        cluster_id=c.cluster_id,
                        event_count=c.event_count,
                        cohesion=c_cohesion,
                        confidence=c_conf,
                    )
                )

        memberships.sort(key=lambda x: (-x.cohesion, x.cluster_id))
        return memberships
