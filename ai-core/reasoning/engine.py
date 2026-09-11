"""
Phase 7 Master Reasoning Coordinator for Ask NETRA.
Coordinates evidence extraction, ledger indexing, attribution, and structured answer synthesis.
"""

from typing import Any, Dict, Tuple
from models.ask_netra import AskAnswer, EpistemicLedger, ParsedQuery
from reasoning.evidence import EvidenceLedgerBuilder
from reasoning.synthesis import AnswerSynthesizer


class ReasoningEngine:
    """Coordinates evidence ledgering, causal reasoning, and structured answer synthesis."""

    def __init__(self):
        self.ledger_builder = EvidenceLedgerBuilder()
        self.synthesizer = AnswerSynthesizer()

    def reason_and_synthesize(
        self,
        parsed: ParsedQuery,
        execution_context: Dict[str, Any],
    ) -> Tuple[AskAnswer, EpistemicLedger]:
        """
        Extracts evidence into the 5-tier ledger and generates a grounded AskAnswer.
        """
        ledger = self.ledger_builder.build_ledger(execution_context)
        answer = self.synthesizer.synthesize(parsed, execution_context, ledger)
        return answer, ledger
