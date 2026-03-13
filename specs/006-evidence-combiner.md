# Feature 006: Evidence Combiner

## Summary

Merge session extraction data and journal entries into a single weekly evidence
package that the coaching agent consumes. This is the glue between the two data
sources — session logs (automatic) and journal (self-reported).

## Module

`src/builder_coach/evidence.py`

## Interfaces

```python
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


def format_evidence_markdown(evidence: WeeklyEvidence) -> str:
    """Render weekly evidence as markdown for the coaching agent.

    Produces the 'Combined Weekly Evidence' format that the coaching
    agent expects as input. Includes:
    - Session summary (count, total time, top tools)
    - Journal entries (raw text, organized by date)
    - Evidence gaps (missing sessions, missing journal, etc.)

    Returns:
        Markdown string ready to inject into the coaching agent prompt.
    """
```

## Acceptance Criteria

1. `total_session_time_minutes` sums duration across all sessions (skips None durations)
2. `total_user_messages` sums user_message_count across all sessions
3. `has_session_data` is True when sessions list is non-empty
4. `has_journal_data` is True when journal_entries list is non-empty
5. `format_evidence_markdown` includes an "Evidence Gaps" section listing missing sources
6. `format_evidence_markdown` includes top 5 tools by call count across all sessions
7. Journal entries appear in chronological order in the formatted output

## Edge Cases

- Both inputs empty → valid WeeklyEvidence with both flags False, gaps section lists both
- Sessions with None durations → skip in time calculation, still count in total_sessions
- week_ending not provided → defaults to today

## Test File

`tests/test_evidence.py`

## Dependencies

- `builder_coach.journal_parser` (JournalEntry)
- `builder_coach.session_extractor` (SessionSummary)

## Not In Scope

- Evaluating the evidence (coaching agent's job)
- Filtering sessions or entries by date (caller's responsibility — use session_discovery and journal_parser filtering)
- Persisting the combined evidence (it's passed through the recipe pipeline)