"""
Confidence Calibration Engine for NETRA Phase 4 Anomaly Intelligence.
Calibrates anomaly confidence independently of anomaly magnitude, factoring in sensor diversity,
cross-sensor contradictions, source reliability, and cold-start caps.
"""

from typing import List, Dict, Any, Tuple, Optional
from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity
from models.anomaly_intelligence import AnomalyConfirmationLevel


class ConfidenceCalibrator:
    """Calibrates confidence scores and determines confirmation levels."""

    @staticmethod
    def calibrate(
        entity: CanonicalEntity,
        events: List[CanonicalEvent],
        dimension_confidences: Optional[List[float]] = None,
        evidence_event_ids: Optional[List[str]] = None,
    ) -> Tuple[float, AnomalyConfirmationLevel, Dict[str, Any]]:
        """
        Calibrate overall anomaly confidence.
        Returns (calibrated_confidence, confirmation_level, audit_metadata).
        """
        audit: Dict[str, Any] = {}

        if not events:
            return 0.20, AnomalyConfirmationLevel.UNCONFIRMED, {"reason": "No events provided"}

        # Use specific anomalous evidence events if available to assess evidence quality
        if evidence_event_ids:
            target_events = [e for e in events if e.event_id in evidence_event_ids]
            if not target_events:
                target_events = events
        else:
            target_events = events

        # 1. Base confidence from dimension confidences or default
        if dimension_confidences:
            base_conf = sum(dimension_confidences) / len(dimension_confidences)
        else:
            base_conf = 0.70

        # 2. Source Reliability Average
        reliabilities = []
        for e in target_events:
            if hasattr(e, "source") and hasattr(e.source, "reliability"):
                reliabilities.append(float(e.source.reliability))
            elif "reliability" in e.attributes:
                reliabilities.append(float(e.attributes["reliability"]))
            else:
                reliabilities.append(0.80)

        avg_reliability = sum(reliabilities) / len(reliabilities) if reliabilities else 0.80
        audit["avg_source_reliability"] = round(avg_reliability, 3)

        # 3. Sensor Diversity Assessment
        sensors = set()
        for e in target_events:
            if hasattr(e, "source") and hasattr(e.source, "source_type"):
                sensors.add(str(e.source.source_type))
            elif "sensor_type" in e.attributes:
                sensors.add(str(e.attributes["sensor_type"]))
            elif "source" in e.attributes:
                sensors.add(str(e.attributes["source"]))

        audit["distinct_sensor_count"] = len(sensors)
        sensor_diversity_bonus = 0.0
        if len(sensors) >= 3:
            sensor_diversity_bonus = 0.15
        elif len(sensors) == 2:
            sensor_diversity_bonus = 0.08

        # 4. Cross-Sensor Contradiction Detection
        # E.g. Check if two events with similar timestamps have opposing speeds or positions
        contradiction_penalty = 0.0
        has_contradiction = False
        if len(events) >= 2:
            for i in range(len(events)):
                for j in range(i + 1, len(events)):
                    e1, e2 = events[i], events[j]
                    dt = abs((e1.timestamp - e2.timestamp).total_seconds())
                    if dt <= 180.0:  # within 3 minutes
                        s1 = float(e1.attributes.get("speed", -1))
                        s2 = float(e2.attributes.get("speed", -1))
                        if s1 >= 0 and s2 >= 0 and abs(s1 - s2) > 80.0:
                            contradiction_penalty = 0.35
                            has_contradiction = True
                            audit["contradiction"] = f"Conflicting speeds ({s1:.1f} vs {s2:.1f}) within {dt:.0f}s"
                            break
                if has_contradiction:
                    break

        audit["has_contradiction"] = has_contradiction

        # 5. Composite Confidence Calculation
        base_blended = (base_conf * 0.50) + (avg_reliability * 0.50)
        raw_confidence = base_blended + sensor_diversity_bonus - contradiction_penalty
        bounded_conf = max(0.10, min(0.98, raw_confidence))

        # Single sensor or low reliability cap
        if avg_reliability <= 0.40:
            bounded_conf = min(0.38, bounded_conf)
            audit["unverified_source_cap"] = True
        elif len(target_events) == 1 and len(sensors) <= 1:
            bounded_conf = min(0.65, bounded_conf)
            audit["single_sensor_cap"] = True

        # 6. Strict Cold-Start Enforcement
        # Fewer than 3 observations MUST NOT receive confidence > 0.35
        total_obs = max(len(events), getattr(entity, "observation_count", len(events)))
        if total_obs < 3:
            bounded_conf = min(0.35, bounded_conf)
            audit["cold_start_applied"] = True
        else:
            audit["cold_start_applied"] = False

        calibrated = round(bounded_conf, 4)

        # 7. Map to Confirmation Level
        if calibrated < 0.40:
            level = AnomalyConfirmationLevel.UNCONFIRMED
        elif calibrated < 0.70:
            level = AnomalyConfirmationLevel.SUPPORTED
        elif calibrated < 0.85:
            level = AnomalyConfirmationLevel.CORROBORATED
        else:
            level = AnomalyConfirmationLevel.STRONGLY_CORROBORATED

        return calibrated, level, audit
