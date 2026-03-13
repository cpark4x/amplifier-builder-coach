"""Tests for evidence module — F-006.

Tests written test-first: all tests exist before any implementation.
Each test maps to a specific acceptance criterion or edge case from the spec.
"""

from datetime import date, datetime, timedelta

import pytest

from builder_coach.evidence import WeeklyEvidence, combine_evidence, format_evidence_markdown
from builder_coach.journal_parser import JournalEntry
from builder_coach.session_extractor import SessionSummary, ToolUsage


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def make_session(
    session_id: str = "sess_001",
    duration_minutes: float | None = 30.0,
    user_message_count: int = 5,
    tool_usage: list[ToolUsage] | None = None,
    description: str = "",
) -> SessionSummary:
    """Build a minimal SessionSummary for testing."""
    if tool_usage is None:
        tool_usage = []
    duration = timedelta(minutes=duration_minutes) if duration_minutes is not None else None
    base = datetime(2026, 3, 10, 9, 0, 0)
    end = base + duration if duration is not None else base
    return SessionSummary(
        session_id=session_id,
        start_time=base,
        end_time=end,
        duration=duration,
        user_message_count=user_message_count,
        assistant_message_count=3,
        tool_usage=tool_usage,
        description=description,
    )


def make_journal_entry(
    entry_date: date,
    raw_text: str = "Worked on something.",
    tags: list[str] | None = None,
) -> JournalEntry:
    """Build a minimal JournalEntry for testing."""
    return JournalEntry(date=entry_date, raw_text=raw_text, tags=tags or [])


# ---------------------------------------------------------------------------
# AC1 — total_session_time_minutes sums duration across all sessions
# ---------------------------------------------------------------------------


def test_total_session_time_sums_durations():
    sessions = [
        make_session(session_id="s1", duration_minutes=30.0),
        make_session(session_id="s2", duration_minutes=45.0),
    ]
    evidence = combine_evidence(sessions=sessions, journal_entries=[])

    assert evidence.total_session_time_minutes == pytest.approx(75.0)


def test_total_session_time_skips_none_durations():
    sessions = [
        make_session(session_id="s1", duration_minutes=60.0),
        make_session(session_id="s2", duration_minutes=None),
        make_session(session_id="s3", duration_minutes=30.0),
    ]
    evidence = combine_evidence(sessions=sessions, journal_entries=[])

    assert evidence.total_session_time_minutes == pytest.approx(90.0)


def test_total_session_time_zero_when_all_durations_none():
    sessions = [
        make_session(session_id="s1", duration_minutes=None),
        make_session(session_id="s2", duration_minutes=None),
    ]
    evidence = combine_evidence(sessions=sessions, journal_entries=[])

    assert evidence.total_session_time_minutes == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# AC2 — total_user_messages sums user_message_count across all sessions
# ---------------------------------------------------------------------------


def test_total_user_messages_sums_across_sessions():
    sessions = [
        make_session(session_id="s1", user_message_count=5),
        make_session(session_id="s2", user_message_count=8),
        make_session(session_id="s3", user_message_count=3),
    ]
    evidence = combine_evidence(sessions=sessions, journal_entries=[])

    assert evidence.total_user_messages == 16


def test_total_user_messages_zero_when_no_sessions():
    evidence = combine_evidence(sessions=[], journal_entries=[])

    assert evidence.total_user_messages == 0


# ---------------------------------------------------------------------------
# AC3 — has_session_data is True when sessions list is non-empty
# ---------------------------------------------------------------------------


def test_has_session_data_true_when_sessions_present():
    sessions = [make_session()]
    evidence = combine_evidence(sessions=sessions, journal_entries=[])

    assert evidence.has_session_data is True


def test_has_session_data_false_when_sessions_empty():
    evidence = combine_evidence(sessions=[], journal_entries=[])

    assert evidence.has_session_data is False


# ---------------------------------------------------------------------------
# AC4 — has_journal_data is True when journal_entries list is non-empty
# ---------------------------------------------------------------------------


def test_has_journal_data_true_when_entries_present():
    entries = [make_journal_entry(date(2026, 3, 10))]
    evidence = combine_evidence(sessions=[], journal_entries=entries)

    assert evidence.has_journal_data is True


def test_has_journal_data_false_when_entries_empty():
    evidence = combine_evidence(sessions=[], journal_entries=[])

    assert evidence.has_journal_data is False


# ---------------------------------------------------------------------------
# AC5 — format_evidence_markdown includes an "Evidence Gaps" section
# ---------------------------------------------------------------------------


def test_format_includes_evidence_gaps_section():
    evidence = combine_evidence(sessions=[], journal_entries=[])
    md = format_evidence_markdown(evidence)

    assert "Evidence Gaps" in md


def test_format_gaps_section_lists_missing_sessions():
    evidence = combine_evidence(sessions=[], journal_entries=[])
    md = format_evidence_markdown(evidence)

    # Should mention that session data is missing
    assert "session" in md.lower()


def test_format_gaps_section_lists_missing_journal():
    sessions = [make_session()]
    evidence = combine_evidence(sessions=sessions, journal_entries=[])
    md = format_evidence_markdown(evidence)

    # Should mention that journal data is missing
    assert "journal" in md.lower()


def test_format_gaps_section_lists_both_when_both_empty():
    evidence = combine_evidence(sessions=[], journal_entries=[])
    md = format_evidence_markdown(evidence)

    # Both sources missing — both should appear in gaps
    lower = md.lower()
    assert "session" in lower
    assert "journal" in lower


def test_format_no_gaps_when_both_sources_present():
    sessions = [make_session()]
    entries = [make_journal_entry(date(2026, 3, 10))]
    evidence = combine_evidence(sessions=sessions, journal_entries=entries)
    md = format_evidence_markdown(evidence)

    # Evidence Gaps section should still exist but indicate nothing is missing
    assert "Evidence Gaps" in md
    # The gaps section should not list any missing sources
    lines = md.split("\n")
    gaps_idx = next(i for i, line in enumerate(lines) if "Evidence Gaps" in line)
    # Find the content right after the gaps header
    gaps_content = "\n".join(lines[gaps_idx : gaps_idx + 5]).lower()
    assert "none" in gaps_content or "complete" in gaps_content or "✓" in gaps_content


# ---------------------------------------------------------------------------
# AC6 — format_evidence_markdown includes top 5 tools by call count
# ---------------------------------------------------------------------------


def test_format_includes_top_tools():
    sessions = [
        make_session(
            session_id="s1",
            tool_usage=[
                ToolUsage(tool_name="bash", call_count=10),
                ToolUsage(tool_name="read_file", call_count=8),
                ToolUsage(tool_name="write_file", call_count=5),
            ],
        )
    ]
    evidence = combine_evidence(sessions=sessions, journal_entries=[])
    md = format_evidence_markdown(evidence)

    assert "bash" in md
    assert "read_file" in md


def test_format_top_tools_aggregated_across_sessions():
    """Tool counts aggregate across multiple sessions."""
    sessions = [
        make_session(
            session_id="s1",
            tool_usage=[ToolUsage(tool_name="bash", call_count=5)],
        ),
        make_session(
            session_id="s2",
            tool_usage=[ToolUsage(tool_name="bash", call_count=7)],
        ),
    ]
    evidence = combine_evidence(sessions=sessions, journal_entries=[])
    md = format_evidence_markdown(evidence)

    # bash total = 12, should appear once in the tools section
    assert "bash" in md
    assert "12" in md


def test_format_top_tools_limited_to_five():
    """Only the top 5 tools appear in the tools section."""
    sessions = [
        make_session(
            session_id="s1",
            tool_usage=[
                ToolUsage(tool_name="bash", call_count=10),
                ToolUsage(tool_name="read_file", call_count=9),
                ToolUsage(tool_name="write_file", call_count=8),
                ToolUsage(tool_name="grep", call_count=7),
                ToolUsage(tool_name="glob", call_count=6),
                ToolUsage(tool_name="LSP", call_count=1),  # 6th — should be excluded
            ],
        )
    ]
    evidence = combine_evidence(sessions=sessions, journal_entries=[])
    md = format_evidence_markdown(evidence)

    # Top 5 should appear
    assert "bash" in md
    assert "read_file" in md
    assert "write_file" in md
    assert "grep" in md
    assert "glob" in md
    # 6th tool should NOT appear in the top tools section
    # (We check that LSP is absent from the tools listing — it may appear elsewhere)
    # Find the tools section and verify LSP isn't listed there
    # Simple check: the formatted top-tools list should have exactly 5 entries
    tool_lines = [ln for ln in md.split("\n") if "LSP" in ln and "call" in ln.lower()]
    assert len(tool_lines) == 0


# ---------------------------------------------------------------------------
# AC7 — Journal entries appear in chronological order in the formatted output
# ---------------------------------------------------------------------------


def test_format_journal_entries_in_chronological_order():
    entries = [
        make_journal_entry(date(2026, 3, 12), "Latest entry"),
        make_journal_entry(date(2026, 3, 10), "Earliest entry"),
        make_journal_entry(date(2026, 3, 11), "Middle entry"),
    ]
    evidence = combine_evidence(sessions=[], journal_entries=entries)
    md = format_evidence_markdown(evidence)

    pos_earliest = md.index("Earliest entry")
    pos_middle = md.index("Middle entry")
    pos_latest = md.index("Latest entry")

    assert pos_earliest < pos_middle < pos_latest


# ---------------------------------------------------------------------------
# Edge: Both inputs empty — valid WeeklyEvidence, both flags False
# ---------------------------------------------------------------------------


def test_both_empty_returns_valid_evidence():
    evidence = combine_evidence(sessions=[], journal_entries=[])

    assert isinstance(evidence, WeeklyEvidence)
    assert evidence.has_session_data is False
    assert evidence.has_journal_data is False
    assert evidence.total_sessions == 0
    assert evidence.total_session_time_minutes == pytest.approx(0.0)
    assert evidence.total_user_messages == 0


def test_both_empty_gaps_section_lists_both_sources():
    evidence = combine_evidence(sessions=[], journal_entries=[])
    md = format_evidence_markdown(evidence)

    lower = md.lower()
    assert "session" in lower
    assert "journal" in lower


# ---------------------------------------------------------------------------
# Edge: Sessions with None durations — skip in time, still count in total_sessions
# ---------------------------------------------------------------------------


def test_none_duration_session_still_counted_in_total_sessions():
    sessions = [
        make_session(session_id="s1", duration_minutes=None),
        make_session(session_id="s2", duration_minutes=None),
    ]
    evidence = combine_evidence(sessions=sessions, journal_entries=[])

    assert evidence.total_sessions == 2
    assert evidence.total_session_time_minutes == pytest.approx(0.0)


def test_mixed_durations_counts_all_sessions():
    sessions = [
        make_session(session_id="s1", duration_minutes=30.0),
        make_session(session_id="s2", duration_minutes=None),
        make_session(session_id="s3", duration_minutes=45.0),
    ]
    evidence = combine_evidence(sessions=sessions, journal_entries=[])

    assert evidence.total_sessions == 3
    assert evidence.total_session_time_minutes == pytest.approx(75.0)


# ---------------------------------------------------------------------------
# Edge: week_ending not provided — defaults to today
# ---------------------------------------------------------------------------


def test_week_ending_defaults_to_today():
    evidence = combine_evidence(sessions=[], journal_entries=[])

    assert evidence.week_ending == date.today()


def test_week_ending_uses_provided_date():
    target = date(2026, 3, 7)
    evidence = combine_evidence(sessions=[], journal_entries=[], week_ending=target)

    assert evidence.week_ending == target


# ---------------------------------------------------------------------------
# Contract: combine_evidence returns WeeklyEvidence dataclass
# ---------------------------------------------------------------------------


def test_combine_evidence_returns_weekly_evidence():
    evidence = combine_evidence(sessions=[], journal_entries=[])

    assert isinstance(evidence, WeeklyEvidence)


def test_weekly_evidence_stores_sessions_and_entries():
    sessions = [make_session()]
    entries = [make_journal_entry(date(2026, 3, 10))]
    evidence = combine_evidence(sessions=sessions, journal_entries=entries)

    assert evidence.sessions == sessions
    assert evidence.journal_entries == entries


def test_total_sessions_matches_sessions_list_length():
    sessions = [
        make_session(session_id="s1"),
        make_session(session_id="s2"),
        make_session(session_id="s3"),
    ]
    evidence = combine_evidence(sessions=sessions, journal_entries=[])

    assert evidence.total_sessions == 3
