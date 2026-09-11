"""
Phase 7 Time Parser for Ask NETRA.
Parses natural language relative durations and explicit timestamps relative to deterministic as_of.
"""

from datetime import datetime, timedelta, timezone
import re
from typing import Optional
from models.ask_netra import TimeRangeFilter


# Patterns for relative durations
DURATION_PATTERNS = [
    (re.compile(r"\b(?:last|past)\s+(\d+)\s*(?:m|min|mins|minutes)\b", re.I), lambda m: float(m.group(1)) * 60.0),
    (re.compile(r"\b(?:last|past)\s+(?:half\s+an\s+hour|30\s*mins?)\b", re.I), lambda m: 1800.0),
    (re.compile(r"\b(?:last|past)\s+(\d+)\s*(?:h|hr|hrs|hours)\b", re.I), lambda m: float(m.group(1)) * 3600.0),
    (re.compile(r"\b(?:last|past)\s+hour\b", re.I), lambda m: 3600.0),
    (re.compile(r"\b(?:last|past)\s+(\d+)\s*(?:d|day|days)\b", re.I), lambda m: float(m.group(1)) * 86400.0),
    (re.compile(r"\b(?:today|last\s+day|past\s+24\s*hours?)\b", re.I), lambda m: 86400.0),
    (re.compile(r"\b(?:last|past)\s+(\d+)\s*(?:w|week|weeks)\b", re.I), lambda m: float(m.group(1)) * 604800.0),
    (re.compile(r"\b(?:last\s+week|past\s+week)\b", re.I), lambda m: 604800.0),
]

ISO_DATE_PATTERN = re.compile(r"\b(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?)\b")


class TimeParser:
    """Parses relative and absolute time bounds deterministically from query strings."""

    def parse(self, text: str, as_of: Optional[datetime] = None) -> Optional[TimeRangeFilter]:
        """
        Parses time expressions from query text.
        Evaluates relative times against as_of (defaulting to fixed epoch if none provided).
        """
        ref_time = as_of or datetime(2026, 9, 12, 12, 0, 0, tzinfo=timezone.utc)
        if ref_time.tzinfo is None:
            ref_time = ref_time.replace(tzinfo=timezone.utc)

        # 1. Check relative duration patterns
        for pattern, duration_calc in DURATION_PATTERNS:
            match = pattern.search(text)
            if match:
                seconds = duration_calc(match)
                start_dt = ref_time - timedelta(seconds=seconds)
                return TimeRangeFilter(
                    start_time=start_dt,
                    end_time=ref_time,
                    relative_duration_seconds=seconds,
                    label=match.group(0),
                )

        # 2. Check explicit ISO timestamp
        iso_match = ISO_DATE_PATTERN.search(text)
        if iso_match:
            try:
                date_str = iso_match.group(1)
                parsed_dt = datetime.fromisoformat(date_str)
                if parsed_dt.tzinfo is None:
                    parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
                return TimeRangeFilter(
                    start_time=parsed_dt - timedelta(hours=1),
                    end_time=parsed_dt + timedelta(hours=1),
                    relative_duration_seconds=7200.0,
                    label=iso_match.group(0),
                )
            except ValueError:
                pass

        return None
