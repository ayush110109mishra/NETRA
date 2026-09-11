"""
Phase 7 Query Executor for Ask NETRA.
Executes plan steps against Phase 1-6 intelligence engines and returns structured execution contexts.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from config import NetraConfig, default_config
from models.ask_netra import ParsedQuery, QueryPlan, QueryValidationStatus
from models.anomaly_intelligence import AnomalyAnalyzeRequest
from models.fusion_intelligence import FusionAnalyzeRequest
from models.predictive_intelligence import PredictionAnalyzeRequest
from entities.repository import EntityRepository
from intelligence.entity_intelligence import EntityIntelligenceEngine
from intelligence.anomaly_intelligence import AnomalyIntelligenceEngine
from intelligence.fusion_intelligence import FusionIntelligenceEngine
from intelligence.predictive_intelligence import PredictiveIntelligenceEngine


class QueryExecutor:
    """Executes query plan steps against NETRA intelligence engines and collects artifacts."""

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

    def execute_plan(
        self,
        plan: QueryPlan,
        parsed: ParsedQuery,
        as_of: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Executes each step in the query plan sequentially, passing intermediate artifacts.
        Returns a dictionary containing all retrieved engine outputs, evidence records, and metrics.
        """
        execution_context: Dict[str, Any] = {
            "query_id": parsed.query_id,
            "intent": parsed.intent,
            "entity_id": parsed.primary_entity_id,
            "secondary_entity_id": parsed.secondary_entity_id,
            "sector_id": parsed.sector_id,
            "as_of": as_of or parsed.parsed_at,
            "step_outputs": {},
            "raw_events": [],
            "entity_profile": None,
            "secondary_profile": None,
            "anomaly_analysis": None,
            "risk_profile": None,
            "forecast_response": None,
            "fusion_analysis": None,
            "active_entities": [],
        }

        ref_time = as_of or parsed.parsed_at
        entity_id = parsed.primary_entity_id

        for step in plan.steps:
            engine_name = step.engine
            action = step.action
            output: Any = None

            try:
                if engine_name == "entity_engine":
                    if action == "get_profile" and entity_id:
                        tgt = step.parameters.get("entity_id", entity_id)
                        entity = self.repository.get_entity(tgt)
                        events = self.repository.get_events_for_entity(tgt)
                        output = {"entity": entity, "events_count": len(events)}
                        if tgt == entity_id:
                            execution_context["entity_profile"] = entity
                            execution_context["raw_events"] = events
                        else:
                            execution_context["secondary_profile"] = entity

                    elif action == "fetch_active_entities":
                        entities = self.repository.list_entities()
                        execution_context["active_entities"] = entities
                        output = {"count": len(entities)}

                    elif action == "get_baseline_drift" and entity_id:
                        entity = self.repository.get_entity(entity_id)
                        events = self.repository.get_events_for_entity(entity_id)
                        execution_context["entity_profile"] = entity
                        execution_context["raw_events"] = events
                        output = {"baseline": entity.attributes if entity else None}

                    elif action == "get_entity_clusters" and entity_id:
                        try:
                            resp = self.entity_engine.analyze_entity(entity_id, as_of=ref_time)
                            output = {"clusters": resp.cluster_memberships, "relationships": resp.relationships}
                        except Exception:
                            output = {"clusters": [], "relationships": []}

                elif engine_name == "event_engine":
                    if action in ("fetch_recent_events", "get_entity_timeline"):
                        if entity_id:
                            evts = self.repository.get_events_for_entity(entity_id)
                        else:
                            evts = self.repository.get_all_events()
                        execution_context["raw_events"] = evts
                        output = {"events_count": len(evts)}

                elif engine_name == "anomaly_engine":
                    if entity_id:
                        try:
                            req = AnomalyAnalyzeRequest(entity_id=entity_id, as_of=ref_time)
                            anom_resp = self.anomaly_engine.analyze_entity_anomaly(req)
                            execution_context["anomaly_analysis"] = anom_resp
                            output = anom_resp
                        except Exception as e:
                            output = {"error": str(e)}

                elif engine_name == "risk_engine":
                    if entity_id:
                        try:
                            # Use anomaly engine which computes full phase4-v1 risk profile
                            anom_resp = execution_context.get("anomaly_analysis")
                            if not anom_resp:
                                req = AnomalyAnalyzeRequest(entity_id=entity_id, as_of=ref_time)
                                anom_resp = self.anomaly_engine.analyze_entity_anomaly(req)
                                execution_context["anomaly_analysis"] = anom_resp
                            if anom_resp:
                                r_prof = getattr(anom_resp, "risk", getattr(anom_resp, "risk_profile", None))
                                if r_prof:
                                    execution_context["risk_profile"] = r_prof
                                    output = r_prof
                        except Exception as e:
                            output = {"error": str(e)}

                elif engine_name == "fusion_engine":
                    if entity_id:
                        try:
                            req = FusionAnalyzeRequest(entity_id=entity_id, as_of=ref_time)
                            fusion_resp = self.fusion_engine.analyze_fusion(req)
                            execution_context["fusion_analysis"] = fusion_resp
                            output = fusion_resp
                        except Exception as e:
                            output = {"error": str(e)}

                elif engine_name == "prediction_engine":
                    if entity_id:
                        try:
                            req = PredictionAnalyzeRequest(entity_id=entity_id, as_of=ref_time)
                            pred_resp = self.prediction_engine.analyze_prediction(req)
                            execution_context["forecast_response"] = pred_resp
                            output = pred_resp
                        except Exception as e:
                            output = {"error": str(e)}

            except Exception as step_exc:
                output = {"step_error": str(step_exc)}

            execution_context["step_outputs"][step.step_id] = output

        return execution_context
