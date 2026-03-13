# Feature 007: Historical Trend Loader

## Summary

Parse saved weekly reports to extract dimension levels over time. The coaching
agent needs to compare this week's evaluation to prior weeks — this module reads
past reports and extracts the structured data needed for trend analysis and
growth chart trajectory arrows.

## Module

`src/builder_coach/historical.py`

## Interfaces

```python
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from builder_coach.growth_chart import Level


@dataclass
class WeekSnapshot:
    """Dimension levels from a single week's report."""
    week_of: date
    problem_selection: Level | None = None
    leverage_ratio: Level | None = None
    taste: Level | None = None
    ambition_trajectory: Level | None = None
    visibility: Level | None = None


def parse_report_levels(content: str) -> dict[str, Level]:
    """Extract dimension levels from a weekly report's growth chart section.

    Looks for the trajectory table in the report (lines matching
    'Dimension Name: Level' or 'Dimension Name: OldLevel → NewLevel').

    Returns:
        Dict mapping dimension name to its Level. Missing dimensions
        are omitted from the dict.
    """


def load_history(
    reports_dir: Path,
    weeks: int = 8,
) -> list[WeekSnapshot]:
    """Load dimension levels from the most recent N weekly reports.

    Args:
        reports_dir: Directory containing week-of-*.md files.
        weeks: Maximum number of weeks to load. Default 8.

    Returns:
        List of WeekSnapshot, newest first, up to `weeks` entries.
    """


def previous_levels(history: list[WeekSnapshot]) -> WeekSnapshot | None:
    """Return the most recent prior week's snapshot, or None if no history.

    Convenience function: from a history list, return the second entry
    (index 1) if it exists, since index 0 is the current week.
    If history has fewer than 2 entries, returns None.
    """
```

## Acceptance Criteria

1. `parse_report_levels` extracts levels from both formats: "Dimension: Level" and "Dimension: Old → New ▲"
2. `parse_report_levels` is case-insensitive for level names
3. `load_history` reads only `week-of-*.md` files, ignores others
4. `load_history` returns at most `weeks` entries, newest first
5. `previous_levels` returns None when history has 0 or 1 entries
6. Missing dimensions in a report result in None values in WeekSnapshot

## Edge Cases

- Report has no growth chart section → all dimensions None in snapshot
- Report has some dimensions but not all → partial snapshot (present ones filled, rest None)
- Level string doesn't match any Level enum value → that dimension is None
- reports_dir doesn't exist → return empty list
- Duplicate week dates (shouldn't happen) → take the first one found

## Test File

`tests/test_historical.py`

## Dependencies

- `builder_coach.growth_chart` (Level enum)
- `builder_coach.report_store` (for file listing pattern, but not imported — uses its own parsing)

## Not In Scope

- Generating trend narratives ("you've improved over 3 weeks") — coaching agent's job
- Modifying or updating historical reports
- Anything beyond level extraction (not parsing the letter content)