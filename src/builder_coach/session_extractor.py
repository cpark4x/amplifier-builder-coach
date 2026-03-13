"""Session Event Extractor — F-005.

Extract key metrics from an Amplifier session's events.jsonl file.
This is the data extraction layer that sits between session discovery (F-001)
and the coaching pipeline. Reads raw event logs, produces structured summaries.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

log = logging.getLogger(__name__)

_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
_DESCRIPTION_MAX_LEN = 200


@dataclass
class ToolUsage:
    """How often a specific tool was called in a session."""

    tool_name: str
    call_count: int


@dataclass
class SessionSummary:
    """Extracted metrics from a single Amplifier session."""

    session_id: str
    start_time: datetime | None  # first event timestamp
    end_time: datetime | None  # last event timestamp
    duration: timedelta | None  # end - start
    user_message_count: int  # number of user turns (proxy for iteration count)
    assistant_message_count: int  # number of assistant turns
    tool_usage: list[ToolUsage] = field(default_factory=list)
    description: str = ""  # best-effort summary of what was worked on


def _parse_timestamp(ts_str: str) -> datetime | None:
    """Parse an ISO 8601 timestamp string, returning None on failure."""
    if not ts_str:
        return None
    # Handle both 'YYYY-MM-DDTHH:MM:SS' and 'YYYY-MM-DDTHH:MM:SS.ffffff' forms
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            continue
    return None


def extract_session(events_path: Path) -> SessionSummary:
    """Extract metrics from a session's events.jsonl file.

    Reads the JSONL file line by line. Each line is a JSON object with
    at minimum a "type" field. Relevant event types:

    - type="user": a user message (count for iteration tracking)
    - type="assistant": an assistant response
    - type="tool_call": a tool invocation (extract tool name)
    - type="session_start": session metadata

    All events may have a "timestamp" field (ISO 8601).

    Args:
        events_path: Path to the events.jsonl file.

    Returns:
        SessionSummary with extracted metrics.

    Raises:
        FileNotFoundError: If events_path doesn't exist.
    """
    if not events_path.exists():
        raise FileNotFoundError(f"events.jsonl not found: {events_path}")

    session_id = events_path.parent.name

    user_message_count = 0
    assistant_message_count = 0
    tool_counts: dict[str, int] = {}
    first_ts: datetime | None = None
    last_ts: datetime | None = None
    description = ""

    with events_path.open("r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                log.debug("Skipping malformed JSON line in %s", events_path)
                continue

            if not isinstance(event, dict):
                continue

            # Track timestamps
            ts_str = event.get("timestamp", "")
            if ts_str:
                ts = _parse_timestamp(ts_str)
                if ts is not None:
                    if first_ts is None or ts < first_ts:
                        first_ts = ts
                    if last_ts is None or ts > last_ts:
                        last_ts = ts

            event_type = event.get("type", "")

            if event_type == "user":
                user_message_count += 1
                # description: first user message content, truncated to 200 chars
                if not description:
                    content = event.get("content", "")
                    if content:
                        description = str(content)[:_DESCRIPTION_MAX_LEN]

            elif event_type == "assistant":
                assistant_message_count += 1

            elif event_type == "tool_call":
                tool_name = event.get("tool_name")
                if tool_name:
                    tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

    # Build tool_usage list sorted by call_count descending
    tool_usage = sorted(
        [ToolUsage(tool_name=name, call_count=count) for name, count in tool_counts.items()],
        key=lambda t: t.call_count,
        reverse=True,
    )

    # Calculate duration
    if first_ts is not None and last_ts is not None and last_ts != first_ts:
        duration: timedelta | None = last_ts - first_ts
    else:
        duration = None

    return SessionSummary(
        session_id=session_id,
        start_time=first_ts,
        end_time=last_ts,
        duration=duration,
        user_message_count=user_message_count,
        assistant_message_count=assistant_message_count,
        tool_usage=tool_usage,
        description=description,
    )


def extract_sessions(session_files: list[Path]) -> list[SessionSummary]:
    """Extract metrics from multiple session files.

    Calls extract_session for each path. Skips files that fail to
    parse (logs a warning, doesn't crash). Returns results sorted
    by start_time, newest first.

    Sessions with no start_time sort after all timed sessions.
    """
    summaries: list[SessionSummary] = []

    for path in session_files:
        try:
            summary = extract_session(path)
            summaries.append(summary)
        except FileNotFoundError:
            log.warning("Session file not found, skipping: %s", path)
        except Exception:  # noqa: BLE001
            log.warning("Failed to parse session file, skipping: %s", path, exc_info=True)

    # Sort newest-first; None start_time sinks to the end
    summaries.sort(
        key=lambda s: s.start_time if s.start_time is not None else datetime.min,
        reverse=True,
    )

    return summaries
