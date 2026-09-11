"""
Phase 8 Relationship Change Detection for NETRA Knowledge Graph.
Detects state and strength changes between two temporal graph snapshots.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from config import NetraConfig, default_config
from models.knowledge_graph import (
    RelationshipChange,
    RelationshipChangeType,
    RelationshipDetail,
    RelationshipStatus,
)
from graph.relationship_intelligence import RelationshipIntelligenceEngine


class RelationshipChangeEngine:
    """
    Compares graph relationships evaluated at T1 vs T2 and detects structured deltas.
    """

    def __init__(
        self,
        rel_engine: RelationshipIntelligenceEngine,
        config: Optional[NetraConfig] = None,
    ) -> None:
        self.rel_engine = rel_engine
        self.config = config or default_config

    def detect_changes(
        self,
        t1: datetime,
        t2: datetime,
        entity_id: Optional[str] = None,
    ) -> List[RelationshipChange]:
        """
        Detects relationship modifications between timestamp t1 and t2.
        """
        rels_t1 = self.rel_engine.evaluate_all_relationships(as_of=t1)
        rels_t2 = self.rel_engine.evaluate_all_relationships(as_of=t2)

        # Map by canonical pair key (min(src, tgt), max(src, tgt))
        map_t1: Dict[Tuple[str, str], RelationshipDetail] = {
            tuple(sorted([r.source_entity_id, r.target_entity_id])): r for r in rels_t1
        }
        map_t2: Dict[Tuple[str, str], RelationshipDetail] = {
            tuple(sorted([r.source_entity_id, r.target_entity_id])): r for r in rels_t2
        }

        all_keys = sorted(list(set(map_t1.keys()).union(set(map_t2.keys()))))
        changes: List[RelationshipChange] = []

        cfg = self.config.relationship_intelligence
        strengthen_thresh = cfg.strengthening_delta_threshold
        weaken_thresh = cfg.weakening_delta_threshold

        for pair in all_keys:
            src, tgt = pair
            if entity_id and entity_id not in (src, tgt):
                continue

            rel_str = f"{src} <-> {tgt}"
            in_t1 = pair in map_t1
            in_t2 = pair in map_t2

            if not in_t1 and in_t2:
                # ADDED
                r2 = map_t2[pair]
                changes.append(
                    RelationshipChange(
                        entity_id=src,
                        change=RelationshipChangeType.ADDED,
                        relationship=rel_str,
                        previous_strength=None,
                        current_strength=r2.strength,
                        supporting_evidence=r2.supporting_evidence,
                        detected_at=t2,
                    )
                )
            elif in_t1 and not in_t2:
                # REMOVED
                r1 = map_t1[pair]
                changes.append(
                    RelationshipChange(
                        entity_id=src,
                        change=RelationshipChangeType.REMOVED,
                        relationship=rel_str,
                        previous_strength=r1.strength,
                        current_strength=None,
                        supporting_evidence=r1.supporting_evidence,
                        detected_at=t2,
                    )
                )
            elif in_t1 and in_t2:
                r1 = map_t1[pair]
                r2 = map_t2[pair]

                # Check REACTIVATED
                if r1.status == RelationshipStatus.STALE and r2.status in (RelationshipStatus.ACTIVE, RelationshipStatus.PERSISTENT):
                    changes.append(
                        RelationshipChange(
                            entity_id=src,
                            change=RelationshipChangeType.REACTIVATED,
                            relationship=rel_str,
                            previous_strength=r1.strength,
                            current_strength=r2.strength,
                            supporting_evidence=r2.supporting_evidence,
                            detected_at=t2,
                        )
                    )
                # Check BECAME_STALE
                elif r1.status != RelationshipStatus.STALE and r2.status == RelationshipStatus.STALE:
                    changes.append(
                        RelationshipChange(
                            entity_id=src,
                            change=RelationshipChangeType.BECAME_STALE,
                            relationship=rel_str,
                            previous_strength=r1.strength,
                            current_strength=r2.strength,
                            supporting_evidence=r2.supporting_evidence,
                            detected_at=t2,
                        )
                    )
                # Check BECAME_DISPUTED
                elif not r1.is_disputed and r2.is_disputed:
                    changes.append(
                        RelationshipChange(
                            entity_id=src,
                            change=RelationshipChangeType.BECAME_DISPUTED,
                            relationship=rel_str,
                            previous_strength=r1.strength,
                            current_strength=r2.strength,
                            supporting_evidence=r2.contradicting_evidence,
                            detected_at=t2,
                        )
                    )
                # Check RESOLVED
                elif r1.is_disputed and not r2.is_disputed:
                    changes.append(
                        RelationshipChange(
                            entity_id=src,
                            change=RelationshipChangeType.RESOLVED,
                            relationship=rel_str,
                            previous_strength=r1.strength,
                            current_strength=r2.strength,
                            supporting_evidence=r2.supporting_evidence,
                            detected_at=t2,
                        )
                    )
                # Check STRENGTHENED
                elif r2.strength - r1.strength >= strengthen_thresh:
                    changes.append(
                        RelationshipChange(
                            entity_id=src,
                            change=RelationshipChangeType.STRENGTHENED,
                            relationship=rel_str,
                            previous_strength=r1.strength,
                            current_strength=r2.strength,
                            supporting_evidence=r2.supporting_evidence,
                            detected_at=t2,
                        )
                    )
                # Check WEAKENED
                elif r1.strength - r2.strength >= weaken_thresh:
                    changes.append(
                        RelationshipChange(
                            entity_id=src,
                            change=RelationshipChangeType.WEAKENED,
                            relationship=rel_str,
                            previous_strength=r1.strength,
                            current_strength=r2.strength,
                            supporting_evidence=r2.supporting_evidence,
                            detected_at=t2,
                        )
                    )

        return sorted(changes, key=lambda c: (c.entity_id, c.change.value, c.relationship))
