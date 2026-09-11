"""
Unit tests for Ask NETRA intent classification across 16 operational intents.
"""

import pytest
from models.ask_netra import QueryIntent
from query.intent import IntentClassifier


@pytest.fixture
def classifier():
    return IntentClassifier()


@pytest.mark.parametrize(
    "query, expected_intent",
    [
        ("What is the current operational situation?", QueryIntent.STATUS),
        ("Status overview of Sector Alpha", QueryIntent.STATUS),
        ("Who is ENTITY-01?", QueryIntent.ENTITY_PROFILE),
        ("Tell me about ENTITY-02", QueryIntent.ENTITY_PROFILE),
        ("Show timeline for ENTITY-01 in the past 24 hours", QueryIntent.TIMELINE),
        ("What is the event history for ENTITY-03?", QueryIntent.TIMELINE),
        ("What changed with ENTITY-01?", QueryIntent.WHAT_CHANGED),
        ("How has its baseline shifted?", QueryIntent.WHAT_CHANGED),
        ("Is ENTITY-01 anomalous?", QueryIntent.ANOMALY),
        ("Show anomaly breakdown for ENTITY-02", QueryIntent.ANOMALY),
        ("What is the risk level of ENTITY-01?", QueryIntent.RISK),
        ("What is the threat posture of ENTITY-02?", QueryIntent.RISK),
        ("Why is ENTITY-01 high risk?", QueryIntent.WHY),
        ("Explain why its anomaly score increased", QueryIntent.WHY),
        ("What is the activity trend for ENTITY-01?", QueryIntent.TREND),
        ("Is its trajectory increasing or decreasing?", QueryIntent.TREND),
        ("What will ENTITY-01 do next?", QueryIntent.FORECAST),
        ("Predict its future state over the next 6 hours", QueryIntent.FORECAST),
        ("Which sensors support ENTITY-01?", QueryIntent.SOURCE_SUPPORT),
        ("What is the sensor corroboration for ENTITY-02?", QueryIntent.SOURCE_SUPPORT),
        ("Are there conflicting reports for ENTITY-01?", QueryIntent.CONFLICT),
        ("Identify sensor discrepancy for track 01", QueryIntent.CONFLICT),
        ("Show underlying evidence and raw observations", QueryIntent.EVIDENCE),
        ("What evidence supports ENTITY-01?", QueryIntent.EVIDENCE),
        ("Compare ENTITY-01 to ENTITY-02", QueryIntent.COMPARISON),
        ("Difference between ENTITY-01 and ENTITY-03", QueryIntent.COMPARISON),
        ("Who is ENTITY-01 operating with?", QueryIntent.RELATIONSHIP),
        ("Show network links and clusters for ENTITY-01", QueryIntent.RELATIONSHIP),
        ("Run simulation scenario border crossing", QueryIntent.SCENARIO),
        ("What can Ask NETRA do?", QueryIntent.HELP),
        ("help", QueryIntent.HELP),
    ],
)
def test_all_16_intents_recognized(classifier, query, expected_intent):
    intent, score = classifier.classify(query)
    assert intent == expected_intent
    assert score >= 0.60
