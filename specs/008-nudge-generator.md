# Feature 008: Nudge Generator

## Summary

Produce a single-line session intention based on the latest weekly report and
recent session patterns. This is the lightweight "session-start nudge" — one
line that frames today's work without lengthy briefing.

## Module

`src/builder_coach/nudge.py`

## Interfaces

```python
from dataclasses import dataclass

from builder_coach.growth_chart import Level
from builder_coach.historical import WeekSnapshot
from builder_coach.report_store import WeeklyReport


@dataclass
class NudgeContext:
    """Inputs for generating a session nudge."""
    latest_report: WeeklyReport | None
    current_levels: WeekSnapshot | None
    sessions_since_report: int          # sessions since the latest report


def select_nudge_dimension(context: NudgeContext) -> str | None:
    """Choose which dimension to nudge on.

    Priority logic:
    1. Lowest-level dimension (most room to grow)
    2. On tie, prefer: Visibility > Leverage > Taste > Ambition > Problem Selection
       (visibility is most commonly neglected)
    3. If no levels available (cold start), return None

    Returns:
        Dimension name, or None if no data available.
    """


def format_nudge(
    dimension: str,
    level: Level,
    report_excerpt: str = "",
) -> str:
    """Format a single-line nudge for the selected dimension.

    The nudge must be:
    - Exactly one sentence
    - Specific to the dimension and current level
    - Actionable for today's session
    - Not a generic motivational quote

    Args:
        dimension: Which dimension to focus on.
        level: Current level for that dimension.
        report_excerpt: Optional relevant excerpt from latest report.

    Returns:
        A single-line nudge string.
    """
```

## Acceptance Criteria

1. `select_nudge_dimension` returns the dimension with the lowest level
2. Tie-breaking follows the specified priority order
3. Returns None when no level data exists (cold start)
4. `format_nudge` returns exactly one sentence (one terminal period, no newlines)
5. Nudge contains the dimension name (so the user knows what it's about)
6. Nudge length is under 200 characters
7. Nudge does not contain generic phrases: "keep going", "push yourself", "stay focused"

## Edge Cases

- No latest report (first session ever) → return None from select, caller handles cold start
- All dimensions at the same level → tie-breaking order applies
- All dimensions at Exceptional → still pick one (even high performers get nudges)

## Test File

`tests/test_nudge.py`

## Dependencies

- `builder_coach.growth_chart` (Level)
- `builder_coach.historical` (WeekSnapshot)
- `builder_coach.report_store` (WeeklyReport)

## Not In Scope

- Multi-line nudges or briefings
- Nudge history tracking (what nudges were given before)
- Generating the report excerpt (caller provides it)