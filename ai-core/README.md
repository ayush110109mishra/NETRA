# NETRA Intelligence Core — Phase 6: Predictive Intelligence & Forecasting

**ASTRAVEDA | Defence Intelligence Platform**  
**Engineering Domain**: AI / ML / Intelligence Core (ATUL)  
**Status**: `VERIFIED & OPERATIONAL`  
**Test Suite**: `248 Passed, 0 Failed` (100% Pass Rate across Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, & Phase 6)  
**Data Classification**: `SYNTHETIC / DEMO` (Zero real-world operational or classified data)

---

## 1. Executive Summary & Core Philosophy

NETRA is an AI-powered defence intelligence platform designed to transform heterogeneous operational telemetry into a unified, explainable intelligence picture.

NETRA's core product philosophy is:
> **NETRA is not a map application.**  
> **The map provides geographic context (WHERE); NETRA's Intelligence Core is the actual product (WHAT, WHO, HOW IMPORTANT, WHY, and WHAT NEXT).**

* **Phase 1 (MVP)**: Single-event intelligence, severity assessment, confidence bounds, and risk modeling.
* **Phase 2 (Event Intelligence)**: Multi-event correlation, spatio-temporal clustering, deduplication, pattern recognition, and baseline drift.
* **Phase 3 (Entity Intelligence)**: Comprehensive Entity-Centric Intelligence, Focus Mode (`GET /api/v1/intelligence/entities/{entity_id}`), behavioral profiling, and four-tier epistemic assessments.
* **Phase 4 (Advanced Anomaly & Risk Intelligence)**: Multi-dimensional anomaly detection across 8 analytical dimensions, mathematical factor attribution, persistence lifecycle tracking, explainable `phase4-v1` risk modeling with hysteresis buffering, decoupled confidence calibration, sector heat indexing, and geospatial hotspot clustering.
* **Phase 5 (Multi-Source Intelligence Fusion)**: Heterogeneous sensor ingestion, source registry & health monitoring, normalization with audit traces, temporal & spatial alignment, deterministic entity resolution, cross-source corroboration without double counting, contradiction detection & claim preservation, immutable evidence ledgering, weighted consensus fusion, and seamless Phase 4 integration.
* **Phase 6 (Predictive Intelligence & Forecasting)**: Probabilistic and uncertainty-aware future state projection (`ACTIVITY_STATE`, `ANOMALY_STATE`, `RISK_TREND`, `SPATIAL_STATE`, `EVENT_TYPE_RECURRENCE`, `BEHAVIORAL_STATE`) over configurable horizons (`SHORT`: 15–30m, `MEDIUM`: 1–6h, `LONG`: 12–24h), cold-start gating (< 3 events $\to$ `UNKNOWN`, $\le 0.30$ confidence), regime shift detection ($\Delta\text{slope} \ge 0.20$), multi-strategy ensemble forecasting (`Persistence`, `Trend`, `Recurrence`), 7-factor linear probability calibration, quantified residual uncertainty intervals, and a 5-tier epistemic ledger (`OBSERVED`, `FUSED`, `INFERRED`, `PREDICTED`, `UNCERTAIN`).

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
│   ├── dependencies.py              # FastAPI providers (EntityRepository, AnomalyEngine, FusionEngine, PredictionEngine)
│   └── routes/
│       ├── health.py                # GET /health, GET /api/v1/health
│       ├── intelligence.py          # Phase 1, Phase 2, and Phase 3 API routes
│       ├── anomaly.py               # Phase 4 Anomaly & Risk API routes
│       ├── fusion.py                # Phase 5 Multi-Source Fusion API routes
│       └── prediction.py            # Phase 6 Predictive Intelligence API routes
├── config.py                        # Centralized thresholds, weights, and horizons (v6.0.0)
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
│   ├── entity_intelligence.py       # Master Phase 3 Entity Intelligence Orchestrator
│   ├── event_intelligence.py        # Master Phase 2 Multi-Event Intelligence Orchestrator
│   ├── fusion_intelligence.py       # Master Phase 5 Fusion Intelligence & Phase 4 Bridge Orchestrator
│   ├── predictive_intelligence.py   # Master Phase 6 Predictive Intelligence Orchestrator
│   └── engine.py                    # Master Phase 1 Single-Event Pipeline Orchestrator
├── models/
│   ├── anomaly_intelligence.py      # Phase 4 Anomaly Schemas
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
├── simulation/
│   ├── synthetic_data.py            # Unified scenario catalogs and EntityRepository seeding
│   ├── fusion_scenarios.py          # 14 Phase 5 multi-source operational scenarios
│   └── prediction_scenarios.py      # 16 Phase 6 predictive operational scenarios
└── tests/                           # 68 test modules (248 automated tests, 100% passing)
```

---

## 3. Phase 6 Predictive Intelligence Pipeline

```text
HISTORICAL TELEMETRY (CanonicalEvents, EntityProfiles, FusedObservations, Phase 4 Anomalies)
         ↓
  TEMPORAL FILTERING (as_of evaluation timestamp; strictly eliminates future leakage)
         ↓
  TEMPORAL STATE SEQUENCE (Irregular interval representation, sampling regularity index)
         ↓
  TREND & REGIME DETECTION (Least-squares regression slope, direction, strength, persistence, regime shifts)
         ↓
  MULTI-DOMAIN FEATURE EXTRACTION (Temporal, Kinematic, Spatial, Behavioral, Anomaly, Risk, Fusion)
         ↓
  COLD-START & SUFFICIENCY GATING (< 3 events -> UNKNOWN, <= 0.30 conf; 3-5 events -> LIMITED, <= 0.55 conf)
         ↓
  MULTI-STRATEGY ENSEMBLE FORECAST (Persistence, Trend Extrapolation, Recurrence)
         ↓
  ENSEMBLE MODEL AGREEMENT (Unanimous=1.0, Majority=0.70, Divergent=0.35)
         ↓
  7-FACTOR PROBABILITY ESTIMATION (Bounded [0.0, 1.0], strictly normalized weights)
         ↓
  UNCERTAINTY & INTERVAL ESTIMATION (Depth, Volatility, Regime Shift, Sensor Conflict penalties)
         ↓
  FIVE-TIER EPISTEMIC ASSESSMENT (OBSERVED, FUSED, INFERRED, PREDICTED, UNCERTAIN)
         ↓
  EXPLAINABLE DOSSIER (Narrative, Supporting Factors, Limiting Factors, Invalidation Conditions)
         ↓
  REST JSON API (Deterministic responses across 7 endpoints)
```

---

## 4. Mathematical Formulations

### 4.1 Least-Squares Linear Trend
$$\text{slope} = \frac{\sum_{i=0}^{n-1} (i - \bar{x})(y_i - \bar{y})}{\sum_{i=0}^{n-1} (i - \bar{x})^2}, \quad \text{strength} = |r| = \frac{\sum (i - \bar{x})(y_i - \bar{y})}{n \cdot \sigma_x \cdot \sigma_y}$$

### 4.2 Operational Regime Shift
$$\text{acceleration} = \text{slope}_{\text{second\_half}} - \text{slope}_{\text{first\_half}}$$
$$\text{is\_regime\_change} = \text{True} \iff |\text{acceleration}| \ge 0.20$$

### 4.3 7-Factor Linear Forecast Probability
$$\text{Probability} = w_1 \text{Recurrence} + w_2 \text{TrendStrength} + w_3 \text{Persistence} + w_4 \text{EvidenceQuality} + w_5 \text{FusionConf} + w_6 \text{DataCompleteness} + w_7 \text{ModelAgreement}$$
* Weights: `recurrence=0.25`, `trend_strength=0.20`, `persistence=0.15`, `evidence_quality=0.15`, `fusion_confidence=0.10`, `data_completeness=0.10`, `model_agreement=0.05` (Sum = 1.00).

### 4.4 Residual Uncertainty & Interval Bounds
$$\text{Uncertainty} = \text{base} + \text{pen}_{\text{history}} + \text{pen}_{\text{volatility}} + \text{pen}_{\text{conflict}} + \text{pen}_{\text{regime}} + \text{pen}_{\text{disagreement}}$$
$$\text{Interval}_{\text{half}} = \max(0.04, \text{Uncertainty} \times 0.25)$$
$$[\text{lower}, \text{upper}] = [\max(0.0, P - \text{Interval}_{\text{half}}), \min(1.0, P + \text{Interval}_{\text{half}})]$$

---

## 5. Phase 6 API Reference

Mounted under `/api/v1/intelligence`:

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/intelligence/predictions/analyze` | **Master Phase 6 Endpoint**: Multi-strategy future-state projection & 5-tier epistemic ledger |
| `GET` | `/api/v1/intelligence/entities/{entity_id}/predictions` | Chronological history of generated predictions for an entity |
| `GET` | `/api/v1/intelligence/entities/{entity_id}/forecast` | Synchronized multi-target dashboard forecast across all 6 analytical dimensions |
| `GET` | `/api/v1/intelligence/predictions/history` | Global prediction logs with optional `entity_id` filtering |
| `GET` | `/api/v1/intelligence/predictions/evaluation` | Aggregate synthetic forecasting accuracy (MAE and directional accuracy) |
| `GET` | `/api/v1/intelligence/predictions/scenarios` | Catalog of 16 predefined predictive operational test scenarios |
| `POST` | `/api/v1/intelligence/predictions/scenarios/{id}/analyze` | Execute any predefined Phase 6 scenario directly |

---

## 6. 16 Predefined Phase 6 Scenarios

1. **`scenario_1_stable_entity`**: Consistent nominal activity; projects `STABLE` state with high model agreement.
2. **`scenario_2_escalating_activity`**: Monotonically rising activity; projects `INCREASING` state with positive slope.
3. **`scenario_3_decaying_risk`**: Tactical resolution with falling threat score; projects `FALLING` risk trend.
4. **`scenario_4_cyclical_patrol`**: Periodic waypoint check recurrence; projects `RECURRING` event recurrence state.
5. **`scenario_5_regime_shift`**: Abrupt behavioral surge breaking baseline ($\Delta\text{slope} \ge 0.20$); projects `REGIME_CHANGE`.
6. **`scenario_6_cold_start_entity`**: Newly detected entity ($< 3$ events); safely projects `UNKNOWN` with confidence $\le 0.30$.
7. **`scenario_7_limited_history`**: 4 observations recorded; confidence capped at $\le 0.55$.
8. **`scenario_8_high_sensor_conflict`**: Contradictory sensor inputs widen uncertainty intervals and dampen confidence.
9. **`scenario_9_unanimous_ensemble`**: 100% agreement across candidate strategies (`Persistence`, `Trend`, `Recurrence`).
10. **`scenario_10_divergent_ensemble`**: High metric oscillation triggers `VOLATILE` projection and penalizes agreement.
11. **`scenario_11_sensor_dropout`**: 8-hour telemetry dropout before evaluation increases temporal uncertainty.
12. **`scenario_12_burst_activity`**: Rapid pulse of 8 events in 2 minutes evaluated for instantaneous rate surge.
13. **`scenario_13_spatial_loitering`**: Low-speed circular trajectory classified as `LOITERING`.
14. **`scenario_14_directed_incursion`**: Sustained high-speed vector transit classified as `DIRECTED_TRANSIT`.
15. **`scenario_15_spurious_anomaly`**: Isolated single-point spike rejected by trend engine; avoids false-alarm escalation.
16. **`scenario_16_mixed_quality_forecast`**: Heterogeneous sensors produce calibrated confidence and empirical bounds.

---

## 7. Verification & Strict Determinism Guarantee

Run the complete test suite across all 6 phases:

```powershell
$env:PYTHONPATH="ai-core"
py -3.12 -m pytest ai-core/tests -q
```

**Results**: `248 passed, 5 warnings in 17.53s` (100% pass rate).

### Strict 50-Run Bit-for-Bit Determinism Guarantee
The automated test `test_strict_50_run_determinism` in `test_prediction_api.py` executes 50 consecutive runs against `POST /api/v1/intelligence/predictions/analyze` under a fixed reference timestamp (`as_of`) and asserts bit-for-bit identical SHA-256 hashes across all 50 iterations:
* Trend metrics (slope, strength, persistence, volatility, regime shift) are bit-for-bit identical.
* Candidate model forecasts and model agreement ratios are bit-for-bit identical.
* Feature engineering items and normalized values are bit-for-bit identical.
* Estimated probabilities, confidence scores, and uncertainty intervals are bit-for-bit identical.
* 5-tier epistemic ledger statements (`OBSERVED`, `FUSED`, `INFERRED`, `PREDICTED`, `UNCERTAIN`) are bit-for-bit identical.
* Generated prediction identifiers and provenance metadata are bit-for-bit identical.
**Outcome: 50/50 Bit-for-Bit Identical.**
