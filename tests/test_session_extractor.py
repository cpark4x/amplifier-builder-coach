"""Tests for session_extractor module — F-005.

Tests written test-first: all tests exist before any implementation.
Each test maps to a specific acceptance criterion or edge case from the spec.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from builder_coach.session_extractor import (
    SessionSummary,
    ToolUsage,
    extract_session,
    extract_sessions,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def write_events(path: Path, events: list[dict]) -> Path:
    """Write a list of event dicts to a JSONL file and return the path."""
    path.write_text("\n".join(json.dumps(e) for e in events) + "\n")
    return path


def make_ts(offset_seconds: int = 0) -> str:
    """Return an ISO 8601 timestamp offset from a fixed base time."""
    base = datetime(2026, 3, 10, 9, 0, 0)
    return (base + timedelta(seconds=offset_seconds)).isoformat()


# ---------------------------------------------------------------------------
# AC1 — Counts user messages as user_message_count
# ---------------------------------------------------------------------------


def test_counts_user_messages(tmp_path):
    events_file = tmp_path / "events.jsonl"
    write_events(
        events_file,
        [
            {"type": "user", "timestamp": make_ts(0), "content": "Hello"},
            {"type": "assistant", "timestamp": make_ts(10), "content": "Hi"},
            {"type": "user", "timestamp": make_ts(20), "content": "What is TDD?"},
            {"type": "assistant", "timestamp": make_ts(30), "content": "It means..."},
            {"type": "user", "timestamp": make_ts(40), "content": "Thanks"},
        ],
    )

    summary = extract_session(events_file)

    assert summary.user_message_count == 3


# ---------------------------------------------------------------------------
# AC2 — Counts assistant messages as assistant_message_count
# ---------------------------------------------------------------------------


def test_counts_assistant_messages(tmp_path):
    events_file = tmp_path / "events.jsonl"
    write_events(
        events_file,
        [
            {"type": "user", "timestamp": make_ts(0), "content": "Go"},
            {"type": "assistant", "timestamp": make_ts(5), "content": "Done"},
            {"type": "assistant", "timestamp": make_ts(10), "content": "More"},
        ],
    )

    summary = extract_session(events_file)

    assert summary.assistant_message_count == 2


# ---------------------------------------------------------------------------
# AC3 — Extracts tool names and counts from tool_call events
# ---------------------------------------------------------------------------


def test_extracts_tool_usage(tmp_path):
    events_file = tmp_path / "events.jsonl"
    write_events(
        events_file,
        [
            {"type": "user", "timestamp": make_ts(0), "content": "Build it"},
            {"type": "tool_call", "timestamp": make_ts(5), "tool_name": "bash"},
            {"type": "tool_call", "timestamp": make_ts(10), "tool_name": "read_file"},
            {"type": "tool_call", "timestamp": make_ts(15), "tool_name": "bash"},
            {"type": "tool_call", "timestamp": make_ts(20), "tool_name": "bash"},
        ],
    )

    summary = extract_session(events_file)

    tool_map = {t.tool_name: t.call_count for t in summary.tool_usage}
    assert tool_map["bash"] == 3
    assert tool_map["read_file"] == 1


def test_tool_usage_is_sorted_by_call_count_descending(tmp_path):
    """Most-used tools should appear first for readability."""
    events_file = tmp_path / "events.jsonl"
    write_events(
        events_file,
        [
            {"type": "tool_call", "timestamp": make_ts(0), "tool_name": "read_file"},
            {"type": "tool_call", "timestamp": make_ts(5), "tool_name": "bash"},
            {"type": "tool_call", "timestamp": make_ts(10), "tool_name": "bash"},
            {"type": "tool_call", "timestamp": make_ts(15), "tool_name": "write_file"},
            {"type": "tool_call", "timestamp": make_ts(20), "tool_name": "bash"},
        ],
    )

    summary = extract_session(events_file)

    assert summary.tool_usage[0].tool_name == "bash"
    assert summary.tool_usage[0].call_count == 3


# ---------------------------------------------------------------------------
# AC4 — Calculates duration from first to last event timestamp
# ---------------------------------------------------------------------------


def test_calculates_duration(tmp_path):
    events_file = tmp_path / "events.jsonl"
    write_events(
        events_file,
        [
            {"type": "user", "timestamp": make_ts(0), "content": "Start"},
            {"type": "assistant", "timestamp": make_ts(30), "content": "Middle"},
            {"type": "user", "timestamp": make_ts(120), "content": "End"},
        ],
    )

    summary = extract_session(events_file)

    assert summary.start_time == datetime(2026, 3, 10, 9, 0, 0)
    assert summary.end_time == datetime(2026, 3, 10, 9, 2, 0)
    assert summary.duration == timedelta(seconds=120)


def test_start_time_is_first_event_timestamp(tmp_path):
    events_file = tmp_path / "events.jsonl"
    write_events(
        events_file,
        [
            {"type": "assistant", "timestamp": make_ts(0), "content": "First"},
            {"type": "user", "timestamp": make_ts(60), "content": "Second"},
        ],
    )

    summary = extract_session(events_file)

    assert summary.start_time == datetime(2026, 3, 10, 9, 0, 0)


# ---------------------------------------------------------------------------
# AC5 — description is first user message content, truncated to 200 chars
# ---------------------------------------------------------------------------


def test_description_is_first_user_message(tmp_path):
    events_file = tmp_path / "events.jsonl"
    write_events(
        events_file,
        [
            {"type": "assistant", "timestamp": make_ts(0), "content": "Ignored"},
            {"type": "user", "timestamp": make_ts(5), "content": "Build the extractor"},
            {"type": "user", "timestamp": make_ts(10), "content": "Also do tests"},
        ],
    )

    summary = extract_session(events_file)

    assert summary.description == "Build the extractor"


def test_description_truncated_to_200_chars(tmp_path):
    events_file = tmp_path / "events.jsonl"
    long_content = "A" * 300
    write_events(
        events_file,
        [
            {"type": "user", "timestamp": make_ts(0), "content": long_content},
        ],
    )

    summary = extract_session(events_file)

    assert len(summary.description) == 200
    assert summary.description == "A" * 200


def test_description_empty_when_no_user_messages(tmp_path):
    events_file = tmp_path / "events.jsonl"
    write_events(
        events_file,
        [
            {"type": "assistant", "timestamp": make_ts(0), "content": "Hello"},
        ],
    )

    summary = extract_session(events_file)

    assert summary.description == ""


# ---------------------------------------------------------------------------
# AC6 — extract_sessions skips unparseable files without crashing
# ---------------------------------------------------------------------------


def test_extract_sessions_skips_missing_file(tmp_path):
    missing = tmp_path / "ghost" / "events.jsonl"
    good_file = tmp_path / "events.jsonl"
    write_events(
        good_file,
        [{"type": "user", "timestamp": make_ts(0), "content": "Hi"}],
    )

    results = extract_sessions([missing, good_file])

    # Only the good file should produce a result
    assert len(results) == 1


def test_extract_sessions_skips_completely_unparseable_file(tmp_path):
    """A file that raises an unexpected error should be skipped."""
    bad_file = tmp_path / "bad" / "events.jsonl"
    bad_file.parent.mkdir()
    bad_file.write_text("NOT JSON AT ALL\n{broken\n")

    good_file = tmp_path / "good" / "events.jsonl"
    good_file.parent.mkdir()
    write_events(
        good_file,
        [{"type": "user", "timestamp": make_ts(0), "content": "Hi"}],
    )

    results = extract_sessions([bad_file, good_file])

    # bad_file has malformed JSON — extract_session still returns a SessionSummary
    # (skips bad lines); extract_sessions never crashes regardless
    assert len(results) >= 1


def test_extract_sessions_returns_empty_list_for_all_bad_files(tmp_path):
    missing1 = tmp_path / "a" / "events.jsonl"
    missing2 = tmp_path / "b" / "events.jsonl"

    results = extract_sessions([missing1, missing2])

    assert results == []


# ---------------------------------------------------------------------------
# AC7 — Results sorted newest-first by start_time
# ---------------------------------------------------------------------------


def test_extract_sessions_sorted_newest_first(tmp_path):
    old_file = tmp_path / "old" / "events.jsonl"
    old_file.parent.mkdir()
    write_events(old_file, [{"type": "user", "timestamp": make_ts(0), "content": "Old"}])

    new_file = tmp_path / "new" / "events.jsonl"
    new_file.parent.mkdir()
    # 1 hour later
    write_events(
        new_file,
        [{"type": "user", "timestamp": make_ts(3600), "content": "New"}],
    )

    results = extract_sessions([old_file, new_file])

    assert results[0].start_time > results[1].start_time


def test_extract_sessions_sessions_with_none_start_time_sorted_last(tmp_path):
    """Sessions with no timestamps should sort after sessions with timestamps."""
    timed_file = tmp_path / "timed" / "events.jsonl"
    timed_file.parent.mkdir()
    write_events(timed_file, [{"type": "user", "timestamp": make_ts(0), "content": "Hi"}])

    no_ts_file = tmp_path / "nots" / "events.jsonl"
    no_ts_file.parent.mkdir()
    write_events(no_ts_file, [{"type": "user", "content": "No timestamp"}])

    results = extract_sessions([no_ts_file, timed_file])

    assert results[0].start_time is not None
    assert results[-1].start_time is None


# ---------------------------------------------------------------------------
# Edge: empty file → all zeros/None
# ---------------------------------------------------------------------------


def test_empty_file_returns_summary_with_zeros(tmp_path):
    events_file = tmp_path / "events.jsonl"
    events_file.write_bytes(b"")

    summary = extract_session(events_file)

    assert summary.user_message_count == 0
    assert summary.assistant_message_count == 0
    assert summary.tool_usage == []
    assert summary.start_time is None
    assert summary.end_time is None
    assert summary.duration is None
    assert summary.description == ""


# ---------------------------------------------------------------------------
# Edge: malformed JSON lines → skip those lines, extract what you can
# ---------------------------------------------------------------------------


def test_malformed_json_lines_are_skipped(tmp_path):
    events_file = tmp_path / "events.jsonl"
    events_file.write_text(
        '{"type": "user", "timestamp": "2026-03-10T09:00:00", "content": "Good line"}\n'
        "NOT VALID JSON\n"
        '{"type": "assistant", "timestamp": "2026-03-10T09:01:00", "content": "Also good"}\n'
        "{broken json}\n"
        '{"type": "user", "timestamp": "2026-03-10T09:02:00", "content": "Third user"}\n'
    )

    summary = extract_session(events_file)

    assert summary.user_message_count == 2
    assert summary.assistant_message_count == 1
    assert summary.start_time == datetime(2026, 3, 10, 9, 0, 0)
    assert summary.end_time == datetime(2026, 3, 10, 9, 2, 0)


# ---------------------------------------------------------------------------
# Edge: no timestamp fields → start_time, end_time, duration all None
# ---------------------------------------------------------------------------


def test_no_timestamps_gives_none_times(tmp_path):
    events_file = tmp_path / "events.jsonl"
    write_events(
        events_file,
        [
            {"type": "user", "content": "No time here"},
            {"type": "assistant", "content": "Me neither"},
        ],
    )

    summary = extract_session(events_file)

    assert summary.start_time is None
    assert summary.end_time is None
    assert summary.duration is None


# ---------------------------------------------------------------------------
# Edge: tool call with no tool_name field → skip it
# ---------------------------------------------------------------------------


def test_tool_call_without_name_is_skipped(tmp_path):
    events_file = tmp_path / "events.jsonl"
    write_events(
        events_file,
        [
            {"type": "tool_call", "timestamp": make_ts(0), "tool_name": "bash"},
            {"type": "tool_call", "timestamp": make_ts(5)},  # no tool_name
            {"type": "tool_call", "timestamp": make_ts(10), "tool_name": "bash"},
        ],
    )

    summary = extract_session(events_file)

    assert len(summary.tool_usage) == 1
    assert summary.tool_usage[0].tool_name == "bash"
    assert summary.tool_usage[0].call_count == 2


# ---------------------------------------------------------------------------
# Edge: single-event session → duration is None or zero
# ---------------------------------------------------------------------------


def test_single_event_duration_is_none_or_zero(tmp_path):
    events_file = tmp_path / "events.jsonl"
    write_events(
        events_file,
        [{"type": "user", "timestamp": make_ts(0), "content": "Alone"}],
    )

    summary = extract_session(events_file)

    # duration should be None or timedelta(0) — both are acceptable
    assert summary.duration is None or summary.duration == timedelta(0)


# ---------------------------------------------------------------------------
# Edge: FileNotFoundError raised when path doesn't exist
# ---------------------------------------------------------------------------


def test_extract_session_raises_for_missing_file(tmp_path):
    missing = tmp_path / "ghost" / "events.jsonl"

    with pytest.raises(FileNotFoundError):
        extract_session(missing)


# ---------------------------------------------------------------------------
# Contract: session_id is derived from the parent directory name
# ---------------------------------------------------------------------------


def test_session_id_is_parent_directory_name(tmp_path):
    session_dir = tmp_path / "session_abc123"
    session_dir.mkdir()
    events_file = session_dir / "events.jsonl"
    write_events(events_file, [{"type": "user", "timestamp": make_ts(0), "content": "Hi"}])

    summary = extract_session(events_file)

    assert summary.session_id == "session_abc123"


# ---------------------------------------------------------------------------
# Contract: ToolUsage and SessionSummary are dataclasses (not dicts)
# ---------------------------------------------------------------------------


def test_summary_is_dataclass_instance(tmp_path):
    events_file = tmp_path / "events.jsonl"
    write_events(events_file, [{"type": "user", "timestamp": make_ts(0), "content": "Hi"}])

    summary = extract_session(events_file)

    assert isinstance(summary, SessionSummary)


def test_tool_usage_is_dataclass_instance(tmp_path):
    events_file = tmp_path / "events.jsonl"
    write_events(
        events_file,
        [{"type": "tool_call", "timestamp": make_ts(0), "tool_name": "bash"}],
    )

    summary = extract_session(events_file)

    assert len(summary.tool_usage) == 1
    assert isinstance(summary.tool_usage[0], ToolUsage)


# ---------------------------------------------------------------------------
# Contract: extract_sessions returns a list
# ---------------------------------------------------------------------------


def test_extract_sessions_returns_list(tmp_path):
    events_file = tmp_path / "events.jsonl"
    write_events(events_file, [{"type": "user", "timestamp": make_ts(0), "content": "Hi"}])

    results = extract_sessions([events_file])

    assert isinstance(results, list)
    assert len(results) == 1
    assert isinstance(results[0], SessionSummary)
