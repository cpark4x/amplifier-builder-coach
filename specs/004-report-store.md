# Feature 004: Report Store

## Summary

Save and retrieve weekly reports from the `data/reports/` directory. This is
the persistence layer for the coaching pipeline — the writer saves reports here,
and the coaching agent reads historical reports for trend comparison.

## Module

`src/builder_coach/report_store.py`

## Interfaces

```python
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass
class WeeklyReport:
    """A stored weekly report."""
    week_of: date             # Monday date of the week
    path: Path                # full path to the file
    content: str              # raw markdown content


def save_report(
    content: str,
    reports_dir: Path,
    week_of: date | None = None,
) -> Path:
    """Save a weekly report to disk.

    Args:
        content: Full markdown report content.
        reports_dir: Directory to save in (e.g., data/reports/).
        week_of: Monday date for the filename. Defaults to the
            Monday of the current week.

    Returns:
        Path to the saved file.
    """


def list_reports(reports_dir: Path) -> list[WeeklyReport]:
    """List all weekly reports, newest first.

    Reads and returns all week-of-*.md files from reports_dir.
    """


def latest_report(reports_dir: Path) -> WeeklyReport | None:
    """Return the most recent weekly report, or None if none exist."""
```

## Acceptance Criteria

1. `save_report` writes to `{reports_dir}/week-of-{YYYY-MM-DD}.md`
2. The date in the filename is always a Monday (adjusts if given a non-Monday)
3. `save_report` creates the reports directory if it doesn't exist
4. `save_report` overwrites if a report for that week already exists
5. `list_reports` returns all `week-of-*.md` files, parsed and sorted newest-first
6. `list_reports` ignores non-matching files (like `.gitkeep`)
7. `latest_report` returns None when directory is empty or missing

## Edge Cases

- `reports_dir` doesn't exist → `save_report` creates it; `list_reports` returns empty
- File named `week-of-not-a-date.md` exists → skip it, don't error
- `week_of` is a Wednesday → adjust to the Monday of that week
- Report content is empty string → save it anyway (valid edge case)

## Test File

`tests/test_report_store.py`

## Dependencies

- Standard library only

## Not In Scope

- Report content parsing (extracting levels or chart data from saved reports)
- Report diffing or merging
- Deleting old reports