# NETRA Intelligence Core — Phase 7: Ask NETRA

**ASTRAVEDA | Defence Intelligence Platform**  
**Engineering Domain**: AI / ML / Python Intelligence Core (ATUL)  
**Status**: `VERIFIED & OPERATIONAL`  
**Test Suite**: `309 Passed, 0 Failed` (100% Pass Rate across Phases 1 through 7)  
**Data Classification**: `SYNTHETIC / DEMO` (Zero real-world operational or classified data)

---

## 1. Executive Summary & Core Philosophy

NETRA is an AI-powered defence intelligence platform designed to transform heterogeneous operational telemetry into a unified, explainable intelligence picture.

NETRA's core product philosophy is:
> **NETRA is not a map application.**  
> **The map provides geographic context (WHERE); NETRA's Intelligence Core is the actual product (WHAT, WHO, HOW IMPORTANT, WHY, WHAT NEXT, and HOW TO QUERY).**

* **Phase 1 (MVP)**: Single-event intelligence, severity assessment, confidence bounds, and risk modeling.
* **Phase 2 (Event Intelligence)**: Multi-event correlation, spatio-temporal clustering, deduplication, pattern recognition, and baseline drift.
* **Phase 3 (Entity Intelligence)**: Comprehensive Entity-Centric Intelligence, Focus Mode (`GET /api/v1/intelligence/entities/{entity_id}`), behavioral profiling, and four-tier epistemic assessments.
* **Phase 4 (Advanced Anomaly & Risk Intelligence)**: Multi-dimensional anomaly detection across 8 analytical dimensions, mathematical factor attribution, persistence lifecycle tracking, explainable `phase4-v1` risk modeling with hysteresis buffering, decoupled confidence calibration, sector heat indexing, and geospatial hotspot clustering.
* **Phase 5 (Multi-Source Intelligence Fusion)**: Heterogeneous sensor ingestion, source registry & health monitoring, normalization with audit traces, temporal & spatial alignment, deterministic entity resolution, cross-source corroboration without double counting, contradiction detection & claim preservation, immutable evidence ledgering, weighted consensus fusion, and seamless Phase 4 integration.
* **Phase 6 (Predictive Intelligence & Forecasting)**: Probabilistic and uncertainty-aware future state projection (`ACTIVITY_STATE`, `ANOMALY_STATE`, `RISK_TREND`, `SPATIAL_STATE`, `EVENT_TYPE_RECURRENCE`, `BEHAVIORAL_STATE`) over configurable horizons (`SHORT`: 15–30m, `MEDIUM`: 1–6h, `LONG`: 12–24h), cold-start gating (< 3 events $\to$ `UNKNOWN`, $\le 0.30$ confidence), regime shift detection ($\Delta\text{slope} \ge 0.20$), multi-strategy ensemble forecasting (`Persistence`, `Trend`, `Recurrence`), 7-factor linear probability calibration, and quantified residual uncertainty intervals.
* **Phase 7 (Ask NETRA — Natural Language Intelligence & Query Reasoning Engine)**: Structured, explainable, evidence-grounded natural-language query reasoning engine over the Phase 1–6 core. Translates operator questions into structured execution plans, runs deterministic engine steps, organizes evidence into a 5-tier Epistemic Ledger (`OBSERVED`, `FUSED`, `INFERRED`, `PREDICTED`, `UNCERTAIN`), grounds 100% of claims with concrete evidence IDs, supports follow-up conversational context (pronouns/entities), and guarantees zero hallucination.

---

## 2. System Architecture & Directory Layout

```text
ai-core/
├── anomaly/                         # Phase 4 Multi-Dimensional Anomaly Detection Engine
│   ├── aggregation.py               # Linear weighted combination + cross-dimensional synergy bonus
│   ├── attribution.py               # Exact mathematical factor attribution
│   ├── behavioral.py                # Composite behavioral drift & posture escalation detector
│   ├── calibration.py               # Decoupled confidence calibrator with contradiction & cold-start caps
│   ├── contextual.py                # Environmental dissonance & restricted operating zone detector
│   ├── engine.py                    # Master AnomalyEngine orchestrating all 8 dimensions
│   ├── event_type.py                # Novel critical/benign event types & rare category surge detector
│   ├── frequency.py                 # Cadence, burst density & operational silence detector
│   ├── kinematic.py                 # Velocity spikes, over-speed & implied velocity detector
│   ├── persistence.py               # Persistence state machine
│   ├── relational.py                # Network rendezvous & cluster shift detector
│   ├── spatial.py                   # Boundary breaches, centroid distance & teleportation detector
│   └── trend.py                     # Rate of change & trajectory analyzer
├── api/
│   ├── dependencies.py              # FastAPI providers (EntityRepository, Engines, AskNetraEngine)
│   └── routes/
│       ├── health.py                # GET /health, GET /api/v1/health
│       ├── intelligence.py          # Phase 1, Phase 2, and Phase 3 API routes
│       ├── anomaly.py               # Phase 4 Anomaly & Risk API routes
│       ├── fusion.py                # Phase 5 Multi-Source Fusion API routes
│       ├── prediction.py            # Phase 6 Predictive Intelligence API routes
│       └── ask.py                   # Phase 7 Ask NETRA Natural Language API routes
├── config.py                        # Centralized thresholds, weights, and AskNetraConfig (v7.0.0)
├── entities/                        # Phase 3 Entity Intelligence Components
│   ├── baseline.py                  # Behavioral baseline engine with cold-start gating (< 3 events)
│   ├── change_detection.py          # Behavioral change detector
│   ├── confidence.py                # Multi-dimensional entity confidence engine
│   ├── network.py                   # Relational network graph builder & cluster extractor
│   ├── profile.py                   # High-level entity profile aggregator
│   ├── repository.py                # In-memory CanonicalEntity & CanonicalEvent repository
│   └── spatial_behavior.py          # Geographic centroid, bounding radius km, spatial concentration
├── events/                          # Phase 2 Multi-Event Intelligence Components
│   ├── clustering.py                # Cohesion-based event clustering engine
│   ├── correlation.py               # Multi-dimensional correlation (temporal, spatial, entity, type, attr)
│   └── deduplication.py             # Exact & near-duplicate detection with audit trail
├── fusion/                          # Phase 5 Multi-Source Intelligence Fusion Engine
│   ├── conflict.py                  # Contradiction detection, claim preservation & arbitration
│   ├── corroboration.py             # Cross-source corroboration & independence clustering
│   ├── engine.py                    # Master FusionEngine orchestrating multi-source pipeline
│   ├── entity_resolution.py         # Deterministic track/alias matching to synthetic entities
│   ├── evidence.py                  # Immutable evidence ledger & evidence quality scoring
│   ├── fusion.py                    # Weighted consensus mathematical fusion & uncertainty estimation
│   ├── normalization.py             # Canonical normalizer with field aliases & unit conversions
│   ├── source_registry.py           # Catalog of registered sources, health & reliability monitoring
│   ├── spatial_alignment.py         # Haversine distance & uncertainty boundary overlap evaluation
│   └── temporal_alignment.py        # Timestamp proximity, clock skew & stale telemetry detection
├── intelligence/
│   ├── anomaly_intelligence.py      # Master Phase 4 Anomaly & Risk Intelligence Orchestrator
│   ├── ask_netra.py                 # Master Phase 7 Ask NETRA Engine & Session Orchestrator
│   ├── entity_intelligence.py       # Master Phase 3 Entity Intelligence Orchestrator
│   ├── event_intelligence.py        # Master Phase 2 Multi-Event Intelligence Orchestrator
│   ├── fusion_intelligence.py       # Master Phase 5 Fusion Intelligence & Phase 4 Bridge Orchestrator
│   ├── predictive_intelligence.py   # Master Phase 6 Predictive Intelligence Orchestrator
│   └── engine.py                    # Master Phase 1 Single-Event Pipeline Orchestrator
├── models/
│   ├── anomaly_intelligence.py      # Phase 4 Anomaly Schemas
│   ├── ask_netra.py                 # Phase 7 Ask NETRA Query, Plan, Evidence & Answer Schemas
│   ├── common.py                    # Coordinates, EntityStatus, Allegiance, EventSource
│   ├── entity_intelligence.py       # Phase 3 Entity Schemas
│   ├── error.py                     # Standardized APIError & APIErrorResponse envelope
│   ├── event_intelligence.py        # Phase 2 Event Schemas
│   ├── fusion_intelligence.py       # Phase 5 Fusion Schemas
│   ├── geo.py                       # Pure-Python Haversine distance calculations
│   ├── predictive_intelligence.py   # Phase 6 Predictive Intelligence Schemas
│   └── risk_intelligence.py         # Phase 4 Risk Schemas
├── prediction/                      # Phase 6 Predictive Intelligence & Forecasting Engine
│   ├── baseline_forecast.py         # Candidate strategies (Persistence, Trend, Recurrence)
│   ├── calibration.py               # Ensemble agreement calculation & synthetic MAE evaluation
│   ├── engine.py                    # Master PredictionEngine coordinating feature & forecast pipelines
│   ├── explainability.py            # Narrative justifications, factor attribution & 5-tier epistemic ledger
│   ├── feature_engineering.py       # Multi-dimensional feature extractor with full lineage
│   ├── forecasting.py               # ForecastingEngine managing cold start, strategies & calibration
│   ├── probability.py               # 7-factor linear probability estimation
│   ├── temporal_state.py            # Irregular time-series sequence builder & sampling regularity
│   ├── trend.py                     # Least-squares linear regression & regime change detector
│   └── uncertainty.py               # Residual uncertainty & heuristic confidence intervals
├── query/                           # Phase 7 Query Interpretation & Planning Subpackage
│   ├── engine.py                    # Master QueryInterpretationEngine coordinator
│   ├── entity_extractor.py          # Entity canonical ID, alias, sector, sensor & pronoun extractor
│   ├── executor.py                  # Multi-step query executor invoking P1–P6 engines
│   ├── filters.py                   # Severity, cutoff, event type & limit extractor
│   ├── intent.py                    # 16-intent deterministic regex & keyword classifier
│   ├── planner.py                   # DAG query plan builder generating inspectable steps
│   ├── time_parser.py               # Relative & absolute duration evaluator relative to as_of
│   └── validator.py                 # Entity recognition, ambiguity & kinetic safety validator
├── reasoning/                       # Phase 7 Evidence Grounding & Synthesis Subpackage
│   ├── engine.py                    # Master ReasoningEngine coordinator
│   ├── evidence.py                  # 5-tier Epistemic Ledger builder & citation indexer
│   ├── explanation.py               # Attribution ("Why?"), drift ("What changed?"), and comparisons
│   └── synthesis.py                 # Structured AskAnswer synthesizer with 100% grounded claims
├── simulation/
│   ├── synthetic_data.py            # Unified scenario catalogs and EntityRepository seeding
│   ├── fusion_scenarios.py          # 14 Phase 5 multi-source operational scenarios
│   ├── prediction_scenarios.py      # 16 Phase 6 predictive operational scenarios
│   └── ask_scenarios.py             # 20 Phase 7 Ask NETRA operational query scenarios
└── tests/                           # 79 test modules (309 automated tests, 100% passing)
```

---

## 3. Ask NETRA Pipeline Architecture

```text
OPERATOR NATURAL LANGUAGE QUERY
               ↓
query/intent.py (16 Intent Types: STATUS, PROFILE, RISK, ANOMALY, WHY, FORECAST, etc.)
               ↓
query/entity_extractor.py (Extracts ENTITY-XX, SECTOR-XX, RADAR-XX, and pronoun references)
               ↓
query/time_parser.py (Relative windows: "last 30 minutes", "past 6 hours", "last 24 hours")
               ↓
query/validator.py (Rejects ENTITY_NOT_FOUND, AMBIGUOUS_QUERY, UNSUPPORTED_QUERY)
               ↓
query/planner.py (Constructs inspectable multi-step DAG execution plan)
               ↓
query/executor.py (Executes steps against Phase 1–6 intelligence engines)
               ↓
reasoning/evidence.py (Extracts and tags evidence into 5 Epistemic Tiers)
               ↓
reasoning/explanation.py (Root cause attribution, longitudinal drift, comparative delta)
               ↓
reasoning/synthesis.py (Synthesizes headline, summary, key findings, and 100% grounded claims)
               ↓
intelligence/ask_netra.py (Coordinates session context, conversational memory, and caching)
               ↓
REST API: POST /api/v1/intelligence/ask (Deterministic output with strict audit provenance)
```

---

## 4. 16 Supported Query Intents

1. `STATUS`: Situational awareness and active entity track table overview.
2. `ENTITY_PROFILE`: Target classification, lifecycle state, observation span, and baseline.
3. `TIMELINE`: Chronological history of events and detections for a track or sector.
4. `WHAT_CHANGED`: Longitudinal behavioral baseline drift and operational state shift detection.
5. `ANOMALY`: 8-dimensional multivariate anomaly detection and factor attribution.
6. `RISK`: Explainable 7-factor composite risk assessment and operational posture rating.
7. `WHY`: Causal attribution and root cause explainability for elevated risk or anomalous states.
8. `TREND`: Longitudinal kinematic and activity trend direction, slope, and momentum.
9. `FORECAST`: Phase 6 probabilistic forecasting across multiple simulation horizons.
10. `SOURCE_SUPPORT`: Multi-sensor corroboration, reporting agreement, and source reliability scoring.
11. `CONFLICT`: Cross-sensor contradiction detection, telemetry discrepancies, and spatial mismatches.
12. `EVIDENCE`: Underlying raw observations, fused consensus tracks, and full epistemic audit trail.
13. `COMPARISON`: Side-by-side comparative operational analysis between two tracks.
14. `RELATIONSHIP`: Network topology, co-location clusters, and multi-entity associations.
15. `SCENARIO`: Execution and evaluation of synthetic operational exercise scenarios.
16. `HELP`: System capabilities, query syntax, and operational operator guidance.

---

## 5. Strict 5-Tier Epistemic Ledger

Every fact and conclusion returned by Ask NETRA is categorized into one of 5 strict epistemic tiers:
* **`OBSERVED`**: Direct raw sensor telemetry or event reports (`EVT-...`).
* **`FUSED`**: Cross-sensor corroborated consensus observations from Phase 5 (`FUS-...`).
* **`INFERRED`**: Derived analytical metrics such as anomaly scores (`ANM-...`) and composite risk (`RSK-...`).
* **`PREDICTED`**: Probabilistic forecasts and horizon states from Phase 6 (`PRD-...`).
* **`UNCERTAIN`**: Identified information gaps, contradictory telemetry, or cold-start limitations (`UNC-...`).

> [!IMPORTANT]
> **Zero Hallucination Guarantee**:
> Ask NETRA will never guess or invent data. Every proposition in `claims` must cite one or more structured evidence IDs from the ledger. When data is missing, conflicting, or cold-started, it is explicitly cataloged under `UNCERTAIN`.

---

## 6. Phase 7 REST API Reference

Mounted under `/api/v1/intelligence/ask`:

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/intelligence/ask` | **Primary Ask NETRA Query Endpoint**: Translates question, executes plan, returns grounded answer |
| `POST` | `/api/v1/intelligence/ask/parse` | Parse natural language query and return execution plan without running engines |
| `GET` | `/api/v1/intelligence/ask/capabilities` | Retrieve catalog of all 16 supported intents, epistemic tiers, and capabilities |
| `GET` | `/api/v1/intelligence/ask/examples` | Retrieve categorized example operational queries |
| `GET` | `/api/v1/intelligence/ask/scenarios` | List all 20 predefined operational test scenarios |
| `POST` | `/api/v1/intelligence/ask/scenarios/{id}` | Execute any predefined scenario directly by identifier |

---

## 7. Verification & Determinism Results

Run the complete regression suite across all 7 phases:

```powershell
$env:PYTHONPATH="ai-core"
py -3.12 -m pytest ai-core/tests -q
```

**Results**: `309 passed, 5 warnings in 32.69s` (100% pass rate).

### Strict 50-Run Bit-for-Bit Determinism Guarantee
The automated test `test_strict_50_run_determinism` in `test_ask_determinism.py` executes 50 consecutive runs against `POST /api/v1/intelligence/ask` under a fixed reference timestamp (`as_of`) and asserts bit-for-bit identical SHA-256 hashes across all 50 iterations:
* Parsed query representation and classification confidence are bit-for-bit identical.
* Execution plan steps and parameters are bit-for-bit identical.
* 5-tier epistemic ledger indexing and evidence references are bit-for-bit identical.
* Synthesized headline, key findings, and grounded claims are bit-for-bit identical.
* **Outcome: 50/50 Bit-for-Bit Identical.**
