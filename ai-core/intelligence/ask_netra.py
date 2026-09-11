"""
Phase 7 Master Ask NETRA Intelligence Engine.
Coordinates natural language query parsing, execution planning, deterministic engine execution,
5-tier epistemic ledgering, no-hallucination synthesis, and conversational session context.
"""

from datetime import datetime, timezone
import hashlib
import time
from typing import Any, Dict, List, Optional, Set

from config import NetraConfig, default_config
from entities.repository import EntityRepository
from intelligence.entity_intelligence import EntityIntelligenceEngine
from intelligence.anomaly_intelligence import AnomalyIntelligenceEngine
from intelligence.fusion_intelligence import FusionIntelligenceEngine
from intelligence.predictive_intelligence import PredictiveIntelligenceEngine
from models.ask_netra import (
    AskAnswer,
    AskNetraRequest,
    AskNetraResponse,
    CapabilitiesResponse,
    CapabilityItem,
    ClaimItem,
    EpistemicLedger,
    EpistemicTier,
    ExampleQueryItem,
    ExamplesResponse,
    ParsedQuery,
    ParseResponse,
    QueryIntent,
    QueryPlan,
    QueryValidationStatus,
)
from query.engine import QueryInterpretationEngine
from query.executor import QueryExecutor
from reasoning.engine import ReasoningEngine


class SessionState:
    """Conversational state container for a single session."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.active_entity_id: Optional[str] = None
        self.active_sector_id: Optional[str] = None
        self.last_intent: Optional[QueryIntent] = None
        self.turn_history: List[Dict[str, Any]] = []

    def update(
        self,
        entity_id: Optional[str],
        sector_id: Optional[str],
        intent: QueryIntent,
        query: str,
        answer_headline: str,
    ) -> None:
        if entity_id:
            self.active_entity_id = entity_id
        if sector_id:
            self.active_sector_id = sector_id
        self.last_intent = intent
        self.turn_history.append(
            {
                "query": query,
                "intent": intent.value,
                "entity_id": self.active_entity_id,
                "headline": answer_headline,
            }
        )
        if len(self.turn_history) > 10:
            self.turn_history.pop(0)


class AskNetraEngine:
    """Master orchestrator for Ask NETRA Natural Language Intelligence."""

    def __init__(
        self,
        config: Optional[NetraConfig] = None,
        repository: Optional[EntityRepository] = None,
        entity_engine: Optional[EntityIntelligenceEngine] = None,
        anomaly_engine: Optional[AnomalyIntelligenceEngine] = None,
        fusion_engine: Optional[FusionIntelligenceEngine] = None,
        prediction_engine: Optional[PredictiveIntelligenceEngine] = None,
    ):
        self.config = config or default_config
        self.repository = repository or EntityRepository(self.config.entity)
        self.entity_engine = entity_engine or EntityIntelligenceEngine(self.config, self.repository)
        self.anomaly_engine = anomaly_engine or AnomalyIntelligenceEngine(self.config, self.repository)
        self.fusion_engine = fusion_engine or FusionIntelligenceEngine(self.config, self.repository, self.anomaly_engine)
        self.prediction_engine = prediction_engine or PredictiveIntelligenceEngine(
            self.config, self.repository, self.anomaly_engine, self.fusion_engine
        )

        known_ids = set(self.repository._entities.keys()) | set(self.repository._entity_events.keys())
        self.query_interpreter = QueryInterpretationEngine(
            config=self.config,
            known_entity_ids=known_ids,
        )
        self.query_executor = QueryExecutor(
            config=self.config,
            repository=self.repository,
            entity_engine=self.entity_engine,
            anomaly_engine=self.anomaly_engine,
            fusion_engine=self.fusion_engine,
            prediction_engine=self.prediction_engine,
        )
        self.reasoning_engine = ReasoningEngine()
        self.sessions: Dict[str, SessionState] = {}

    def get_or_create_session(self, session_id: Optional[str]) -> SessionState:
        """Retrieves or creates a session context."""
        s_id = session_id or "default_session"
        if s_id not in self.sessions:
            self.sessions[s_id] = SessionState(s_id)
        return self.sessions[s_id]

    def clear_session(self, session_id: str) -> None:
        """Resets the conversational context of a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def ask(self, request: AskNetraRequest) -> AskNetraResponse:
        """
        Main query processing pipeline:
        Natural Language -> Interpret -> Validate -> Plan -> Execute -> Reason & Synthesize -> Response
        """
        start_time = time.perf_counter()

        ref_time = request.as_of or datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
        if ref_time.tzinfo is None:
            ref_time = ref_time.replace(tzinfo=timezone.utc)

        # Synchronize known entities
        all_ids = set(self.repository._entities.keys()) | set(self.repository._entity_events.keys())
        self.query_interpreter.update_known_entities(all_ids)

        # Session context
        session = self.get_or_create_session(request.session_id)
        effective_entity_id = request.active_entity_id or session.active_entity_id

        # 1. Interpret and Plan
        parsed, plan, val_status, val_msg = self.query_interpreter.interpret(
            query_text=request.query,
            session_entity_id=effective_entity_id,
            as_of=ref_time,
        )

        # 2. Validation Gating
        if val_status != QueryValidationStatus.VALID:
            # Build explainable validation rejection answer
            ledger = EpistemicLedger()
            answer = AskAnswer(
                headline=f"Query Gated: {val_status.value}",
                summary=val_msg or f"The query could not be processed due to validation status: {val_status.value}.",
                key_findings=[val_msg or "Validation check failed."],
                claims=[
                    ClaimItem(
                        statement=val_msg or "Query failed validation gating.",
                        epistemic_tier=EpistemicTier.UNCERTAIN,
                        supporting_evidence_ids=["VALIDATION-GATE"],
                        confidence=1.00,
                    )
                ],
                evidence_ledger=ledger,
                uncertainties=[val_msg or "Invalid query context."],
                caveats=["Provide an existing registered entity identifier or clarify the request."],
                overall_confidence=1.00,
            )
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return AskNetraResponse(
                schema_version="phase7-v1",
                query_id=parsed.query_id,
                session_id=session.session_id,
                as_of=ref_time,
                parsed_query=parsed,
                execution_plan=plan,
                answer=answer,
                execution_time_ms=elapsed_ms,
                provenance={
                    "validation_status": val_status.value,
                    "validation_message": val_msg,
                    "executed_steps": 0,
                },
            )

        # 3. Execute Plan
        exec_context = self.query_executor.execute_plan(plan, parsed, as_of=ref_time)

        # 4. Reason and Synthesize Answer
        answer, ledger = self.reasoning_engine.reason_and_synthesize(parsed, exec_context)

        # 5. Update Session Context
        resolved_ent = parsed.primary_entity_id or effective_entity_id
        session.update(
            entity_id=resolved_ent,
            sector_id=parsed.sector_id,
            intent=parsed.intent,
            query=request.query,
            answer_headline=answer.headline,
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return AskNetraResponse(
            schema_version="phase7-v1",
            query_id=parsed.query_id,
            session_id=session.session_id,
            as_of=ref_time,
            parsed_query=parsed,
            execution_plan=plan,
            answer=answer,
            execution_time_ms=elapsed_ms,
            provenance={
                "validation_status": val_status.value,
                "executed_steps": len(plan.steps),
                "evidence_count": ledger.total_evidence_count,
            },
        )

    def parse(
        self,
        query: str,
        session_id: Optional[str] = None,
        as_of: Optional[datetime] = None,
    ) -> ParseResponse:
        """Parses and generates execution plan without engine execution."""
        ref_time = as_of or datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
        if ref_time.tzinfo is None:
            ref_time = ref_time.replace(tzinfo=timezone.utc)

        all_ids = set(self.repository._entities.keys()) | set(self.repository._entity_events.keys())
        self.query_interpreter.update_known_entities(all_ids)
        session = self.get_or_create_session(session_id)

        parsed, plan, val_status, val_msg = self.query_interpreter.interpret(
            query_text=query,
            session_entity_id=session.active_entity_id,
            as_of=ref_time,
        )

        return ParseResponse(
            parsed_query=parsed,
            execution_plan=plan,
            validation_status=val_status,
            validation_message=val_msg,
        )

    def get_capabilities(self) -> CapabilitiesResponse:
        """Returns comprehensive catalog of supported query capabilities."""
        capabilities = [
            CapabilityItem(
                intent=QueryIntent.STATUS,
                description="High-level operational situational awareness and entity track table overview.",
                supported_engines=["event_engine", "entity_engine", "risk_engine"],
                example_queries=["What is the current operational situation?", "Status overview of Sector 1"],
            ),
            CapabilityItem(
                intent=QueryIntent.ENTITY_PROFILE,
                description="Comprehensive profile, classification, lifecycle, and baseline data for a track.",
                supported_engines=["entity_engine", "risk_engine"],
                example_queries=["Who is ENTITY-01?", "Show profile for ENTITY-02"],
            ),
            CapabilityItem(
                intent=QueryIntent.TIMELINE,
                description="Chronological event history and sequential telemetry timeline.",
                supported_engines=["event_engine"],
                example_queries=["Show timeline for ENTITY-01", "What happened with ENTITY-01 in the past 6 hours?"],
            ),
            CapabilityItem(
                intent=QueryIntent.WHAT_CHANGED,
                description="Longitudinal behavioral baseline drift and operational state shift detection.",
                supported_engines=["entity_engine", "anomaly_engine"],
                example_queries=["What changed with ENTITY-01?", "How has its baseline shifted?"],
            ),
            CapabilityItem(
                intent=QueryIntent.ANOMALY,
                description="8-dimensional multivariate anomaly detection and factor attribution.",
                supported_engines=["anomaly_engine"],
                example_queries=["Is ENTITY-01 anomalous?", "Show anomaly breakdown for ENTITY-03"],
            ),
            CapabilityItem(
                intent=QueryIntent.RISK,
                description="Explainable 7-factor composite risk assessment and operational posture rating.",
                supported_engines=["risk_engine", "anomaly_engine"],
                example_queries=["What is the risk level of ENTITY-01?", "Assess threat posture of ENTITY-02"],
            ),
            CapabilityItem(
                intent=QueryIntent.WHY,
                description="Causal attribution and explainability for elevated risk or anomalous states.",
                supported_engines=["risk_engine", "anomaly_engine"],
                example_queries=["Why is ENTITY-01 high risk?", "Why did its anomaly score increase?"],
            ),
            CapabilityItem(
                intent=QueryIntent.TREND,
                description="Longitudinal kinematic and activity trend direction, slope, and momentum.",
                supported_engines=["prediction_engine"],
                example_queries=["What is the speed trend for ENTITY-01?", "Is its activity increasing?"],
            ),
            CapabilityItem(
                intent=QueryIntent.FORECAST,
                description="Phase 6 probabilistic forecasting across multiple simulation horizons.",
                supported_engines=["prediction_engine"],
                example_queries=["What will ENTITY-01 do next?", "Forecast risk for ENTITY-02 over next 6 hours"],
            ),
            CapabilityItem(
                intent=QueryIntent.SOURCE_SUPPORT,
                description="Multi-sensor corroboration, reporting agreement, and source reliability scoring.",
                supported_engines=["fusion_engine"],
                example_queries=["Which sensors support ENTITY-01?", "What is the sensor corroboration for ENTITY-02?"],
            ),
            CapabilityItem(
                intent=QueryIntent.CONFLICT,
                description="Cross-sensor contradiction detection, telemetry discrepancies, and spatial mismatches.",
                supported_engines=["fusion_engine"],
                example_queries=["Are there sensor conflicts for ENTITY-01?", "Identify conflicting reports"],
            ),
            CapabilityItem(
                intent=QueryIntent.EVIDENCE,
                description="Underlying raw observations, fused consensus tracks, and full epistemic audit trail.",
                supported_engines=["fusion_engine", "event_engine"],
                example_queries=["What evidence supports ENTITY-01?", "Show telemetry lineage for ENTITY-01"],
            ),
            CapabilityItem(
                intent=QueryIntent.COMPARISON,
                description="Side-by-side comparative operational analysis between two tracks.",
                supported_engines=["entity_engine", "anomaly_engine", "risk_engine"],
                example_queries=["Compare ENTITY-01 to ENTITY-02", "Contrast ENTITY-01 and ENTITY-03"],
            ),
            CapabilityItem(
                intent=QueryIntent.RELATIONSHIP,
                description="Network topology, co-location clusters, and multi-entity associations.",
                supported_engines=["entity_engine", "event_engine"],
                example_queries=["Who is ENTITY-01 operating with?", "Show clusters for ENTITY-01"],
            ),
            CapabilityItem(
                intent=QueryIntent.SCENARIO,
                description="Execution and evaluation of synthetic operational exercise scenarios.",
                supported_engines=["simulation_engine"],
                example_queries=["Run scenario border intrusion", "Simulate rapid escalation drill"],
            ),
            CapabilityItem(
                intent=QueryIntent.HELP,
                description="System capabilities, query syntax, and operational guidance.",
                supported_engines=["reasoning_engine"],
                example_queries=["Help", "What can Ask NETRA do?", "Show capabilities"],
            ),
        ]

        return CapabilitiesResponse(
            schema_version="phase7-v1",
            supported_intents=capabilities,
            epistemic_tiers=[t.value for t in EpistemicTier],
            version="7.0.0",
        )

    def get_examples(self) -> ExamplesResponse:
        """Returns catalog of categorized operational query examples."""
        examples = [
            ExampleQueryItem(
                category="Situational Awareness",
                query="What is the current operational situation?",
                intent=QueryIntent.STATUS,
                description="Global overview of active entities and event counts",
            ),
            ExampleQueryItem(
                category="Entity Intelligence",
                query="Give me a profile for ENTITY-01",
                intent=QueryIntent.ENTITY_PROFILE,
                description="Dossier on target classification, state, and observation span",
            ),
            ExampleQueryItem(
                category="Anomaly Detection",
                query="Is ENTITY-01 anomalous?",
                intent=QueryIntent.ANOMALY,
                description="Evaluates 8 dimensions of anomalous behavior",
            ),
            ExampleQueryItem(
                category="Risk Assessment",
                query="What is the risk level of ENTITY-01?",
                intent=QueryIntent.RISK,
                description="Calculates explainable 7-factor risk score",
            ),
            ExampleQueryItem(
                category="Attribution",
                query="Why is ENTITY-01 high risk?",
                intent=QueryIntent.WHY,
                description="Causal factor breakdown of risk and anomaly drivers",
            ),
            ExampleQueryItem(
                category="Forecasting",
                query="What will ENTITY-01 do next?",
                intent=QueryIntent.FORECAST,
                description="Probabilistic future state projection across horizons",
            ),
            ExampleQueryItem(
                category="Multi-Source Fusion",
                query="Which sensors support ENTITY-01?",
                intent=QueryIntent.SOURCE_SUPPORT,
                description="Corroborating sensor modalities and fusion confidence",
            ),
            ExampleQueryItem(
                category="Sensor Conflicts",
                query="Are there any sensor conflicts for ENTITY-01?",
                intent=QueryIntent.CONFLICT,
                description="Discrepancies and contradictory reports",
            ),
            ExampleQueryItem(
                category="Comparative Analysis",
                query="Compare ENTITY-01 to ENTITY-02",
                intent=QueryIntent.COMPARISON,
                description="Side-by-side metric comparison between two tracks",
            ),
            ExampleQueryItem(
                category="Follow-up Continuation",
                query="What about its risk?",
                intent=QueryIntent.RISK,
                description="Pronoun continuation using prior session entity context",
            ),
        ]
        return ExamplesResponse(examples=examples)
