# Feature 003: Growth Chart Renderer

## Summary

Render a text-based growth chart showing the builder's current shape across
the five dimensions. This is "Part 2" of the weekly report — a visual snapshot
of where you are and how you've changed.

## Module

`src/builder_coach/growth_chart.py`

## Interfaces

```python
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


def render_chart(shape: BuilderShape) -> str:
    """Render a text-based growth chart.

    Returns a string containing:
    1. A radar-style visual showing the five dimensions and levels
    2. A trajectory table showing changes from previous week
       (omitted on cold start when all previous values are None)

    The output is valid markdown, ready to embed in the weekly report.
    """


def level_from_string(s: str) -> Level:
    """Parse a level string case-insensitively.

    Args:
        s: Level name (e.g., "developing", "STRONG", "Emerging")

    Returns:
        Matching Level enum value.

    Raises:
        ValueError: If string doesn't match any level.
    """
```

## Acceptance Criteria

1. `render_chart` output contains all five dimension names
2. Each dimension shows its current level in the visual
3. Trajectory table shows `▲` for improvement, `▼` for regression, `→` for no change
4. When all `previous` values are None (cold start), trajectory table is omitted entirely
5. When some `previous` values are None (partial history), show `(new)` instead of arrow
6. Output is valid markdown (no broken formatting)
7. `level_from_string` is case-insensitive
8. `level_from_string` raises ValueError for unknown strings

## Expected Output Shape

```
=== YOUR BUILDER SHAPE ===

              Problem Selection
                   [Level]
                     |
Visibility ----+----+----+---- Leverage Ratio
  [Level]      |         |       [Level]
               +----+----+
              /           \
    Ambition               Taste
  Trajectory              [Level]
    [Level]

Problem Selection:  Developing → Strong ▲
Leverage Ratio:     Emerging (no change) →
Taste:              Developing (no change) →
Ambition Trajectory: Low → Emerging ▲
Visibility:         Low (no change) →
```

## Test File

`tests/test_growth_chart.py`

## Dependencies

- Standard library only (enum, dataclasses)

## Not In Scope

- Generating actual images (SVG, PNG) — text only for now
- Comparing across more than one previous week (just current vs. previous)
- Deciding what level a dimension should be — that's the coaching agent's job