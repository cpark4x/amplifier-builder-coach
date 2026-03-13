"""F-006: Evidence Combiner.

Merge session extraction data and journal entries into a single weekly
evidence package that the coaching agent consumes. Standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from builder_coach.journal_parser import JournalEntry
from builder_coach.session_extractor import SessionSummary


@dataclass
class WeeklyEvidence:
    """Combined evidence for one week's coaching evaluation."""

    week_ending: date
    sessions: list[SessionSummary] = field(default_factory=list)
    journal_entries: list[JournalEntry] = field(default_factory=list)
    total_session_time_minutes: float = 0.0
    total_user_messages: int = 0
    total_sessions: int = 0
    has_session_data: bool = False
    has_journal_data: bool = False


def combine_evidence(
    sessions: list[SessionSummary],
    journal_entries: list[JournalEntry],
    week_ending: date | None = None,
) -> WeeklyEvidence:
    """Combine session and journal data into a weekly evidence package.

    Computes aggregate metrics from the session list and flags which
    data sources are available. The coaching agent uses these flags
    to adjust its evaluation (e.g., cold start, missing journal).

    Args:
        sessions: Extracted session summaries for the week.
        journal_entries: Parsed journal entries for the week.
        week_ending: End date of the week. Defaults to today.

    Returns:
        WeeklyEvidence with aggregated metrics and source flags.
    """
    if week_ending is None:
        week_ending = date.today()

    total_time = 0.0
    for s in sessions:
        if s.duration is not None:
            total_time += s.duration.total_seconds() / 60.0

    total_messages = sum(s.user_message_count for s in sessions)

    return WeeklyEvidence(
        week_ending=week_ending,
        sessions=sessions,
        journal_entries=journal_entries,
        total_session_time_minutes=total_time,
        total_user_messages=total_messages,
        total_sessions=len(sessions),
        has_session_data=len(sessions) > 0,
        has_journal_data=len(journal_entries) > 0,
    )


def format_evidence_markdown(evidence: WeeklyEvidence) -> str:
    """Render weekly evidence as markdown for the coaching agent.

    Produces the 'Combined Weekly Evidence' format that the coaching
    agent expects as input. Includes:
    - Session summary (count, total time, top tools)
    - Journal entries (raw text, organized by date, chronological)
    - Evidence gaps (missing sessions, missing journal, etc.)

    Returns:
        Markdown string ready to inject into the coaching agent prompt.
    """
    lines: list[str] = []

    lines.append(f"## Combined Weekly Evidence — Week of {evidence.week_ending}")
    lines.append("")

    # --- Sessions section ---
    lines.append(f"### Sessions ({evidence.total_sessions} total)")
    lines.append("")
    lines.append(f"- **Total time:** {evidence.total_session_time_minutes:.1f} minutes")
    lines.append(f"- **Total user messages:** {evidence.total_user_messages}")
    lines.append("")

    # Top 5 tools aggregated across all sessions
    tool_counts: dict[str, int] = {}
    for session in evidence.sessions:
        for tu in session.tool_usage:
            tool_counts[tu.tool_name] = tool_counts.get(tu.tool_name, 0) + tu.call_count

    top_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    if top_tools:
        lines.append("#### Top Tools")
        lines.append("")
        lines.append("| Tool | Calls |")
        lines.append("|------|-------|")
        for tool_name, count in top_tools:
            lines.append(f"| {tool_name} | {count} |")
        lines.append("")

    # Session descriptions
    if evidence.sessions:
        lines.append("#### Session Details")
        lines.append("")
        for s in evidence.sessions:
            start_str = s.start_time.strftime("%Y-%m-%d %H:%M") if s.start_time else "unknown time"
            dur_str = (
                f"{s.duration.total_seconds() / 60:.0f} min"
                if s.duration is not None
                else "duration unknown"
            )
            lines.append(f"- **{s.session_id}** ({start_str}, {dur_str})")
            if s.description:
                lines.append(f"  {s.description}")
        lines.append("")

    # --- Journal section ---
    lines.append("### Journal Entries")
    lines.append("")

    if evidence.journal_entries:
        # Chronological order: oldest first
        sorted_entries = sorted(evidence.journal_entries, key=lambda e: e.date)
        for entry in sorted_entries:
            lines.append(f"#### {entry.date}")
            lines.append("")
            lines.append(entry.raw_text)
            lines.append("")
    else:
        lines.append("_No journal entries for this week._")
        lines.append("")

    # --- Evidence Gaps section ---
    lines.append("### Evidence Gaps")
    lines.append("")

    gaps: list[str] = []
    if not evidence.has_session_data:
        gaps.append("No session data available for this week.")
    if not evidence.has_journal_data:
        gaps.append("No journal entries available for this week.")

    if gaps:
        for gap in gaps:
            lines.append(f"- {gap}")
    else:
        lines.append("None — both session data and journal entries are present.")

    lines.append("")

    return "\n".join(lines)
