"""
Feature Engineering Engine for NETRA Phase 6.
Extracts normalized multi-dimensional features across temporal, spatial, kinematic,
behavioral, anomaly, risk, and multi-source fusion dimensions with complete provenance.
"""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional
import logging

from models.event_intelligence import CanonicalEvent
from models.entity_intelligence import CanonicalEntity, EntityProfile
from models.predictive_intelligence import FeatureItem
from models.geo import haversine_distance_km

logger = logging.getLogger("netra.prediction.features")


class FeatureExtractor:
    """
    Extracts structured, explainable features from multi-phase intelligence evidence.
    Maintains complete lineage (derived_from and source_evidence) for every feature.
    """

    @classmethod
    def extract_features(
        cls,
        events: List[CanonicalEvent],
        entity: Optional[CanonicalEntity] = None,
        profile: Optional[EntityProfile] = None,
        anomaly_assessment: Optional[Dict[str, Any]] = None,
        fused_observations: Optional[List[Any]] = None,
    ) -> List[FeatureItem]:
        """
        Extracts multi-domain features from events, entity history, anomalies, and fused feeds.
        """
        features: List[FeatureItem] = []
        if not events:
            return features

        sorted_events = sorted(events, key=lambda e: e.timestamp)
        event_ids = [e.event_id for e in sorted_events]
        source_ids = [e.source.source_id for e in sorted_events if e.source]

        # -------------------------------------------------------------
        # 1. Temporal Features
        # -------------------------------------------------------------
        time_span_hours = max(
            0.1,
            (sorted_events[-1].timestamp - sorted_events[0].timestamp).total_seconds() / 3600.0
        )
        freq_per_hour = len(sorted_events) / time_span_hours
        norm_freq = min(1.0, freq_per_hour / 10.0)
        features.append(FeatureItem(
            feature_name="temporal_event_frequency",
            value=round(freq_per_hour, 3),
            normalized_value=round(norm_freq, 4),
            derived_from=event_ids,
            source_evidence=source_ids,
        ))

        # Inter-event intervals
        if len(sorted_events) > 1:
            intervals = [
                (sorted_events[i].timestamp - sorted_events[i - 1].timestamp).total_seconds() / 60.0
                for i in range(1, len(sorted_events))
            ]
            mean_interval_min = sum(intervals) / len(intervals)
            norm_interval = max(0.0, min(1.0, 1.0 - (mean_interval_min / 360.0)))
        else:
            mean_interval_min = 60.0
            norm_interval = 0.50

        features.append(FeatureItem(
            feature_name="temporal_inter_event_interval_mean",
            value=round(mean_interval_min, 2),
            normalized_value=round(norm_interval, 4),
            derived_from=event_ids,
            source_evidence=source_ids,
        ))

        # -------------------------------------------------------------
        # 2. Kinematic Features
        # -------------------------------------------------------------
        speeds = [float(e.attributes.get("speed", 0.0)) for e in sorted_events]
        mean_speed = sum(speeds) / len(speeds)
        max_speed = max(speeds)
        norm_mean_speed = min(1.0, mean_speed / 150.0)
        features.append(FeatureItem(
            feature_name="kinematic_mean_speed",
            value=round(mean_speed, 2),
            normalized_value=round(norm_mean_speed, 4),
            derived_from=event_ids,
            source_evidence=source_ids,
        ))

        # Kinematic acceleration / speed slope
        if len(speeds) >= 2:
            speed_delta = speeds[-1] - speeds[0]
            norm_speed_delta = min(1.0, max(0.0, (speed_delta + 100.0) / 200.0))
        else:
            speed_delta = 0.0
            norm_speed_delta = 0.50

        features.append(FeatureItem(
            feature_name="kinematic_speed_trend_delta",
            value=round(speed_delta, 2),
            normalized_value=round(norm_speed_delta, 4),
            derived_from=event_ids,
            source_evidence=source_ids,
        ))

        # -------------------------------------------------------------
        # 3. Behavioral Features
        # -------------------------------------------------------------
        activities = [float(e.attributes.get("activity_level", 0.5)) for e in sorted_events]
        mean_activity = sum(activities) / len(activities)
        recent_activity = activities[-1]
        activity_slope = (activities[-1] - activities[0]) if len(activities) > 1 else 0.0

        features.append(FeatureItem(
            feature_name="behavioral_activity_level_current",
            value=round(recent_activity, 3),
            normalized_value=round(min(1.0, max(0.0, recent_activity)), 4),
            derived_from=[sorted_events[-1].event_id],
            source_evidence=source_ids[-1:] if source_ids else [],
        ))

        features.append(FeatureItem(
            feature_name="behavioral_activity_trend_slope",
            value=round(activity_slope, 3),
            normalized_value=round(min(1.0, max(0.0, (activity_slope + 1.0) / 2.0)), 4),
            derived_from=event_ids,
            source_evidence=source_ids,
        ))

        # -------------------------------------------------------------
        # 4. Spatial Features
        # -------------------------------------------------------------
        if len(sorted_events) >= 2:
            first_loc = sorted_events[0].location
            last_loc = sorted_events[-1].location
            spatial_disp = haversine_distance_km(first_loc, last_loc)
        else:
            spatial_disp = 0.0

        norm_disp = min(1.0, max(0.0, spatial_disp / 50.0))
        features.append(FeatureItem(
            feature_name="spatial_centroid_displacement",
            value=round(spatial_disp, 3),
            normalized_value=round(norm_disp, 4),
            derived_from=event_ids,
            source_evidence=source_ids,
        ))

        # -------------------------------------------------------------
        # 5. Phase 4 Anomaly & Risk Features
        # -------------------------------------------------------------
        if anomaly_assessment:
            anom_score = float(anomaly_assessment.get("anomaly", {}).get("score", anomaly_assessment.get("anomaly_score", 0.0)))
            anom_state = str(anomaly_assessment.get("anomaly", {}).get("state", "TRANSIENT"))
            risk_score = float(anomaly_assessment.get("risk", {}).get("score", anomaly_assessment.get("risk_score", 0.0)))
            risk_trend_dir = str(anomaly_assessment.get("risk", {}).get("trend", {}).get("direction", "STABLE"))

            features.append(FeatureItem(
                feature_name="anomaly_score_composite",
                value=round(anom_score, 4),
                normalized_value=round(min(1.0, max(0.0, anom_score)), 4),
                derived_from=[anomaly_assessment.get("analysis_id", "ANOM-PHASE4")],
                source_evidence=source_ids,
            ))

            features.append(FeatureItem(
                feature_name="anomaly_overall_score",
                value=round(anom_score, 4),
                normalized_value=round(min(1.0, max(0.0, anom_score)), 4),
                derived_from=[anomaly_assessment.get("analysis_id", "ANOM-PHASE4")],
                source_evidence=source_ids,
            ))

            is_persistent_anom = 1.0 if anom_state in ("PERSISTENT", "ESCALATING", "RECURRING") else 0.20
            features.append(FeatureItem(
                feature_name="anomaly_persistence_factor",
                value=is_persistent_anom,
                normalized_value=is_persistent_anom,
                derived_from=[anomaly_assessment.get("analysis_id", "ANOM-PHASE4")],
                source_evidence=source_ids,
            ))

            features.append(FeatureItem(
                feature_name="risk_score_current",
                value=round(risk_score, 4),
                normalized_value=round(min(1.0, max(0.0, risk_score)), 4),
                derived_from=[anomaly_assessment.get("analysis_id", "ANOM-PHASE4")],
                source_evidence=source_ids,
            ))

            features.append(FeatureItem(
                feature_name="anomaly_risk_score",
                value=round(risk_score, 4),
                normalized_value=round(min(1.0, max(0.0, risk_score)), 4),
                derived_from=[anomaly_assessment.get("analysis_id", "ANOM-PHASE4")],
                source_evidence=source_ids,
            ))

            risk_trend_val = 0.85 if "RISING" in risk_trend_dir or "INCREASING" in risk_trend_dir else (0.25 if "FALLING" in risk_trend_dir else 0.50)
            features.append(FeatureItem(
                feature_name="risk_trend_indicator",
                value=risk_trend_val,
                normalized_value=risk_trend_val,
                derived_from=[anomaly_assessment.get("analysis_id", "ANOM-PHASE4")],
                source_evidence=source_ids,
            ))

        # -------------------------------------------------------------
        # 6. Phase 5 Multi-Source Fusion Features
        # -------------------------------------------------------------
        if fused_observations:
            latest_fo = fused_observations[-1]
            indep_src = getattr(latest_fo, "independent_source_count", 1)
            agree_score = getattr(latest_fo, "agreement_score", 0.80)
            conf_score = getattr(latest_fo, "fusion_confidence", 0.75)
            conflict_score = getattr(latest_fo, "conflict_score", 0.0)

            features.append(FeatureItem(
                feature_name="fusion_independent_sources",
                value=float(indep_src),
                normalized_value=round(min(1.0, max(0.0, indep_src / 4.0)), 4),
                derived_from=[getattr(latest_fo, "fused_observation_id", "FO-PHASE5")],
                source_evidence=getattr(latest_fo, "supporting_sources", []),
            ))

            features.append(FeatureItem(
                feature_name="fusion_agreement_score",
                value=round(agree_score, 4),
                normalized_value=round(min(1.0, max(0.0, agree_score)), 4),
                derived_from=[getattr(latest_fo, "fused_observation_id", "FO-PHASE5")],
                source_evidence=getattr(latest_fo, "supporting_sources", []),
            ))

            features.append(FeatureItem(
                feature_name="fusion_confidence",
                value=round(conf_score, 4),
                normalized_value=round(min(1.0, max(0.0, conf_score)), 4),
                derived_from=[getattr(latest_fo, "fused_observation_id", "FO-PHASE5")],
                source_evidence=getattr(latest_fo, "supporting_sources", []),
            ))

            features.append(FeatureItem(
                feature_name="fusion_mean_confidence",
                value=round(conf_score, 4),
                normalized_value=round(min(1.0, max(0.0, conf_score)), 4),
                derived_from=[getattr(latest_fo, "fused_observation_id", "FO-PHASE5")],
                source_evidence=getattr(latest_fo, "supporting_sources", []),
            ))

            features.append(FeatureItem(
                feature_name="fusion_conflict_severity",
                value=round(conflict_score, 4),
                normalized_value=round(min(1.0, max(0.0, conflict_score)), 4),
                derived_from=[getattr(latest_fo, "fused_observation_id", "FO-PHASE5")],
                source_evidence=getattr(latest_fo, "supporting_sources", []),
            ))


        return features
