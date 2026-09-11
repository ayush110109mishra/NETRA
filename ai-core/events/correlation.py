"""
Multi-Dimensional Event Correlation Engine for NETRA Intelligence Core.
Combines temporal, spatial, entity overlap, taxonomy similarity, and attribute telemetry
into an evidence-backed correlation score.
Strictly distinguishes correlation from causation and enforces false-correlation safeguards.
"""

from typing import List, Dict, Tuple, Optional, Any
from config import NetraConfig, default_config
from models.common import RelationshipType, RelationshipStrength
from models.event_intelligence import (
    CanonicalEvent,
    CorrelationComponents,
    EventCorrelation,
)
from events.temporal import TemporalIntelligence
from events.spatial import SpatialIntelligence

# Event type compatibility matrix
TYPE_COMPATIBILITY_MATRIX: Dict[Tuple[str, str], float] = {
    ("MOVEMENT", "PATROL_DEVIATION"): 0.75,
    ("MOVEMENT", "SUPPLY_CONVOY"): 0.70,
    ("MOVEMENT", "PERIMETER_PROXIMITY"): 0.65,
    ("PATROL_DEVIATION", "PERIMETER_PROXIMITY"): 0.80,
    ("PATROL_DEVIATION", "RADAR_ANOMALY"): 0.75,
    ("RADAR_ANOMALY", "PERIMETER_PROXIMITY"): 0.80,
    ("SENSOR_PING", "COMMUNICATION"): 0.65,
    ("SENSOR_PING", "MOVEMENT"): 0.55,
}


class MultiDimensionalCorrelator:
    """Computes multi-dimensional event correlations with explainable reasoning."""

    def __init__(self, config: Optional[NetraConfig] = None):
        self.cfg = config or default_config
        self.temporal_intel = TemporalIntelligence(self.cfg)
        self.spatial_intel = SpatialIntelligence(self.cfg)

    def calculate_type_similarity(self, type1: str, type2: str) -> float:
        """Evaluate taxonomy compatibility score [0.0 - 1.0]."""
        t1, t2 = type1.upper(), type2.upper()
        if t1 == t2:
            return 1.0
        if (t1, t2) in TYPE_COMPATIBILITY_MATRIX:
            return TYPE_COMPATIBILITY_MATRIX[(t1, t2)]
        if (t2, t1) in TYPE_COMPATIBILITY_MATRIX:
            return TYPE_COMPATIBILITY_MATRIX[(t2, t1)]
        return 0.20

    def calculate_entity_similarity(self, e1_entities: List[str], e2_entities: List[str]) -> Tuple[float, Optional[RelationshipType]]:
        """Evaluate entity overlap using Jaccard index."""
        s1, s2 = set(e1_entities), set(e2_entities)
        if not s1 or not s2:
            return 0.0, None

        intersection = s1.intersection(s2)
        union = s1.union(s2)

        jaccard = len(intersection) / len(union)
        if jaccard == 1.0:
            return 1.0, RelationshipType.SAME_ENTITY
        elif jaccard > 0.0:
            return round(jaccard, 2), RelationshipType.PARTIAL_ENTITY_OVERLAP
        return 0.0, None

    def calculate_attribute_similarity(self, attr1: Dict[str, Any], attr2: Dict[str, Any]) -> float:
        """Evaluate telemetry attribute similarity (speed, activity_level)."""
        if not attr1 and not attr2:
            return 0.0

        spd1 = float(attr1.get("speed", 0.0))
        spd2 = float(attr2.get("speed", 0.0))
        act1 = float(attr1.get("activity_level", 0.5))
        act2 = float(attr2.get("activity_level", 0.5))

        speed_delta = abs(spd1 - spd2)
        speed_sim = max(0.0, 1.0 - (speed_delta / max(30.0, max(spd1, spd2))))

        act_delta = abs(act1 - act2)
        act_sim = max(0.0, 1.0 - act_delta)

        return round(0.5 * speed_sim + 0.5 * act_sim, 4)

    def map_strength(self, score: float) -> RelationshipStrength:
        """Map aggregate score to categorical relationship strength band."""
        bands = self.cfg.relationship_strength
        if score <= bands.very_weak_max:
            return RelationshipStrength.VERY_WEAK
        elif score <= bands.weak_max:
            return RelationshipStrength.WEAK
        elif score <= bands.moderate_max:
            return RelationshipStrength.MODERATE
        elif score <= bands.strong_max:
            return RelationshipStrength.STRONG
        else:
            return RelationshipStrength.VERY_STRONG

    def correlate_pair(self, e1: CanonicalEvent, e2: CanonicalEvent) -> EventCorrelation:
        """
        Compute complete multi-dimensional correlation between two canonical events.
        Enforces Section 24 False-Correlation safeguards.
        """
        weights = self.cfg.correlation_weights

        # 1. Temporal Component
        time_delta, s_temporal, c_temporal = self.temporal_intel.calculate_temporal_score(
            e1.timestamp, e2.timestamp
        )

        # 2. Spatial Component
        dist_km, s_spatial, c_spatial = self.spatial_intel.calculate_spatial_score(
            e1.location, e2.location
        )

        # 3. Entity Component
        s_entity, entity_rel = self.calculate_entity_similarity(e1.entity_ids, e2.entity_ids)

        # 4. Type Similarity Component
        s_type = self.calculate_type_similarity(e1.event_type, e2.event_type)

        # 5. Attribute Telemetry Component
        s_attr = self.calculate_attribute_similarity(e1.attributes, e2.attributes)

        # --- SECTION 24 FALSE-CORRELATION SAFEGUARDS ---
        # Safeguard A: Type similarity alone across distant time, space, and disjoint entities
        # MUST remain strictly VERY_WEAK (<= 0.24).
        if s_spatial == 0.0 and s_temporal == 0.0 and s_entity == 0.0:
            s_type = min(0.20, s_type * 0.20)
            s_attr = 0.0

        # Safeguard B: Same location BUT distant in time (> window, s_temporal == 0) and different entities.
        # Spatial coincidence across distinct times without entity overlap is heavily discounted.
        if s_temporal == 0.0 and s_entity == 0.0:
            s_spatial = s_spatial * 0.65
            s_attr = s_attr * 0.25

        # Safeguard C: Same time BUT distant in space (> window, s_spatial == 0) and different entities.
        # Temporal coincidence on opposite ends of a theater without entity overlap is heavily discounted.
        if s_spatial == 0.0 and s_entity == 0.0:
            s_temporal = s_temporal * 0.45
            s_attr = s_attr * 0.25

        # Composite Correlation Score
        raw_score = (
            (weights.temporal * s_temporal)
            + (weights.spatial * s_spatial)
            + (weights.entity * s_entity)
            + (weights.type_similarity * s_type)
            + (weights.attribute_similarity * s_attr)
        )
        correlation_score = round(min(1.0, max(0.0, raw_score)), 4)
        strength = self.map_strength(correlation_score)

        # Detect specific qualitative relationships
        relationships: List[RelationshipType] = []
        if entity_rel:
            relationships.append(entity_rel)

        is_same_loc, _ = self.spatial_intel.is_same_location(e1.location, e2.location)
        if is_same_loc:
            relationships.append(RelationshipType.SAME_LOCATION)
        elif dist_km <= self.cfg.spatial.proximity_km:
            relationships.append(RelationshipType.SPATIAL_PROXIMITY)

        if time_delta <= self.cfg.temporal.proximity_window_seconds:
            relationships.append(RelationshipType.TEMPORAL_PROXIMITY)

        is_seq, _ = self.temporal_intel.is_sequential(e1, e2)
        if is_seq:
            relationships.append(RelationshipType.SEQUENTIAL)

        if s_type >= 0.70:
            relationships.append(RelationshipType.SIMILAR_TYPE)

        confidence = round(
            0.35 * max(0.5, c_temporal)
            + 0.35 * max(0.5, c_spatial)
            + 0.30 * (0.90 if s_entity > 0 else 0.70),
            2,
        )

        reasons = []
        if s_entity > 0:
            shared = set(e1.entity_ids).intersection(set(e2.entity_ids))
            reasons.append(f"Shared entity association ({', '.join(shared)})")
        if dist_km <= 0.20:
            reasons.append(f"Co-located within {dist_km:.2f} km")
        elif dist_km <= self.cfg.spatial.proximity_km:
            reasons.append(f"Spatial proximity of {dist_km:.1f} km")
        if time_delta <= 1800:
            reasons.append(f"Temporal proximity of {int(time_delta/60)} mins")
        if s_type >= 0.70:
            reasons.append(f"Compatible event categories ({e1.event_type} <-> {e2.event_type})")

        if not reasons:
            reasons.append("Weak independent background correlation")

        reasoning = "; ".join(reasons) + "."

        return EventCorrelation(
            source_event_id=e1.event_id,
            target_event_id=e2.event_id,
            correlation_score=correlation_score,
            strength=strength,
            components=CorrelationComponents(
                temporal=round(s_temporal, 4),
                spatial=round(s_spatial, 4),
                entity=round(s_entity, 4),
                type_similarity=round(s_type, 4),
                attribute_similarity=round(s_attr, 4),
            ),
            relationships=relationships,
            confidence=confidence,
            reasoning=reasoning,
        )

    def correlate_all(self, events: List[CanonicalEvent]) -> List[EventCorrelation]:
        """
        Compute pairwise correlations across candidate event pairs.
        Uses candidate filtering to prevent unnecessary calculations.
        """
        if len(events) < 2:
            return []

        correlations: List[EventCorrelation] = []
        n = len(events)

        for i in range(n):
            for j in range(i + 1, n):
                e1, e2 = events[i], events[j]
                time_delta = abs((e1.timestamp - e2.timestamp).total_seconds())
                shared_entities = set(e1.entity_ids).intersection(set(e2.entity_ids))
                if time_delta > (self.cfg.temporal.proximity_window_seconds * 2.0) and not shared_entities:
                    continue

                corr = self.correlate_pair(e1, e2)
                correlations.append(corr)

        return correlations
