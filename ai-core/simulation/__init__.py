"""
Synthetic operational simulation data scenarios for NETRA Intelligence Core.
"""

from .synthetic_data import (
    get_synthetic_scenario,
    get_all_synthetic_scenarios,
    get_all_anomaly_scenarios,
    get_anomaly_scenario,
    PHASE4_SCENARIOS_MAP,
    SCENARIO_NORMAL,
    SCENARIO_UNUSUAL,
    SCENARIO_ANOMALOUS,
    SCENARIO_HIGH_RISK_CORRELATED,
    SCENARIO_INSUFFICIENT_HISTORY,
    SCENARIO_CONFLICTING_SIGNALS,
)

__all__ = [
    "get_synthetic_scenario",
    "get_all_synthetic_scenarios",
    "get_all_anomaly_scenarios",
    "get_anomaly_scenario",
    "PHASE4_SCENARIOS_MAP",
    "SCENARIO_NORMAL",
    "SCENARIO_UNUSUAL",
    "SCENARIO_ANOMALOUS",
    "SCENARIO_HIGH_RISK_CORRELATED",
    "SCENARIO_INSUFFICIENT_HISTORY",
    "SCENARIO_CONFLICTING_SIGNALS",
]
