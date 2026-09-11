"""
Evidence Ledger and Quality Assessment Engine for NETRA Phase 5.
Maintains immutable audit records tracing fused intelligence back to source
observations and evaluates evidence quality independently of anomaly/risk scores.
"""

from typing import Dict, List, Optional, Tuple, Any
import hashlib
import logging

from models.fusion_intelligence import (
    CanonicalObservation,
    ConflictRecord,
    EvidenceRecord,
)
from fusion.source_registry import SourceRegistry

logger = logging.getLogger("netra.fusion.evidence")


class EvidenceLedger:
    """
    Maintains provenance lineage for multi-source intelligence.
    Computes explainable evidence quality scores based on source reliability,
    field completeness, observation freshness, and contradiction absence.
    """

    def __init__(self, source_registry: Optional[SourceRegistry] = None):
        self.registry = source_registry or SourceRegistry()
        self._records: Dict[str, EvidenceRecord] = {}

    def create_evidence_record(
        self,
        observations: List[CanonicalObservation],
        derived_from: Optional[List[str]] = None,
        conflicts: Optional[List[ConflictRecord]] = None,
        lineage_steps: Optional[List[str]] = None,
    ) -> EvidenceRecord:
        """
        Creates an immutable EvidenceRecord connecting raw observations,
        derived processing steps, and calculated evidence quality.
        """
        obs_ids = sorted([o.observation_id for o in observations])
        derived = derived_from or []
        conf_list = conflicts or []

        # Deterministic evidence ID
        hash_input = f"{':'.join(obs_ids)}::{':'.join(derived)}"
        ev_id = f"EV-{hashlib.sha256(hash_input.encode('utf-8')).hexdigest()[:8].upper()}"

        quality = self.calculate_evidence_quality(observations, conf_list)

        steps = lineage_steps or [
            "SOURCE_INGESTION",
            "CANONICAL_NORMALIZATION",
            "TEMPORAL_SPATIAL_ALIGNMENT",
            "ENTITY_RESOLUTION",
            "CORROBORATION_ASSESSMENT",
            "CONFLICT_ARBITRATION",
        ]

        record = EvidenceRecord(
            evidence_id=ev_id,
            source_observations=obs_ids,
            derived_from=derived,
            evidence_quality=quality,
            lineage_path=steps,
        )
        self._records[ev_id] = record
        return record

    def calculate_evidence_quality(
        self,
        observations: List[CanonicalObservation],
        conflicts: List[ConflictRecord],
    ) -> float:
        """
        Calculates normalized evidence quality [0.0 - 1.0].
        Formula:
          0.35 * mean_source_reliability
        + 0.25 * completeness
        + 0.20 * freshness
        + 0.20 * (1.0 - max_conflict_severity)
        """
        if not observations:
            return 0.0

        # 1. Mean Source Reliability
        reliabilities = [self.registry.get_source(o.source_id).reliability for o in observations]
        mean_rel = sum(reliabilities) / len(reliabilities)

        # 2. Field Completeness
        completeness_scores = []
        for o in observations:
            fields_present = 0
            if o.position:
                fields_present += 1
            if o.velocity:
                fields_present += 1
            if o.event_type:
                fields_present += 1
            if o.entity_hint:
                fields_present += 1
            completeness_scores.append(fields_present / 4.0)
        mean_completeness = sum(completeness_scores) / len(completeness_scores)

        # 3. Freshness (based on observation quality/staleness)
        freshness_scores = [o.quality for o in observations]
        mean_freshness = sum(freshness_scores) / len(freshness_scores)

        # 4. Conflict Absence
        max_conflict_sev = max([c.severity for c in conflicts], default=0.0)
        conflict_factor = max(0.0, 1.0 - max_conflict_sev)

        # Linear weighted combination
        quality = (
            (0.35 * mean_rel)
            + (0.25 * mean_completeness)
            + (0.20 * mean_freshness)
            + (0.20 * conflict_factor)
        )
        return round(max(0.0, min(1.0, quality)), 4)

    def get_record(self, evidence_id: str) -> Optional[EvidenceRecord]:
        """Retrieve stored evidence record by ID."""
        return self._records.get(evidence_id)
