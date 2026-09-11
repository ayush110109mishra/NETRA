"""
Strict 50-run bit-for-bit determinism test for Ask NETRA Phase 7.
"""

from datetime import datetime, timezone
import json
from config import default_config
from entities.repository import EntityRepository
from intelligence.ask_netra import AskNetraEngine
from models.ask_netra import AskNetraRequest
from simulation.synthetic_data import seed_entity_repository


def test_strict_50_run_determinism():
    """
    Executes the exact same query 50 times with fixed as_of and seed.
    Verifies that all 50 serialized JSON outputs match bit-for-bit (excluding execution_time_ms).
    """
    fixed_as_of = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    baseline_payload = None

    for i in range(50):
        # Create fresh engine instance
        repo = EntityRepository(default_config.entity)
        seed_entity_repository(repo)
        engine = AskNetraEngine(config=default_config, repository=repo)

        req = AskNetraRequest(
            query="What is the risk level of ENTITY-01?",
            session_id=f"det_session_{i}",
            as_of=fixed_as_of,
        )
        response = engine.ask(req)

        data = response.model_dump()
        # Pop variable execution duration and session id
        data.pop("execution_time_ms", None)
        data.pop("session_id", None)
        serialized = json.dumps(data, sort_keys=True, default=str)

        if baseline_payload is None:
            baseline_payload = serialized
        else:
            assert (
                serialized == baseline_payload
            ), f"Determinism failure on run {i+1}/50: output differed bit-for-bit."
