"""
Conflict Detection and Arbitration Engine for NETRA Phase 5.
Detects geospatial, kinematic, taxonomy, and temporal contradictions across
reporting sensors while preserving all conflicting claims in immutable audit records.
"""

from typing import Any, Dict, List, Optional
import math
import logging

from config import NetraConfig, default_config, ConflictThresholds
from models.geo import haversine_distance_km
from models.fusion_intelligence import (
    CanonicalObservation,
    ConflictRecord,
    ConflictStatus,
    ConflictType,
)
from fusion.source_registry import SourceRegistry

logger = logging.getLogger("netra.fusion.conflict")


class ConflictDetector:
    """
    Detects and arbitrates multi-source intelligence contradictions.
    Never silently discards conflicting reports; preserves full source claims.
    """

    def __init__(
        self,
        config: Optional[NetraConfig] = None,
        source_registry: Optional[SourceRegistry] = None,
    ):
        self.config = config or default_config
        self.thresholds: ConflictThresholds = self.config.conflict
        self.registry = source_registry or SourceRegistry(self.config)

    def detect_conflicts(
        self,
        observations: List[CanonicalObservation],
    ) -> List[ConflictRecord]:
        """
        Scans pairs of observations for material contradictions.
        Returns a list of ConflictRecords with source claims and arbitration status.
        """
        conflicts: List[ConflictRecord] = []
        if len(observations) < 2:
            return conflicts

        # Compare pairs deterministically
        n = len(observations)
        for i in range(n):
            for j in range(i + 1, n):
                obs1 = observations[i]
                obs2 = observations[j]

                # If from same source and exact same observation, skip
                if obs1.observation_id == obs2.observation_id:
                    continue

                # 1. Position Conflict
                pos_conflict = self._check_position_conflict(obs1, obs2)
                if pos_conflict:
                    conflicts.append(pos_conflict)

                # 2. Velocity / Kinematic Conflict
                vel_conflict = self._check_velocity_conflict(obs1, obs2)
                if vel_conflict:
                    conflicts.append(vel_conflict)

                # 3. Event-Type / Classification Conflict
                type_conflict = self._check_event_type_conflict(obs1, obs2)
                if type_conflict:
                    conflicts.append(type_conflict)

                # 4. Status Conflict
                status_conflict = self._check_status_conflict(obs1, obs2)
                if status_conflict:
                    conflicts.append(status_conflict)

        return conflicts

    def _check_position_conflict(
        self,
        obs1: CanonicalObservation,
        obs2: CanonicalObservation,
    ) -> Optional[ConflictRecord]:
        if not obs1.position or not obs2.position:
            return None

        dist_km = haversine_distance_km(obs1.position, obs2.position)
        if dist_km > self.thresholds.position_conflict_km:
            severity = min(1.0, dist_km / 50.0)
            claims = {
                obs1.source_id: {
                    "latitude": obs1.position.latitude,
                    "longitude": obs1.position.longitude,
                    "uncertainty_km": obs1.position_uncertainty_km,
                },
                obs2.source_id: {
                    "latitude": obs2.position.latitude,
                    "longitude": obs2.position.longitude,
                    "uncertainty_km": obs2.position_uncertainty_km,
                },
            }

            # Arbitrate based on source reliability
            src1_rel = self.registry.get_source(obs1.source_id).reliability
            src2_rel = self.registry.get_source(obs2.source_id).reliability
            rel_diff = abs(src1_rel - src2_rel)

            if rel_diff >= 0.25:
                arb_status = ConflictStatus.RESOLVED
                favored_src = obs1.source_id if src1_rel > src2_rel else obs2.source_id
                resolved_claim = claims[favored_src]
                method = f"FAVOR_HIGHER_RELIABILITY ({favored_src} rel={max(src1_rel, src2_rel):.2f} vs {min(src1_rel, src2_rel):.2f})"
                uncertainty = round(1.0 - max(src1_rel, src2_rel), 4)
                expl = (
                    f"Position conflict ({dist_km:.1f}km discrepancy) resolved in favor of "
                    f"{favored_src} due to material reliability advantage."
                )
            else:
                arb_status = ConflictStatus.UNRESOLVED
                resolved_claim = None
                method = "UNRESOLVED_COMPARABLE_RELIABILITY"
                uncertainty = round(min(1.0, severity * 0.8), 4)
                expl = (
                    f"UNRESOLVED position conflict: {obs1.source_id} and {obs2.source_id} differ by "
                    f"{dist_km:.1f}km with comparable source reliabilities ({src1_rel:.2f} vs {src2_rel:.2f})."
                )

            cid = f"CONF-POS-{obs1.observation_id[:6]}-{obs2.observation_id[:6]}"
            return ConflictRecord(
                conflict_id=cid,
                conflict_type=ConflictType.POSITION,
                severity=round(severity, 4),
                sources=[obs1.source_id, obs2.source_id],
                observation_ids=[obs1.observation_id, obs2.observation_id],
                status=arb_status,
                claims=claims,
                resolution_method=method,
                resolved_claim=resolved_claim,
                unresolved_uncertainty=uncertainty,
                explanation=expl,
            )
        return None

    def _check_velocity_conflict(
        self,
        obs1: CanonicalObservation,
        obs2: CanonicalObservation,
    ) -> Optional[ConflictRecord]:
        if not obs1.velocity or not obs2.velocity:
            return None

        speed_diff = abs(obs1.velocity.speed_kmh - obs2.velocity.speed_kmh)
        heading_diff = 0.0
        if obs1.velocity.heading_deg is not None and obs2.velocity.heading_deg is not None:
            raw_diff = abs(obs1.velocity.heading_deg - obs2.velocity.heading_deg)
            heading_diff = min(raw_diff, 360.0 - raw_diff)

        is_conflict = (
            speed_diff > self.thresholds.speed_conflict_kmh
            or heading_diff > self.thresholds.heading_conflict_deg
        )

        if is_conflict:
            severity = max(speed_diff / 150.0, heading_diff / 180.0)
            severity = min(1.0, severity)
            claims = {
                obs1.source_id: {
                    "speed_kmh": obs1.velocity.speed_kmh,
                    "heading_deg": obs1.velocity.heading_deg,
                },
                obs2.source_id: {
                    "speed_kmh": obs2.velocity.speed_kmh,
                    "heading_deg": obs2.velocity.heading_deg,
                },
            }

            src1_rel = self.registry.get_source(obs1.source_id).reliability
            src2_rel = self.registry.get_source(obs2.source_id).reliability
            rel_diff = abs(src1_rel - src2_rel)

            if rel_diff >= 0.25:
                arb_status = ConflictStatus.RESOLVED
                favored_src = obs1.source_id if src1_rel > src2_rel else obs2.source_id
                resolved_claim = claims[favored_src]
                method = f"FAVOR_HIGHER_RELIABILITY ({favored_src})"
                uncertainty = round(1.0 - max(src1_rel, src2_rel), 4)
                expl = (
                    f"Velocity conflict (speed delta {speed_diff:.1f}km/h, heading delta {heading_diff:.1f}°) "
                    f"resolved favoring {favored_src}."
                )
            else:
                arb_status = ConflictStatus.UNRESOLVED
                resolved_claim = None
                method = "UNRESOLVED_COMPARABLE_RELIABILITY"
                uncertainty = round(severity * 0.7, 4)
                expl = (
                    f"UNRESOLVED velocity conflict: speed delta {speed_diff:.1f}km/h, "
                    f"heading delta {heading_diff:.1f}° between {obs1.source_id} and {obs2.source_id}."
                )

            cid = f"CONF-VEL-{obs1.observation_id[:6]}-{obs2.observation_id[:6]}"
            return ConflictRecord(
                conflict_id=cid,
                conflict_type=ConflictType.VELOCITY,
                severity=round(severity, 4),
                sources=[obs1.source_id, obs2.source_id],
                observation_ids=[obs1.observation_id, obs2.observation_id],
                status=arb_status,
                claims=claims,
                resolution_method=method,
                resolved_claim=resolved_claim,
                unresolved_uncertainty=uncertainty,
                explanation=expl,
            )
        return None

    def _check_event_type_conflict(
        self,
        obs1: CanonicalObservation,
        obs2: CanonicalObservation,
    ) -> Optional[ConflictRecord]:
        if not obs1.event_type or not obs2.event_type:
            return None

        t1 = obs1.event_type.upper().strip()
        t2 = obs2.event_type.upper().strip()

        # Incompatible critical pairs (e.g. routine patrol vs electronic warfare / strike)
        if t1 != t2 and ("PATROL" in t1 and ("JAMMING" in t2 or "STRIKE" in t2) or ("JAMMING" in t1 and "PATROL" in t2)):
            severity = 0.85
            claims = {
                obs1.source_id: {"event_type": t1},
                obs2.source_id: {"event_type": t2},
            }

            src1_rel = self.registry.get_source(obs1.source_id).reliability
            src2_rel = self.registry.get_source(obs2.source_id).reliability
            rel_diff = abs(src1_rel - src2_rel)

            if rel_diff >= 0.25:
                arb_status = ConflictStatus.RESOLVED
                favored_src = obs1.source_id if src1_rel > src2_rel else obs2.source_id
                resolved_claim = claims[favored_src]
                method = f"FAVOR_SPECIALIZED_OR_HIGH_RELIABILITY ({favored_src})"
                uncertainty = 0.20
                expl = f"Event type conflict ({t1} vs {t2}) resolved favoring {favored_src}."
            else:
                arb_status = ConflictStatus.UNRESOLVED
                resolved_claim = None
                method = "UNRESOLVED_CONTRADICTORY_TAXONOMY"
                uncertainty = 0.60
                expl = f"Contradictory event type reported: {obs1.source_id} claims {t1} while {obs2.source_id} claims {t2}."

            cid = f"CONF-TYPE-{obs1.observation_id[:6]}-{obs2.observation_id[:6]}"
            return ConflictRecord(
                conflict_id=cid,
                conflict_type=ConflictType.EVENT_TYPE,
                severity=severity,
                sources=[obs1.source_id, obs2.source_id],
                observation_ids=[obs1.observation_id, obs2.observation_id],
                status=arb_status,
                claims=claims,
                resolution_method=method,
                resolved_claim=resolved_claim,
                unresolved_uncertainty=uncertainty,
                explanation=expl,
            )
        return None

    def _check_status_conflict(
        self,
        obs1: CanonicalObservation,
        obs2: CanonicalObservation,
    ) -> Optional[ConflictRecord]:
        s1 = obs1.attributes.get("status") or obs1.attributes.get("entity_status")
        s2 = obs2.attributes.get("status") or obs2.attributes.get("entity_status")

        if s1 and s2 and str(s1).upper() != str(s2).upper():
            if ("ACTIVE" in str(s1).upper() and "DISABLED" in str(s2).upper()) or ("DISABLED" in str(s1).upper() and "ACTIVE" in str(s2).upper()):
                cid = f"CONF-STAT-{obs1.observation_id[:6]}-{obs2.observation_id[:6]}"
                return ConflictRecord(
                    conflict_id=cid,
                    conflict_type=ConflictType.STATUS,
                    severity=0.75,
                    sources=[obs1.source_id, obs2.source_id],
                    observation_ids=[obs1.observation_id, obs2.observation_id],
                    status=ConflictStatus.UNRESOLVED,
                    claims={
                        obs1.source_id: {"status": str(s1)},
                        obs2.source_id: {"status": str(s2)},
                    },
                    resolution_method="UNRESOLVED_STATUS_CONTRADICTION",
                    resolved_claim=None,
                    unresolved_uncertainty=0.50,
                    explanation=f"Status contradiction: {obs1.source_id} reports {s1}, {obs2.source_id} reports {s2}.",
                )
        return None
