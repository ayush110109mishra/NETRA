"""
Test suite for NETRA Phase 5 Source Registry and Health Assessment.
"""

from datetime import datetime, timezone
import pytest

from fusion.source_registry import SourceRegistry
from models.fusion_intelligence import SourceMetadata, SourceStatus, SourceType


def test_default_sources_registered():
    registry = SourceRegistry()
    sources = registry.list_sources()
    assert len(sources) >= 8

    # Verify standard sources exist
    radar = registry.get_source("RADAR_01")
    assert radar.source_id == "RADAR_01"
    assert radar.reliability == 0.90
    assert radar.independence_group == "RADAR_ALPHA"

    radar_dup = registry.get_source("RADAR_01_DUP")
    assert radar_dup.independence_group == "RADAR_ALPHA"  # Shared independence group

    optical = registry.get_source("OPTICAL_01")
    assert optical.source_type == SourceType.OPTICAL
    assert optical.reliability == 0.85


def test_cold_start_source_registration():
    registry = SourceRegistry()
    unknown = registry.get_source("UNSEEN_SENSOR_XYZ")
    assert unknown.source_id == "UNSEEN_SENSOR_XYZ"
    assert unknown.status == SourceStatus.UNKNOWN
    assert unknown.reliability <= 0.40
    assert unknown.metadata.get("cold_start") is True


def test_calculate_source_reliability_bounds():
    registry = SourceRegistry()
    score, factors, explanation = registry.calculate_source_reliability("RADAR_01")
    assert 0.0 <= score <= 1.0
    assert "declared_reliability" in factors
    assert "historical_consistency" in factors
    assert len(explanation) > 10


def test_source_health_and_dropout():
    registry = SourceRegistry()
    # Normal active health
    health_active = registry.get_source_health("RADAR_01", observation_count=10, contradiction_count=0)
    assert health_active.status == SourceStatus.ACTIVE
    assert health_active.reliability_score >= 0.80
    assert health_active.is_dropout is False

    # Dropout state
    health_dropout = registry.get_source_health("RADAR_01", observation_count=10, is_dropout=True)
    assert health_dropout.status == SourceStatus.DROPOUT
    assert health_dropout.is_dropout is True
    assert health_dropout.reliability_trend == "DEGRADING"

    # Stale state
    health_stale = registry.get_source_health("RADAR_01", observation_count=10, is_stale=True)
    assert health_stale.status == SourceStatus.DEGRADED
    assert health_stale.is_stale is True
