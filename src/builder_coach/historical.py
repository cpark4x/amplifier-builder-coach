"""F-007: Historical Trend Loader.

Reads saved weekly reports and extracts dimension levels over time so the
coaching agent can compare this week's evaluation to prior weeks.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from builder_coach.growth_chart import Level, level_from_string


@dataclass
class WeekSnapshot:
    """Dimension levels from a single week's report."""

    week_of: date
    problem_selection: Level | None = None
    leverage_ratio: Level | None = None
    taste: Level | None = None
    ambition_trajectory: Level | None = None
    visibility: Level | None = None


# Maps the display name used in the growth chart trajectory table to the
# corresponding WeekSnapshot field name.
_DIMENSION_FIELDS: dict[str, str] = {
    "Problem Selection": "problem_selection",
    "Leverage Ratio": "leverage_ratio",
    "Taste": "taste",
    "Ambition Trajectory": "ambition_trajectory",
    "Visibility": "visibility",
}


def parse_report_levels(content: str) -> dict[str, Level]:
    """Extract dimension levels from a weekly report's growth chart section.

    Handles two trajectory-table formats produced by the growth chart renderer:

    - Simple / cold-start: ``"Problem Selection: Developing (new)"``
    - No-change:           ``"Leverage Ratio: Developing (no change) →"``
    - Transition up/down:  ``"Taste: Emerging → Strong ▲"``

    For transition lines the *current* (new) level is extracted — the word that
    appears after the ``→`` separator.  For all other lines the first word after
    the colon is used.

    Returns:
        Dict mapping dimension display name to its current Level.  Dimensions
        not present in the content are omitted.  Level strings that don't match
        any Level enum value are silently omitted.
    """
    result: dict[str, Level] = {}
    for line in content.splitlines():
        for dim_name in _DIMENSION_FIELDS:
            prefix = f"{dim_name}: "
            if not line.startswith(prefix):
                continue
            rest = line[len(prefix) :]

            # Transition format: "OldLevel → NewLevel [▲▼]"
            # The separator is " → " (space–arrow–space); the no-change suffix
            # " →" has no trailing space, so this branch is NOT triggered for it.
            if " \u2192 " in rest:
                after_arrow = rest.split(" \u2192 ", 1)[1]
                words = after_arrow.split()
            else:
                # Simple / cold-start / no-change: take the first word.
                words = rest.split()

            if not words:
                break  # malformed line — skip this dimension

            level_str = words[0]
            try:
                result[dim_name] = level_from_string(level_str)
            except ValueError:
                pass  # unknown level string → omit this dimension
            break  # matched a dimension name; no need to check others

    return result


def load_history(
    reports_dir: Path,
    weeks: int = 8,
) -> list[WeekSnapshot]:
    """Load dimension levels from the most recent N weekly reports.

    Reads ``week-of-YYYY-MM-DD.md`` files from *reports_dir*, newest first.
    Files whose names don't contain a valid ISO date are silently skipped.
    If the same date appears more than once (shouldn't happen in practice),
    only the first occurrence is kept.

    Args:
        reports_dir: Directory containing ``week-of-*.md`` files.
        weeks: Maximum number of weeks to load.  Default 8.

    Returns:
        List of WeekSnapshot, newest first, up to *weeks* entries.
        Returns ``[]`` if *reports_dir* doesn't exist.
    """
    if not reports_dir.is_dir():
        return []

    # Sort files by the date portion of their stem (ISO strings sort correctly
    # lexicographically), newest first.
    candidates = sorted(
        reports_dir.glob("week-of-*.md"),
        key=lambda p: p.stem,
        reverse=True,
    )

    snapshots: list[WeekSnapshot] = []
    seen: set[date] = set()

    for path in candidates:
        if len(snapshots) >= weeks:
            break

        date_part = path.stem[len("week-of-") :]
        try:
            week_of = date.fromisoformat(date_part)
        except ValueError:
            continue  # skip files with unparseable date names

        if week_of in seen:
            continue  # de-duplicate (guard; shouldn't occur with real filenames)
        seen.add(week_of)

        levels = parse_report_levels(path.read_text())

        snapshots.append(
            WeekSnapshot(
                week_of=week_of,
                problem_selection=levels.get("Problem Selection"),
                leverage_ratio=levels.get("Leverage Ratio"),
                taste=levels.get("Taste"),
                ambition_trajectory=levels.get("Ambition Trajectory"),
                visibility=levels.get("Visibility"),
            )
        )

    return snapshots


def previous_levels(history: list[WeekSnapshot]) -> WeekSnapshot | None:
    """Return the most recent prior week's snapshot, or None if no history.

    Treats *history* as newest-first (as returned by :func:`load_history`).
    Index 0 is the current week; index 1 is the previous week.  Returns
    ``None`` when the list has fewer than two entries.
    """
    if len(history) < 2:
        return None
    return history[1]
