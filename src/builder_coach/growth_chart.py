"""Growth chart renderer for the builder coaching system — F-003.

Renders a text-based growth chart showing the builder's current shape across
the five dimensions. Output is valid markdown, ready to embed in the weekly report.
"""

from dataclasses import dataclass
from enum import Enum


class Level(Enum):
    """Qualitative growth levels from the framework."""

    LOW = "Low"
    EMERGING = "Emerging"
    DEVELOPING = "Developing"
    STRONG = "Strong"
    EXCEPTIONAL = "Exceptional"


@dataclass
class DimensionScore:
    """A single dimension's current and previous level."""

    name: str
    current: Level
    previous: Level | None = None  # None on first week (cold start)


@dataclass
class BuilderShape:
    """The builder's complete shape across all five dimensions."""

    problem_selection: DimensionScore
    leverage_ratio: DimensionScore
    taste: DimensionScore
    ambition_trajectory: DimensionScore
    visibility: DimensionScore


# Ordinal rank used to compare levels (lower index = lower level).
_LEVEL_RANK: dict[Level, int] = {
    Level.LOW: 0,
    Level.EMERGING: 1,
    Level.DEVELOPING: 2,
    Level.STRONG: 3,
    Level.EXCEPTIONAL: 4,
}


def level_from_string(s: str) -> Level:
    """Parse a level string case-insensitively.

    Args:
        s: Level name (e.g., "developing", "STRONG", "Emerging")

    Returns:
        Matching Level enum value.

    Raises:
        ValueError: If string doesn't match any level.
    """
    for level in Level:
        if level.value.lower() == s.lower():
            return level
    valid = [lv.value for lv in Level]
    raise ValueError(f"Unknown level: {s!r}. Valid values: {valid}")


def _dimensions(shape: BuilderShape) -> list[DimensionScore]:
    """Return all five dimensions in display order."""
    return [
        shape.problem_selection,
        shape.leverage_ratio,
        shape.taste,
        shape.ambition_trajectory,
        shape.visibility,
    ]


def _render_visual(shape: BuilderShape) -> str:
    """Render the ASCII radar chart section."""
    ps = shape.problem_selection.current.value
    lr = shape.leverage_ratio.current.value
    taste = shape.taste.current.value
    at = shape.ambition_trajectory.current.value
    vis = shape.visibility.current.value

    # Left column is widest at "Exceptional" (11 chars) + 2 leading spaces = 13 chars before |.
    # Use left-justified padding so the vertical bar stays in a consistent column.
    vis_padded = f"{vis:<13}"

    lines = [
        "=== YOUR BUILDER SHAPE ===",
        "",
        "              Problem Selection",
        f"                   {ps}",
        "                     |",
        "Visibility ----+----+----+---- Leverage Ratio",
        f"  {vis_padded}|         |       {lr}",
        "               +----+----+",
        "              /           \\",
        "  Ambition Trajectory      Taste",
        f"      {at:<17}{taste}",
    ]
    return "\n".join(lines)


def _trajectory_row(dim: DimensionScore) -> str:
    """Format a single trajectory table row for one dimension."""
    if dim.previous is None:
        return f"{dim.name}: {dim.current.value} (new)"

    curr_rank = _LEVEL_RANK[dim.current]
    prev_rank = _LEVEL_RANK[dim.previous]

    if curr_rank > prev_rank:
        return f"{dim.name}: {dim.previous.value} \u2192 {dim.current.value} \u25b2"
    if curr_rank < prev_rank:
        return f"{dim.name}: {dim.previous.value} \u2192 {dim.current.value} \u25bc"
    return f"{dim.name}: {dim.current.value} (no change) \u2192"


def render_chart(shape: BuilderShape) -> str:
    """Render a text-based growth chart.

    Returns a string containing:
    1. A radar-style visual showing the five dimensions and levels
    2. A trajectory table showing changes from previous week
       (omitted on cold start when all previous values are None)

    The output is valid markdown, ready to embed in the weekly report.
    """
    visual = _render_visual(shape)
    dims = _dimensions(shape)

    # Cold start: every dimension lacks history — omit the trajectory table entirely.
    if all(d.previous is None for d in dims):
        return visual

    trajectory = "\n".join(_trajectory_row(d) for d in dims)
    return visual + "\n\n" + trajectory
