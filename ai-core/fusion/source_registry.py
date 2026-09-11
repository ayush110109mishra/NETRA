"""
Source Registry and Source Health Monitoring for NETRA Phase 5.
Maintains deterministic catalog of synthetic intelligence sources, tracks
independence groups to prevent double counting, calculates explainable
source reliability, and assesses sensor health/dropout states.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
import logging

from config import NetraConfig, default_config, SourceReliabilityWeights
from models.fusion_intelligence import (
    SourceMetadata,
    SourceHealth,
    SourceStatus,
    SourceType,
)

logger = logging.getLogger("netra.fusion.source_registry")


class SourceRegistry:
    """
    Central catalog of registered synthetic intelligence sources.
    Enforces deterministic source evaluation, independence clustering,
    and explainable reliability calculations.
    """

    def __init__(self, config: Optional[NetraConfig] = None):
        self.config = config or default_config
        self.weights: SourceReliabilityWeights = self.config.source_reliability_weights
        self._sources: Dict[str, SourceMetadata] = {}
        self._initialize_default_synthetic_sources()

    def _initialize_default_synthetic_sources(self) -> None:
        """Pre-load standard synthetic sensors specified in NETRA Phase 5."""
        default_sources = [
            SourceMetadata(
                source_id="RADAR_01",
                source_type=SourceType.RADAR,
                source_name="Synthetic Primary Surveillance Radar 01",
                reliability=0.90,
                independence_group="RADAR_ALPHA",
                spatial_accuracy_km=0.05,
                temporal_accuracy_sec=0.5,
                status=SourceStatus.ACTIVE,
                metadata={"band": "X-Band", "coverage_radius_km": 150.0},
            ),
            SourceMetadata(
                source_id="RADAR_01_DUP",
                source_type=SourceType.RADAR,
                source_name="Synthetic Primary Radar Retransmission Feed",
                reliability=0.88,
                independence_group="RADAR_ALPHA",  # Shares independence group with RADAR_01!
                spatial_accuracy_km=0.05,
                temporal_accuracy_sec=0.5,
                status=SourceStatus.ACTIVE,
                metadata={"is_retransmission": True, "parent_source": "RADAR_01"},
            ),
            SourceMetadata(
                source_id="OPTICAL_01",
                source_type=SourceType.OPTICAL,
                source_name="Synthetic Long-Range EO/IR Sensor 01",
                reliability=0.85,
                independence_group="OPTICAL_BRAVO",
                spatial_accuracy_km=0.02,
                temporal_accuracy_sec=0.2,
                status=SourceStatus.ACTIVE,
                metadata={"spectrum": "EO/MWIR", "resolution_m": 0.5},
            ),
            SourceMetadata(
                source_id="TELEMETRY_01",
                source_type=SourceType.TELEMETRY,
                source_name="Direct Synthetic Platform Telemetry Link",
                reliability=0.95,
                independence_group="TELEMETRY_CHARLIE",
                spatial_accuracy_km=0.01,
                temporal_accuracy_sec=0.1,
                status=SourceStatus.ACTIVE,
                metadata={"protocol": "SECURE_DATALINK_SYNTH"},
            ),
            SourceMetadata(
                source_id="SIGNAL_01",
                source_type=SourceType.SIGNAL,
                source_name="Synthetic SIGINT / RF Direction Finder",
                reliability=0.70,
                independence_group="SIGNAL_DELTA",
                spatial_accuracy_km=0.50,
                temporal_accuracy_sec=2.0,
                status=SourceStatus.ACTIVE,
                metadata={"frequency_coverage_mhz": "100-6000"},
            ),
            SourceMetadata(
                source_id="SENSOR_A",
                source_type=SourceType.SENSOR_A,
                source_name="Forward Synthetic Multi-Sensor Cluster A",
                reliability=0.85,
                independence_group="SENSOR_A_GROUP",
                spatial_accuracy_km=0.10,
                temporal_accuracy_sec=1.0,
                status=SourceStatus.ACTIVE,
                metadata={"sector": "SECTOR_NORTH"},
            ),
            SourceMetadata(
                source_id="SENSOR_B",
                source_type=SourceType.SENSOR_B,
                source_name="Secondary Synthetic Sensor Unit B",
                reliability=0.50,
                independence_group="SENSOR_B_GROUP",
                spatial_accuracy_km=0.25,
                temporal_accuracy_sec=1.5,
                status=SourceStatus.DEGRADED,
                contradiction_rate=0.18,
                metadata={"sector": "SECTOR_EAST", "maintenance_flag": True},
            ),
            SourceMetadata(
                source_id="LOW_REL_SENSOR",
                source_type=SourceType.SENSOR_B,
                source_name="Unverified Tactical Acoustic Sensor",
                reliability=0.35,
                independence_group="UNVERIFIED_GROUP",
                spatial_accuracy_km=0.60,
                temporal_accuracy_sec=3.0,
                status=SourceStatus.DEGRADED,
                contradiction_rate=0.25,
                metadata={"unverified": True},
            ),
        ]
        for src in default_sources:
            self._sources[src.source_id] = src

    def register_source(self, source: SourceMetadata) -> None:
        """Register or update a source metadata entry."""
        self._sources[source.source_id] = source

    def get_source(self, source_id: str) -> SourceMetadata:
        """
        Retrieve source metadata. If not registered, deterministically creates
        a cold-start entry with UNKNOWN status and capped reliability.
        """
        if source_id in self._sources:
            return self._sources[source_id]

        # Cold-start fallback for previously unseen synthetic source
        new_source = SourceMetadata(
            source_id=source_id,
            source_type=SourceType.UNKNOWN,
            source_name=f"Synthetic Source {source_id}",
            reliability=0.40,
            independence_group=f"INDEP_{source_id}",
            spatial_accuracy_km=0.30,
            temporal_accuracy_sec=2.0,
            status=SourceStatus.UNKNOWN,
            metadata={"cold_start": True},
        )
        self._sources[source_id] = new_source
        return new_source

    def list_sources(self) -> List[SourceMetadata]:
        """List all registered synthetic sources in deterministic sorted order."""
        return [self._sources[k] for k in sorted(self._sources.keys())]

    def calculate_source_reliability(
        self,
        source_id: str,
        observation_count: int = 1,
        contradiction_count: int = 0,
        is_stale: bool = False,
        is_dropout: bool = False,
        completeness_ratio: float = 1.0,
    ) -> Tuple[float, Dict[str, float], str]:
        """
        Calculates explainable, deterministic source reliability score.
        Combines declared reliability, consistency, completeness, and operational stability.
        """
        source = self.get_source(source_id)

        # Base factors
        declared = source.reliability
        
        # Historical consistency (penalized by contradiction rate)
        raw_c_rate = (contradiction_count / max(1, observation_count)) if observation_count > 0 else source.contradiction_rate
        c_rate = min(1.0, max(0.0, raw_c_rate))
        consistency = max(0.0, 1.0 - (c_rate * 1.5))
        
        # Completeness factor
        completeness = max(0.0, min(1.0, completeness_ratio))
        
        # Operational stability factor (dropout or stale data degrades stability)
        stability = 1.0
        if is_dropout:
            stability -= 0.40
        if is_stale:
            stability -= 0.30
        stability = max(0.0, stability)

        # Cold start dampening
        if observation_count < 3 and source.metadata.get("cold_start", False):
            declared = min(declared, 0.40)
            consistency = min(consistency, 0.50)

        # Weighted calculation
        w = self.weights
        score = (
            (w.declared_reliability * declared)
            + (w.historical_consistency * consistency)
            + (w.observation_completeness * completeness)
            + (w.stability * stability)
        )
        bounded_score = round(max(0.0, min(1.0, score)), 4)

        factors = {
            "declared_reliability": round(declared, 4),
            "historical_consistency": round(consistency, 4),
            "observation_completeness": round(completeness, 4),
            "stability": round(stability, 4),
            "contradiction_penalty": round(c_rate * 0.20, 4),
            "staleness_penalty": round(0.15 if is_stale else 0.0, 4),
        }

        explanation_parts = [
            f"Base reliability {declared:.2f}",
            f"consistency {consistency:.2f} (contradiction rate {c_rate:.1%})",
            f"completeness {completeness:.2f}",
        ]
        if is_dropout:
            explanation_parts.append("PENALTY: Sensor dropout detected")
        if is_stale:
            explanation_parts.append("PENALTY: Telemetry stale")
        if observation_count < 3 and source.metadata.get("cold_start", False):
            explanation_parts.append("CAUTION: Cold-start limited history (< 3 observations)")

        explanation = f"Source {source_id} reliability {bounded_score:.2f} ({'; '.join(explanation_parts)})."
        return bounded_score, factors, explanation

    def get_source_health(
        self,
        source_id: str,
        observation_count: int = 1,
        contradiction_count: int = 0,
        is_stale: bool = False,
        is_dropout: bool = False,
        completeness_ratio: float = 1.0,
    ) -> SourceHealth:
        """
        Produces detailed SourceHealth object with operational status evaluation.
        """
        source = self.get_source(source_id)
        score, factors, explanation = self.calculate_source_reliability(
            source_id=source_id,
            observation_count=observation_count,
            contradiction_count=contradiction_count,
            is_stale=is_stale,
            is_dropout=is_dropout,
            completeness_ratio=completeness_ratio,
        )

        # Derive status
        if is_dropout:
            status = SourceStatus.DROPOUT
        elif observation_count < 3 and source.metadata.get("cold_start", False):
            status = SourceStatus.UNKNOWN
        elif score < 0.45 or is_stale:
            status = SourceStatus.DEGRADED
        elif score >= 0.70:
            status = SourceStatus.ACTIVE
        else:
            status = SourceStatus.DEGRADED

        c_rate = round(min(1.0, max(0.0, (contradiction_count / max(1, observation_count)) if observation_count > 0 else source.contradiction_rate)), 4)


        return SourceHealth(
            source_id=source_id,
            source_type=source.source_type.value if hasattr(source.source_type, "value") else str(source.source_type),
            status=status,
            reliability_score=score,
            is_stale=is_stale,
            is_dropout=is_dropout,
            observation_count=observation_count,
            contradiction_rate=c_rate,
            reliability_trend="DEGRADING" if (is_dropout or is_stale or c_rate > 0.15) else "STABLE",
            factors=factors,
            explanation=explanation,
        )
