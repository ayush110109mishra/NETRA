"""
Cross-Source Corroboration Engine for NETRA Phase 5.
Evaluates multi-sensor agreement, clusters reporting feeds by independence_group,
and prevents duplicate retransmission double-counting.
"""

from typing import List, Optional
import logging

from models.fusion_intelligence import CanonicalObservation, CorroborationResult
from fusion.source_registry import SourceRegistry

logger = logging.getLogger("netra.fusion.corroboration")


class CorroborationEngine:
    """
    Measures degree of independent sensor corroboration.
    Distinguishes genuine independent consensus from redundant or duplicate feeds.
    """

    def __init__(self, source_registry: Optional[SourceRegistry] = None):
        self.registry = source_registry or SourceRegistry()

    def evaluate(
        self,
        observations: List[CanonicalObservation],
    ) -> CorroborationResult:
        """
        Assesses corroboration across a group of compatible observations.
        Identifies unique independence groups to compute calibrated corroboration score.
        """
        if not observations:
            return CorroborationResult(
                corroboration_score=0.0,
                supporting_sources=[],
                independent_source_count=0,
                duplicate_source_count=0,
                independence_groups=[],
                explanation="No observations provided for corroboration evaluation.",
            )

        source_ids = [obs.source_id for obs in observations]
        unique_sources = sorted(list(set(source_ids)))

        # Resolve independence group for each unique source
        source_group_map = {}
        for sid in unique_sources:
            src_meta = self.registry.get_source(sid)
            source_group_map[sid] = src_meta.independence_group

        unique_groups = sorted(list(set(source_group_map.values())))
        indep_count = len(unique_groups)
        dup_count = len(observations) - indep_count

        # Compute corroboration score based strictly on INDEPENDENT groups
        if indep_count <= 0:
            score = 0.0
            explanation = "Zero sources available."
        elif indep_count == 1:
            # Single independent sensor (even if multiple duplicate observations/retransmissions exist)
            score = 0.35
            if dup_count > 0:
                explanation = (
                    f"Single independent sensor group '{unique_groups[0]}' ({len(observations)} observations, "
                    f"{dup_count} duplicates detected). Corroboration capped at {score:.2f} to prevent double-counting."
                )
            else:
                explanation = f"Single independent source '{unique_groups[0]}' without corroboration (score={score:.2f})."
        elif indep_count == 2:
            score = 0.70
            explanation = (
                f"Dual-source independent corroboration across groups {unique_groups} "
                f"({dup_count} duplicate feeds filtered). Score={score:.2f}."
            )
        else:
            # 3 or more independent sources
            bonus = min(0.30, 0.15 + (0.05 * (indep_count - 3)))
            score = min(1.0, 0.70 + bonus)
            explanation = (
                f"Robust multi-source independent corroboration across {indep_count} groups "
                f"{unique_groups} ({dup_count} duplicate feeds filtered). Score={score:.2f}."
            )

        bounded_score = round(max(0.0, min(1.0, score)), 4)

        return CorroborationResult(
            corroboration_score=bounded_score,
            supporting_sources=unique_sources,
            independent_source_count=indep_count,
            duplicate_source_count=dup_count,
            independence_groups=unique_groups,
            explanation=explanation,
        )
