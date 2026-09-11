"""
Master Multi-Event Intelligence Orchestrator for NETRA Intelligence Core.
Coordinates canonical normalization, deduplication, candidate filtering,
multi-dimensional correlation, clustering, pattern detection, baseline drift analysis,
and structured assessment generation.
"""

import time
import hashlib
from datetime import datetime, timezone
from typing import Optional, List

from config import NetraConfig, default_config
from models.event_intelligence import (
    CanonicalEvent,
    MultiEventAnalyzeRequest,
    MultiEventAnalyzeResponse,
    StructuredAssessment,
)
from events.normalizer import EventNormalizer
from events.deduplication import EventDeduplicator
from events.correlation import MultiDimensionalCorrelator
from events.clustering import EventClusterer
from events.patterns import PatternDetector
from events.drift import BaselineDriftAnalyzer


class EventIntelligenceEngine:
    """Master engine for multi-event intelligence analysis."""

    def __init__(self, config: Optional[NetraConfig] = None):
        self.cfg = config or default_config
        self.normalizer = EventNormalizer()
        self.deduplicator = EventDeduplicator(self.cfg)
        self.correlator = MultiDimensionalCorrelator(self.cfg)
        self.clusterer = EventClusterer(self.cfg)
        self.pattern_detector = PatternDetector(self.cfg)
        self.drift_analyzer = BaselineDriftAnalyzer(self.cfg)

    def analyze_events(self, request: MultiEventAnalyzeRequest) -> MultiEventAnalyzeResponse:
        """
        Execute full Phase 2 multi-event intelligence pipeline.
        """
        start_time = time.perf_counter()

        # Step 1: Normalize all raw inputs to CanonicalEvents
        normalized_events: List[CanonicalEvent] = self.normalizer.normalize_batch(request.events)

        # Step 2: Deduplication Analysis
        duplicates = self.deduplicator.analyze_duplicates(normalized_events)

        # Step 3: Pairwise Multi-Dimensional Correlation
        correlations = self.correlator.correlate_all(normalized_events)

        # Step 4: Event Clustering
        clusters = self.clusterer.cluster_events(normalized_events, correlations)

        # Step 5: Pattern Detection
        patterns = self.pattern_detector.detect_patterns(normalized_events)

        # Step 6: Baseline Drift Analysis
        hist_baseline = request.context.historical_baseline_activity if request.context else None
        rec_baseline = request.context.recent_baseline_activity if request.context else None
        drift = self.drift_analyzer.analyze_drift(
            events=normalized_events,
            historical_baseline=hist_baseline,
            recent_baseline=rec_baseline,
        )

        # Step 7: Structured Assessment Generation (OBSERVED / INFERRED / UNCERTAIN)
        observed_facts = [
            f"{len(normalized_events)} synthetic events processed across sector timeline.",
            f"Active synthetic entities: {', '.join(sorted(list({ent for e in normalized_events for ent in e.entity_ids}))) or 'None specified'}.",
            f"Event categories observed: {', '.join(sorted(list({e.event_type for e in normalized_events})))}.",
        ]
        dup_count = sum(1 for d in duplicates if d.is_duplicate)
        if dup_count > 0:
            observed_facts.append(f"{dup_count} duplicate or near-duplicate transmissions detected.")

        inferred_intelligence = []
        if correlations:
            strongest = max(correlations, key=lambda c: c.correlation_score)
            inferred_intelligence.append(
                f"Peak multi-dimensional correlation: {strongest.correlation_score:.2f} ({strongest.strength.value}) "
                f"between {strongest.source_event_id} and {strongest.target_event_id}."
            )
        else:
            inferred_intelligence.append("No significant cross-event correlations detected above baseline.")

        if clusters:
            inferred_intelligence.append(
                f"Formed {len(clusters)} tactical activity cluster(s): "
                f"{', '.join(c.cluster_id + ' (' + str(c.event_count) + ' events)' for c in clusters)}."
            )

        if patterns:
            inferred_intelligence.append(
                f"Detected {len(patterns)} operational pattern(s): {', '.join(p.pattern_type for p in patterns)}."
            )

        if drift.direction != "STABLE":
            inferred_intelligence.append(drift.description)

        uncertainties = [
            "Correlation establishes evidence-backed association but does NOT prove causal linkage.",
            "Synthetic prototype values require corroborating sensor cross-validation.",
        ]
        if not request.context or request.context.historical_baseline_activity is None:
            uncertainties.append("Historical sector baseline was not explicitly provided; drift estimates rely on batch averages.")

        summary = (
            f"Processed {len(normalized_events)} events resulting in {len(correlations)} correlation links, "
            f"{len(clusters)} cluster(s), and {len(patterns)} behavioral pattern(s)."
        )

        assessment = StructuredAssessment(
            summary=summary,
            observed=observed_facts,
            inferred=inferred_intelligence,
            uncertain=uncertainties,
        )

        # Step 8: Deterministic analysis ID based on event IDs and timestamps
        id_seed = "_".join(e.event_id for e in normalized_events)
        hash_digest = hashlib.sha256(id_seed.encode("utf-8")).hexdigest()[:8].upper()
        analysis_id = f"ANL-MULTI-{hash_digest}"

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 3)

        return MultiEventAnalyzeResponse(
            analysis_id=analysis_id,
            timestamp=datetime.now(timezone.utc),
            event_count=len(normalized_events),
            normalized_events=normalized_events,
            duplicates=duplicates,
            correlations=correlations,
            clusters=clusters,
            patterns=patterns,
            baseline_drift=drift,
            assessment=assessment,
            metadata={
                "processing_time_ms": elapsed_ms,
                "data_classification": self.cfg.data_classification,
                "engine_version": self.cfg.version,
                "mode": self.cfg.mode,
            },
        )
