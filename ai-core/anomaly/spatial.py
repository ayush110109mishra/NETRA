"""
Spatial Anomaly Detector for NETRA Phase 4 Anomaly Intelligence.
Assesses coordinate excursions beyond historical operating boundaries,
centroid drift, spatial dispersion surges, and unexpected sector relocations.
"""

from typing import List, Dict, Optional, Any
from models.common import Coordinates
from models.geo import haversine_distance_km
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityBehaviorProfile
from models.anomaly_intelligence import DimensionScoreItem


class SpatialAnomalyDetector:
    """Detects spatial boundary breaches, dispersion surges, and sector shifts."""

    @staticmethod
    def detect(
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        baseline: Optional[EntityBehaviorProfile] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> DimensionScoreItem:
        """
        Evaluate spatial anomaly for entity observations.
        Returns DimensionScoreItem with normalized score [0.0 - 1.0].
        """
        if not events:
            return DimensionScoreItem(
                dimension="spatial",
                score=0.0,
                confidence=0.50,
                indicators=[],
                explanation="No recent events provided for spatial evaluation.",
                evidence_event_ids=[],
            )

        indicators: List[str] = []
        evidence_ids: List[str] = []
        scores: List[float] = []

        # 1. Centroid Distance & Operational Bounding Radius Check
        if baseline and baseline.spatial:
            centroid = None
            if hasattr(baseline.spatial, "centroid") and baseline.spatial.centroid:
                centroid = baseline.spatial.centroid
            elif hasattr(baseline.spatial, "centroid_lat") and baseline.spatial.centroid_lat is not None:
                centroid = Coordinates(
                    latitude=baseline.spatial.centroid_lat,
                    longitude=baseline.spatial.centroid_lon,
                )

            if centroid:
                base_dispersion = getattr(
                    baseline.spatial,
                    "bounding_radius_km",
                    getattr(baseline.spatial, "spatial_dispersion_km", 5.0),
                )
                base_dispersion = max(1.0, float(base_dispersion))

                excursion_events: List[CanonicalEvent] = []
                max_dist = 0.0

                for e in events:
                    dist = haversine_distance_km(centroid, e.coordinates)
                    if dist > max_dist:
                        max_dist = dist
                    if dist > base_dispersion:
                        excursion_events.append(e)

            if excursion_events:
                excursion_ratio = max_dist / base_dispersion
                if excursion_ratio >= 3.5:
                    score = min(1.0, round(0.75 + (excursion_ratio - 3.5) * 0.05, 2))
                    indicators.append("SEVERE_SPATIAL_BREACH")
                elif excursion_ratio >= 2.0:
                    score = min(0.85, round(0.55 + (excursion_ratio - 2.0) * 0.12, 2))
                    indicators.append("SPATIAL_EXPANSION")
                else:
                    score = min(0.60, round(0.35 + (excursion_ratio - 1.0) * 0.20, 2))
                    indicators.append("BOUNDARY_EXCURSION")

                scores.append(score)
                evidence_ids.extend([e.event_id for e in excursion_events])

        # 2. Sector Relocation / Sector Breach Check
        registered_sector = (
            entity.attributes.get("registered_sector")
            or entity.attributes.get("primary_sector")
            or (context.get("expected_sector") if context else None)
        )
        if registered_sector:
            sector_deviations: List[CanonicalEvent] = []
            for e in events:
                event_sector = e.attributes.get("sector") or e.attributes.get("sector_id")
                if event_sector and event_sector != registered_sector:
                    sector_deviations.append(e)

            if sector_deviations:
                scores.append(0.80)
                indicators.append("UNEXPECTED_SECTOR_RELOCATION")
                evidence_ids.extend([e.event_id for e in sector_deviations])

        # 3. Spatial jump / Teleportation between consecutive events
        if len(events) >= 2:
            sorted_events = sorted(events, key=lambda x: x.timestamp)
            for i in range(len(sorted_events) - 1):
                e1, e2 = sorted_events[i], sorted_events[i + 1]
                dt_hours = max(0.001, (e2.timestamp - e1.timestamp).total_seconds() / 3600.0)
                jump_dist = haversine_distance_km(e1.coordinates, e2.coordinates)
                implied_speed = jump_dist / dt_hours

                # Ground platforms jumping > 200 km/h or air platforms > 3000 km/h
                is_air = entity.entity_type.upper() in ["AIRCRAFT", "DRONE", "UAV"]
                speed_cap = 3000.0 if is_air else 200.0

                if implied_speed > speed_cap and jump_dist > 25.0:
                    scores.append(0.90)
                    indicators.append("UNREALISTIC_SPATIAL_DISPLACEMENT")
                    evidence_ids.extend([e1.event_id, e2.event_id])
                    break

        # 4. Aggregate dimensional score
        if not scores:
            final_score = 0.0
            explanation = "Spatial dispersion within nominal operational boundary."
        else:
            final_score = min(1.0, round(max(scores), 2))
            explanation = (
                f"Spatial anomaly detected (score {final_score:.2f}) with indicators: "
                f"{', '.join(indicators)}."
            )

        # Confidence calculation
        confidence = 0.90
        if not baseline or baseline.baseline_status == "INSUFFICIENT_HISTORY":
            confidence = min(confidence, 0.45)
        if len(events) < 2:
            confidence = min(confidence, 0.65)

        unique_evidence = list(dict.fromkeys(evidence_ids))

        return DimensionScoreItem(
            dimension="spatial",
            score=final_score,
            confidence=round(confidence, 2),
            indicators=indicators,
            explanation=explanation,
            evidence_event_ids=unique_evidence,
        )
