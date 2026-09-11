"""
Event Clustering Engine for NETRA Intelligence Core.
Groups strongly correlated events into coherent operational activity clusters.
Calculates cluster-level features, spatial extents, cohesion metrics, and average threat indicators.
"""

from typing import List, Dict, Set, Optional, Any
from collections import defaultdict
from config import NetraConfig, default_config
from models.common import SeverityLevel
from models.event_intelligence import CanonicalEvent, EventCorrelation, EventCluster
from events.spatial import SpatialIntelligence


class EventClusterer:
    """Deterministic event clustering engine based on graph-link correlation."""

    def __init__(self, config: Optional[NetraConfig] = None):
        self.cfg = config or default_config
        self.spatial_intel = SpatialIntelligence(self.cfg)

    def cluster_events(
        self,
        events: List[CanonicalEvent],
        correlations: List[EventCorrelation],
    ) -> List[EventCluster]:
        """
        Group events into clusters based on strong correlation links (>= min_correlation_for_link).
        """
        if len(events) < self.cfg.clustering.min_cluster_size:
            return []

        min_score = self.cfg.clustering.min_correlation_for_link

        # Build adjacency graph of strong correlation links
        adj: Dict[str, Set[str]] = defaultdict(set)
        pair_scores: Dict[tuple, float] = {}

        for corr in correlations:
            if corr.correlation_score >= min_score:
                adj[corr.source_event_id].add(corr.target_event_id)
                adj[corr.target_event_id].add(corr.source_event_id)
                pair_scores[(corr.source_event_id, corr.target_event_id)] = corr.correlation_score
                pair_scores[(corr.target_event_id, corr.source_event_id)] = corr.correlation_score

        # Find connected components
        visited: Set[str] = set()
        components: List[List[str]] = []
        event_dict: Dict[str, CanonicalEvent] = {e.event_id: e for e in events}

        for ev_id in sorted(event_dict.keys()):
            if ev_id not in visited and ev_id in adj:
                component: List[str] = []
                queue = [ev_id]
                visited.add(ev_id)

                while queue:
                    curr = queue.pop(0)
                    component.append(curr)
                    for neighbor in sorted(adj[curr]):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                if len(component) >= self.cfg.clustering.min_cluster_size:
                    components.append(component)

        # Build EventCluster objects
        clusters: List[EventCluster] = []
        for idx, comp in enumerate(components, 1):
            comp_events = [event_dict[eid] for eid in comp]
            sorted_comp = sorted(comp_events, key=lambda e: e.timestamp)

            cluster_id = f"CLUSTER-SYNTH-{idx:03d}"
            event_ids = [e.event_id for e in sorted_comp]

            unique_entities = sorted(list({
                ent for e in sorted_comp for ent in e.entity_ids
            }))
            event_types = sorted(list({e.event_type for e in sorted_comp}))

            start_time = sorted_comp[0].timestamp
            end_time = sorted_comp[-1].timestamp
            duration_seconds = max(0.0, (end_time - start_time).total_seconds())

            # Spatial extent
            extent = self.spatial_intel.compute_spatial_extent([e.location for e in sorted_comp])

            # Cohesion score: average pairwise correlation in cluster
            internal_scores = []
            for i in range(len(comp)):
                for j in range(i + 1, len(comp)):
                    pair = (comp[i], comp[j])
                    if pair in pair_scores:
                        internal_scores.append(pair_scores[pair])

            cohesion = (
                round(sum(internal_scores) / len(internal_scores), 4)
                if internal_scores
                else round(min_score, 4)
            )

            # Average metrics
            activities = [float(e.attributes.get("activity_level", 0.3)) for e in sorted_comp]
            avg_risk = round(min(1.0, max(0.05, sum(activities) / len(activities))), 2)
            avg_conf = round(min(1.0, max(0.50, cohesion * 0.95)), 2)

            if avg_risk < 0.25:
                avg_sev = SeverityLevel.LOW
            elif avg_risk < 0.50:
                avg_sev = SeverityLevel.MEDIUM
            elif avg_risk < 0.75:
                avg_sev = SeverityLevel.HIGH
            else:
                avg_sev = SeverityLevel.CRITICAL

            clusters.append(
                EventCluster(
                    cluster_id=cluster_id,
                    event_ids=event_ids,
                    event_count=len(event_ids),
                    unique_entities=unique_entities,
                    event_types=event_types,
                    start_time=start_time,
                    end_time=end_time,
                    duration_seconds=duration_seconds,
                    spatial_extent=extent,
                    cohesion_score=cohesion,
                    average_risk=avg_risk,
                    average_confidence=avg_conf,
                    average_severity=avg_sev,
                )
            )

        return clusters
