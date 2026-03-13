"""F-004: Report Store.

Persistence layer for weekly coaching reports.
Saves and retrieves week-of-YYYY-MM-DD.md files from a reports directory.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


@dataclass
class WeeklyReport:
    """A stored weekly report."""

    week_of: date  # Monday date of the week
    path: Path  # full path to the file
    content: str  # raw markdown content


def _to_monday(d: date) -> date:
    """Return the Monday of the week containing d."""
    return d - timedelta(days=d.weekday())


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
            Monday of the current week. Non-Monday dates are adjusted
            back to that week's Monday.

    Returns:
        Path to the saved file.
    """
    if week_of is None:
        week_of = date.today()
    monday = _to_monday(week_of)
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"week-of-{monday}.md"
    path.write_text(content)
    return path


def list_reports(reports_dir: Path) -> list[WeeklyReport]:
    """List all weekly reports, newest first.

    Reads and returns all week-of-*.md files from reports_dir.
    Files whose names don't parse as valid dates are silently skipped.
    Returns [] if reports_dir doesn't exist.
    """
    if not reports_dir.is_dir():
        return []

    reports: list[WeeklyReport] = []
    for path in reports_dir.glob("week-of-*.md"):
        stem = path.stem  # e.g. "week-of-2024-01-15"
        date_part = stem[len("week-of-") :]
        try:
            week_of = date.fromisoformat(date_part)
        except ValueError:
            continue  # skip unparseable names like week-of-not-a-date.md
        reports.append(WeeklyReport(week_of=week_of, path=path, content=path.read_text()))

    reports.sort(key=lambda r: r.week_of, reverse=True)
    return reports


def latest_report(reports_dir: Path) -> WeeklyReport | None:
    """Return the most recent weekly report, or None if none exist."""
    reports = list_reports(reports_dir)
    return reports[0] if reports else None
