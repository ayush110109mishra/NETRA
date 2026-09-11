"""
Master Entity Intelligence Orchestrator for NETRA.
Coordinates repository retrieval, profile aggregation, behavioral baseline computation,
change detection, anomaly assessment, risk and confidence calculations, relational graphs,
chronological timelines, and four-tier intelligence assessments for Focus Mode.
"""

import time
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from config import NetraConfig, default_config
from models.common import EntityStatus, RiskLevel
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import (
    CanonicalEntity,
    EntityProfile,
    EntityBehaviorProfile,
    BehavioralChangeReport,
    EntityAnomalyAssessment,
    EntityRiskProfile,
    EntityConfidenceProfile,
    EntityRelationshipEdge,
    EntityClusterMembership,
    EntityPatternOccurrence,
    EntityTimelineItem,
    EntityMapContext,
    FourTierAssessment,
    EntityIntelligenceResponse,
    EntityCompareRequest,
    EntityCompareResponse,
    EntityCompareItem,
    EntitySearchResponse,
)
from entities.repository import EntityRepository
from entities.profile import EntityProfileAggregator
from entities.baseline import BehavioralBaselineEngine
from entities.change_detection import BehavioralChangeDetector
from entities.anomaly import EntityAnomalyEngine
from entities.risk import EntityRiskEngine
from entities.confidence import EntityConfidenceEngine
from entities.timeline import EntityTimelineBuilder
from entities.network import EntityNetworkBuilder
from entities.assessment import EntityAssessmentGenerator
from events.clustering import EventClusterer
from events.patterns import PatternDetector
from events.correlation import MultiDimensionalCorrelator


class EntityIntelligenceEngine:
    """Master engine for Entity-Centric Intelligence and Focus Mode."""

    def __init__(
        self,
        config: Optional[NetraConfig] = None,
        repository: Optional[EntityRepository] = None,
    ):
        self.cfg = config or default_config
        self.repository = repository or EntityRepository(self.cfg.entity)
        self.profile_aggregator = EntityProfileAggregator()
        self.baseline_engine = BehavioralBaselineEngine(self.cfg.entity)
        self.change_detector = BehavioralChangeDetector(self.cfg.entity)
        self.anomaly_engine = EntityAnomalyEngine()
        self.risk_engine = EntityRiskEngine(self.cfg)
        self.confidence_engine = EntityConfidenceEngine(self.cfg)
        self.timeline_builder = EntityTimelineBuilder()
        self.network_builder = EntityNetworkBuilder()
        self.assessment_generator = EntityAssessmentGenerator()

        # Phase 2 sub-engines for cluster and pattern context
        self.correlator = MultiDimensionalCorrelator(self.cfg)
        self.clusterer = EventClusterer(self.cfg)
        self.pattern_detector = PatternDetector(self.cfg)

    def analyze_entity(
        self,
        entity_id: str,
        as_of: Optional[datetime] = None,
    ) -> EntityIntelligenceResponse:
        """
        Execute full Entity Intelligence pipeline for Focus Mode.
        Produces complete context required for Ayush's frontend in a single deterministic call.
        """
        start_time = time.perf_counter()

        # Step 1: Retrieve canonical entity and its events
        entity = self.repository.get_entity(entity_id, as_of=as_of)
        if not entity:
            raise ValueError(f"Entity '{entity_id}' not found in repository.")

        events = self.repository.get_events_for_entity(entity_id)
        all_events = self.repository.get_all_events()

        # Step 2: Compute Phase 2 Clusters and Patterns for relational context
        clusters = []
        patterns = []
        if len(all_events) >= 2:
            correlations = self.correlator.correlate_all(all_events)
            clusters = self.clusterer.cluster_events(all_events, correlations)
            patterns = self.pattern_detector.detect_patterns(all_events)

        # Entity-specific cluster memberships
        cluster_memberships = self.network_builder.extract_cluster_memberships(entity_id, clusters)

        # Entity-specific pattern occurrences
        pattern_occurrences: List[EntityPatternOccurrence] = []
        for p in patterns:
            p_event_ids = getattr(p, "event_ids", getattr(p, "evidence_event_ids", []))
            # Check if any event in pattern belongs to this entity
            if any(e_id in [e.event_id for e in events] for e_id in p_event_ids):
                pattern_occurrences.append(
                    EntityPatternOccurrence(
                        pattern_type=p.pattern_type,
                        occurrences=len(p_event_ids),
                        confidence=p.confidence,
                    )
                )

        # Step 3: Relational Graph Edges
        relationships = self.network_builder.build_relationships(
            target_entity_id=entity_id,
            all_events=all_events,
            clusters=clusters,
            spatial_threshold_km=self.cfg.spatial_proximity_km_threshold,
            temporal_threshold_seconds=self.cfg.temporal_proximity_seconds_threshold,
        )

        # Step 4: High-Level Profile Aggregation
        profile = self.profile_aggregator.aggregate(
            entity=entity,
            events=events,
            associated_entities_count=len(relationships),
            associated_clusters_count=len(cluster_memberships),
        )

        # Step 5: Behavioral Baseline
        behavior = self.baseline_engine.compute_baseline(entity, events)

        # Step 6: Behavioral Change Detection
        changes = self.change_detector.detect_changes(entity, behavior, events)

        # Step 7: Anomaly Assessment
        sorted_events = sorted(events, key=lambda x: x.timestamp)
        latest_time = sorted_events[-1].timestamp if sorted_events else entity.last_observed
        recent_window_hours = self.cfg.entity.recent_analysis_window_hours
        recent_events = [
            e for e in sorted_events
            if (latest_time - e.timestamp).total_seconds() <= recent_window_hours * 3600.0
        ]
        if not recent_events and sorted_events:
            recent_events = [sorted_events[-1]]

        anomalies = self.anomaly_engine.assess_anomaly(entity, behavior, changes, recent_events)

        # Step 8: Risk Profile
        risk = self.risk_engine.compute_risk(entity, events, changes, anomalies, cluster_memberships)

        # Step 9: Confidence Profile (with Cold-Start gate & Contradiction penalties)
        confidence = self.confidence_engine.compute_confidence(entity, events, behavior)

        # Step 10: Chronological Timeline
        timeline = self.timeline_builder.build_timeline(events)

        # Step 11: Map Context (30% view)
        observed_coords = [e.location for e in events]
        associated_locations = []
        for rel in relationships[:5]:  # Top 5 related entities
            other_entity = self.repository.get_entity(rel.entity_id, as_of=as_of)
            if other_entity and other_entity.attributes.get("location"):
                associated_locations.append({
                    "entity_id": rel.entity_id,
                    "location": other_entity.attributes["location"],
                    "relationship_type": rel.relationship_type.value,
                })
            else:
                other_events = self.repository.get_events_for_entity(rel.entity_id)
                if other_events:
                    associated_locations.append({
                        "entity_id": rel.entity_id,
                        "location": other_events[-1].location.model_dump(),
                        "relationship_type": rel.relationship_type.value,
                    })

        map_context = EntityMapContext(
            centroid=behavior.spatial.centroid,
            bounding_radius_km=behavior.spatial.bounding_radius_km,
            observed_coordinates=observed_coords,
            associated_entity_locations=associated_locations,
        )

        # Step 12: Four-Tier Assessment
        assessment = self.assessment_generator.generate(
            entity=entity,
            profile=profile,
            behavior=behavior,
            changes=changes,
            anomalies=anomalies,
            risk=risk,
            confidence=confidence,
            relationships=relationships,
            clusters=cluster_memberships,
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 3)

        return EntityIntelligenceResponse(
            entity=entity,
            profile=profile,
            behavior=behavior,
            changes=changes,
            anomalies=anomalies,
            risk=risk,
            confidence=confidence,
            relationships=relationships,
            clusters=cluster_memberships,
            patterns=pattern_occurrences,
            timeline=timeline,
            map_context=map_context,
            assessment=assessment,
            metadata={
                "processing_time_ms": elapsed_ms,
                "data_classification": self.cfg.data_classification,
                "engine_version": self.cfg.version,
                "mode": self.cfg.mode,
            },
        )

    def compare_entities(
        self,
        request: EntityCompareRequest,
        as_of: Optional[datetime] = None,
    ) -> EntityCompareResponse:
        """Execute side-by-side comparative analysis across multiple entities."""
        items: List[EntityCompareItem] = []

        for entity_id in request.entity_ids:
            res = self.analyze_entity(entity_id, as_of=as_of)
            items.append(
                EntityCompareItem(
                    entity_id=res.entity.entity_id,
                    entity_type=res.entity.entity_type,
                    status=res.entity.status,
                    event_count=res.entity.event_count,
                    event_frequency_per_day=res.behavior.event_frequency_per_day,
                    average_activity=res.behavior.average_activity,
                    average_speed=res.behavior.average_speed,
                    dominant_event_type=res.profile.dominant_event_type,
                    anomaly_score=res.anomalies.score,
                    risk_score=res.risk.score,
                    confidence_score=res.confidence.score,
                )
            )

        # Deterministic summary of comparison
        highest_risk = max(items, key=lambda x: x.risk_score)
        highest_anomaly = max(items, key=lambda x: x.anomaly_score)
        summary = (
            f"Compared {len(items)} synthetic entities. "
            f"Highest risk: {highest_risk.entity_id} ({highest_risk.risk_score:.2f}). "
            f"Highest anomaly: {highest_anomaly.entity_id} ({highest_anomaly.anomaly_score:.2f})."
        )

        return EntityCompareResponse(
            entities=items,
            comparison_summary=summary,
            metadata={
                "comparison_count": len(items),
                "data_classification": self.cfg.data_classification,
                "engine_version": self.cfg.version,
            },
        )

    def search_entities(
        self,
        query: Optional[str] = None,
        entity_type: Optional[str] = None,
        status: Optional[EntityStatus] = None,
        as_of: Optional[datetime] = None,
    ) -> EntitySearchResponse:
        """Search and filter known canonical entities."""
        all_entities = self.repository.list_entities(as_of=as_of)
        filtered = list(all_entities)

        if query:
            q = query.strip().lower()
            filtered = [
                e for e in filtered
                if q in e.entity_id.lower() or (e.callsign and q in e.callsign.lower())
            ]

        if entity_type:
            et = entity_type.strip().lower()
            filtered = [e for e in filtered if e.entity_type.lower() == et]

        if status:
            filtered = [e for e in filtered if e.status == status]

        return EntitySearchResponse(
            total_count=len(filtered),
            entities=filtered,
            metadata={
                "data_classification": self.cfg.data_classification,
                "engine_version": self.cfg.version,
            },
        )
