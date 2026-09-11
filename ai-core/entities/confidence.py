"""
Entity Confidence Engine for NETRA Entity Intelligence.
Computes multi-dimensional confidence metrics with strict cold-start gating (< 3 events),
observation depth, time span depth, telemetry completeness, source reliability,
and penalty deductions for conflicting or contradictory sensor telemetry.
"""

from typing import List, Optional
from config import NetraConfig, default_config
from models.geo import haversine_distance_km
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import (
    CanonicalEntity,
    EntityBehaviorProfile,
    EntityConfidenceFactor,
    EntityConfidenceContradiction,
    EntityConfidenceProfile,
)


class EntityConfidenceEngine:
    """Computes bounded confidence rating and checks for contradictory telemetry."""

    def __init__(self, config: Optional[NetraConfig] = None):
        self.config = config or default_config
        self.weights = self.config.entity_confidence_weights

    def compute_confidence(
        self,
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        baseline: EntityBehaviorProfile,
    ) -> EntityConfidenceProfile:
        """Compute reliability assessment for entity profile and detections."""
        if not events:
            return EntityConfidenceProfile(
                score=0.10,
                level="LOW",
                factors=[
                    EntityConfidenceFactor(
                        factor="NO_OBSERVATIONS",
                        score=0.10,
                        description="Zero events available for this entity",
                    )
                ],
                contradictions=[],
            )

        # 1. Observation Depth [0.0 - 1.0] (10+ events = 1.0)
        obs_score = min(1.0, round(len(events) / 10.0, 2))

        # 2. Time Span Depth [0.0 - 1.0] (72+ hours = 1.0)
        span_hours = max(0.0, (entity.last_observed - entity.first_observed).total_seconds() / 3600.0)
        time_score = min(1.0, round(max(0.10, span_hours / 72.0), 2))

        # 3. Telemetry Completeness [0.0 - 1.0]
        telemetry_fields = ["speed", "activity_level", "heading_deg"]
        present_count = sum(
            1 for e in events
            for f in telemetry_fields
            if f in e.attributes and e.attributes[f] is not None
        )
        total_possible = len(events) * len(telemetry_fields)
        comp_score = round(max(0.50, present_count / total_possible), 2) if total_possible > 0 else 0.80

        # 4. Source Reliability [0.0 - 1.0]
        source_rel_scores = [
            getattr(e.source, "reliability", getattr(e.source, "reliability_score", 0.85))
            for e in events
        ]
        src_score = round(sum(source_rel_scores) / len(source_rel_scores), 2)

        # Base weighted score
        raw_score = (
            obs_score * self.weights.observation_depth
            + time_score * self.weights.time_span_depth
            + comp_score * self.weights.completeness
            + src_score * self.weights.source_reliability
        )

        factors = [
            EntityConfidenceFactor(
                factor="OBSERVATION_DEPTH",
                score=obs_score,
                description=f"{len(events)} discrete synthetic event observation(s)",
            ),
            EntityConfidenceFactor(
                factor="TIME_SPAN_DEPTH",
                score=time_score,
                description=f"Active observation baseline span of {span_hours:.1f} hours",
            ),
            EntityConfidenceFactor(
                factor="TELEMETRY_COMPLETENESS",
                score=comp_score,
                description=f"Field completeness rating across required kinematics: {comp_score * 100:.0f}%",
            ),
            EntityConfidenceFactor(
                factor="SOURCE_RELIABILITY",
                score=src_score,
                description=f"Mean sensor feeder reliability index: {src_score:.2f}",
            ),
        ]

        # 5. Sensor Contradiction Detection
        contradictions: List[EntityConfidenceContradiction] = []
        sorted_events = sorted(events, key=lambda x: x.timestamp)

        for i in range(len(sorted_events) - 1):
            e1 = sorted_events[i]
            e2 = sorted_events[i + 1]
            time_delta = abs((e2.timestamp - e1.timestamp).total_seconds())

            # Check concurrent or near-concurrent reporting (< 120s)
            if time_delta <= 120.0:
                dist = haversine_distance_km(e1.location, e2.location)
                # Physical impossibility check: ground vehicle > 5km in 120s
                if dist > 5.0 and entity.entity_type.upper() in ["VEHICLE", "PATROL_UNIT"]:
                    contradictions.append(
                        EntityConfidenceContradiction(
                            feature="location",
                            sources=[e1.source.source_id, e2.source.source_id],
                            confidence_impact=0.15,
                            description=(
                                f"Sensors reported contradictory coordinates ({dist:.1f} km apart) "
                                f"within {int(time_delta)} seconds"
                            ),
                        )
                    )

                # Speed contradiction check
                s1 = float(e1.attributes.get("speed", 0.0))
                s2 = float(e2.attributes.get("speed", 0.0))
                if abs(s1 - s2) > 80.0:
                    contradictions.append(
                        EntityConfidenceContradiction(
                            feature="speed",
                            sources=[e1.source.source_id, e2.source.source_id],
                            confidence_impact=0.15,
                            description=(
                                f"Sensors reported conflicting speed telemetry ({s1:.1f} vs {s2:.1f} km/h) "
                                f"within {int(time_delta)} seconds"
                            ),
                        )
                    )

            # Explicit contradiction attribute in synthetic test payload
            if e2.attributes.get("contradictory_sensor") or e2.attributes.get("telemetry_conflict"):
                if not any(c.feature == "telemetry_conflict" for c in contradictions):
                    contradictions.append(
                        EntityConfidenceContradiction(
                            feature="telemetry_conflict",
                            sources=[e1.source.source_id, e2.source.source_id],
                            confidence_impact=0.20,
                            description="Direct sensor conflict flagged in operational stream",
                        )
                    )

        # Apply contradiction penalties
        penalty = sum(c.confidence_impact for c in contradictions)
        penalized_score = max(0.05, round(raw_score - penalty, 2))

        # 6. Cold-Start Cap: < 3 observations cannot exceed 0.35 confidence
        if len(events) < self.config.entity.min_observations_for_baseline:
            penalized_score = min(0.35, penalized_score)
            factors.append(
                EntityConfidenceFactor(
                    factor="COLD_START_RESTRICTION",
                    score=0.35,
                    description=f"Cold-start condition: {len(events)} < 3 minimum events required for high confidence",
                )
            )

        final_score = round(penalized_score, 2)

        # Categorical Level
        if final_score >= 0.70:
            level = "HIGH"
        elif final_score >= 0.40:
            level = "MEDIUM"
        else:
            level = "LOW"

        return EntityConfidenceProfile(
            score=final_score,
            level=level,
            factors=factors,
            contradictions=contradictions,
        )
