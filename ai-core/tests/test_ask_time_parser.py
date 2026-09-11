"""
Unit tests for Ask NETRA time parsing across relative and ISO durations.
"""

from datetime import datetime, timezone
from query.time_parser import TimeParser


def test_relative_hours_parsing():
    parser = TimeParser()
    as_of = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    res = parser.parse("Show events in the past 6 hours", as_of=as_of)
    assert res is not None
    assert res.relative_duration_seconds == 21600.0
    assert res.end_time == as_of
    assert (as_of - res.start_time).total_seconds() == 21600.0


def test_relative_minutes_parsing():
    parser = TimeParser()
    as_of = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    res = parser.parse("What happened in the last 30 minutes?", as_of=as_of)
    assert res is not None
    assert res.relative_duration_seconds == 1800.0


def test_day_parsing():
    parser = TimeParser()
    as_of = datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
    res = parser.parse("Activity over the past 24 hours", as_of=as_of)
    assert res is not None
    assert res.relative_duration_seconds == 86400.0


def test_no_time_returns_none():
    parser = TimeParser()
    res = parser.parse("Is ENTITY-01 high risk?")
    assert res is None
