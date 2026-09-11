"""
Phase 7 Query Intent Classifier for Ask NETRA.
Deterministic keyword and regex-based intent classification for operational questions.
"""

import re
from typing import List, Tuple
from models.ask_netra import QueryIntent


INTENT_PATTERNS: List[Tuple[QueryIntent, List[re.Pattern], float]] = [
    # Help / Capabilities
    (
        QueryIntent.HELP,
        [
            re.compile(r"\b(help|capabilities|supported (queries|commands)|how to use)\b", re.I),
            re.compile(r"\bwhat can (you|ask netra|netra) do\b", re.I),
            re.compile(r"^(commands|options|\?)$", re.I),
        ],
        0.98,
    ),
    # Comparison
    (
        QueryIntent.COMPARISON,
        [
            re.compile(r"\b(compare|contrast|versus|\bvs\b|difference between)\b", re.I),
            re.compile(r"\bhow does \S+ compare to \S+\b", re.I),
        ],
        0.95,
    ),
    # Conflict
    (
        QueryIntent.CONFLICT,
        [
            re.compile(r"\b(conflict\w*|contradict\w*|discrepan\w*|mismatch\w*|disagree\w*)\b", re.I),
            re.compile(r"\bcontradictory (reports|telemetry|sensors)\b", re.I),
        ],
        0.95,
    ),
    # Source Support / Corroboration
    (
        QueryIntent.SOURCE_SUPPORT,
        [
            re.compile(r"\b(source[s]? support|sensor[s]? support|who reported|corroborat\w*|sensor[s]? reliability|which source[s]?|which sensor[s]?)\b", re.I),
            re.compile(r"\b(reporting sources|source consensus)\b", re.I),
        ],
        0.92,
    ),
    # Evidence / Telemetry lineage
    (
        QueryIntent.EVIDENCE,
        [
            re.compile(r"\b(evidence|audit trail|lineage|raw observations|raw telemetry|underlying evidence|cite evidence)\b", re.I),
            re.compile(r"\bwhat evidence supports\b", re.I),
        ],
        0.92,
    ),
    # Why / Attribution
    (
        QueryIntent.WHY,
        [
            re.compile(r"\b(why did|why is|what caused|attribution|explain why|root cause|reason for)\b", re.I),
            re.compile(r"\bwhy\b", re.I),
        ],
        0.94,
    ),
    # What Changed / Drift
    (
        QueryIntent.WHAT_CHANGED,
        [
            re.compile(r"\b(what changed|what has changed|changes in|how has .* (changed|shifted)|recent changes|operational delta)\b", re.I),
            re.compile(r"\b(baseline.*shift|state shift|baseline drift|baseline shift)\b", re.I),
        ],
        0.92,
    ),
    # Forecast / Prediction
    (
        QueryIntent.FORECAST,
        [
            re.compile(r"\b(forecast\w*|predict\w*|projected|future state|what will happen|expected behavior|next state)\b", re.I),
            re.compile(r"\bwhat will .* (do next|happen)\b", re.I),
            re.compile(r"\bwill \S+ (escalate|recur|move|attack|deviate|do next)\b", re.I),
        ],
        0.93,
    ),
    # Trend
    (
        QueryIntent.TREND,
        [
            re.compile(r"\b(trend\w*|trajectory|momentum|increasing or decreasing|rate of change|accelerat\w*)\b", re.I),
            re.compile(r"\b(risk trend|activity trend|trend direction)\b", re.I),
        ],
        0.90,
    ),
    # Anomaly
    (
        QueryIntent.ANOMALY,
        [
            re.compile(r"\b(anomal\w*|unusual|abnormal|deviat\w*|outlier\w*|irregular\w*)\b", re.I),
            re.compile(r"\bis \S+ anomalous\b", re.I),
        ],
        0.92,
    ),
    # Risk
    (
        QueryIntent.RISK,
        [
            re.compile(r"\b(risk|threat\w*|danger\w*|threat level|risk score|composite risk|risk posture)\b", re.I),
            re.compile(r"\bhow dangerous is\b", re.I),
        ],
        0.91,
    ),
    # Relationship / Network
    (
        QueryIntent.RELATIONSHIP,
        [
            re.compile(r"\b(relationship\w*|connect\w*|network\w*|associated with|linked to|co-located|allies|cluster\w*)\b", re.I),
            re.compile(r"\bwho is \S+ operating with\b", re.I),
        ],
        0.90,
    ),
    # Timeline / History
    (
        QueryIntent.TIMELINE,
        [
            re.compile(r"\b(timeline|history|chronolog\w*|sequence of events|event log|activity history)\b", re.I),
            re.compile(r"\bwhat happened with\b", re.I),
        ],
        0.88,
    ),
    # Scenario
    (
        QueryIntent.SCENARIO,
        [
            re.compile(r"\b(scenario|simulation|exercise|drill|test case|synthetic run)\b", re.I),
            re.compile(r"\brun scenario\b", re.I),
        ],
        0.90,
    ),
    # Entity Profile
    (
        QueryIntent.ENTITY_PROFILE,
        [
            re.compile(r"\b(who is|tell me about|profile of|entity profile|describe entity|details of|dossier on)\b", re.I),
            re.compile(r"\bwhat is (entity|track|target)\b", re.I),
        ],
        0.87,
    ),
    # Status (Default Operational Posture)
    (
        QueryIntent.STATUS,
        [
            re.compile(r"\b(status|situation|overview|readiness|posture|what is happening|current state)\b", re.I),
            re.compile(r"\bsummarize current\b", re.I),
        ],
        0.82,
    ),
]


class IntentClassifier:
    """Deterministic intent classifier utilizing operational regex patterns and keyword heuristics."""

    def classify(self, text: str) -> Tuple[QueryIntent, float]:
        """
        Classifies the operator's query text into a primary QueryIntent with associated confidence.
        """
        query_clean = text.strip()
        if not query_clean:
            return QueryIntent.HELP, 0.70

        best_intent = QueryIntent.STATUS
        best_score = 0.50

        for intent, patterns, base_confidence in INTENT_PATTERNS:
            for pattern in patterns:
                match = pattern.search(query_clean)
                if match:
                    score = base_confidence
                    # Boost if match is near the beginning
                    if match.start() < 10:
                        score = min(0.99, score + 0.04)
                    if score > best_score:
                        best_score = score
                        best_intent = intent
                        break  # Found best match for this intent

        return best_intent, round(best_score, 3)
