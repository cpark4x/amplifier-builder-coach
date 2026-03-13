# Feature 005: Session Event Extractor

## Summary

Extract key metrics from an Amplifier session's `events.jsonl` file. This is
the data extraction layer that sits between session discovery (001) and the
coaching pipeline. It reads the raw event log and produces a structured summary
the coaching agent can evaluate.

## Module

`src/builder_coach/session_extractor.py`

## Interfaces

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class ToolUsage:
    """How often a specific tool was called in a session."""
    tool_name: str
    call_count: int


@dataclass
class SessionSummary:
    """Extracted metrics from a single Amplifier session."""
    session_id: str
    start_time: datetime | None        # first event timestamp
    end_time: datetime | None          # last event timestamp
    duration: timedelta | None         # end - start
    user_message_count: int            # number of user turns (proxy for iteration count)
    assistant_message_count: int       # number of assistant turns
    tool_usage: list[ToolUsage] = field(default_factory=list)
    description: str = ""              # best-effort summary of what was worked on


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


def extract_sessions(session_files: list[Path]) -> list[SessionSummary]:
    """Extract metrics from multiple session files.

    Calls extract_session for each path. Skips files that fail to
    parse (logs a warning, doesn't crash). Returns results sorted
    by start_time, newest first.
    """
```

## Acceptance Criteria

1. Counts user messages as `user_message_count` (proxy for iteration/effort)
2. Counts assistant messages as `assistant_message_count`
3. Extracts tool names and counts from tool_call events
4. Calculates duration from first to last event timestamp
5. `description` is best-effort: first user message content, truncated to 200 chars
6. `extract_sessions` skips unparseable files without crashing
7. Results from `extract_sessions` sorted newest-first by start_time

## Edge Cases

- events.jsonl is empty (0 bytes) → return SessionSummary with all zeros/None
- events.jsonl has malformed JSON lines → skip those lines, extract what you can
- No timestamp fields on events → start_time, end_time, duration all None
- Tool call with no tool name field → skip it
- Single-event session (only one line) → duration is None or zero
- Very large events.jsonl (>100MB) → read line by line, never load whole file into memory

## Test File

`tests/test_session_extractor.py`

## Dependencies

- Standard library only (json, pathlib, datetime, dataclasses, logging)

## Not In Scope

- Interpreting what was built (that's the coaching agent's judgment call)
- Classifying sessions as completed vs. abandoned (coaching agent's job)
- Reading events other than user, assistant, tool_call, session_start
- Any analysis or evaluation — this is pure extraction