"""Tests for F-008: Nudge Generator.

Strict TDD — tests written before implementation.
All tests must FAIL before any implementation code is written.
"""

from datetime import date

import pytest

from builder_coach.growth_chart import Level
from builder_coach.historical import WeekSnapshot
from builder_coach.nudge import NudgeContext, format_nudge, select_nudge_dimension
from builder_coach.report_store import WeeklyReport

# ---------------------------------------------------------------------------
# Helpers — build NudgeContext quickly
# ---------------------------------------------------------------------------

_WEEK_OF = date(2024, 1, 15)
_DUMMY_PATH = None  # WeeklyReport.path; unused in nudge logic

_LATEST_REPORT = WeeklyReport(
    week_of=_WEEK_OF,
    path=None,  # type: ignore[arg-type]
    content="## Growth Chart\n\nProblem Selection: Developing (new)\n",
)


def _snap(**kwargs: Level) -> WeekSnapshot:
    """Build a WeekSnapshot with only the supplied dimension levels set."""
    return WeekSnapshot(week_of=_WEEK_OF, **kwargs)


def _all_snap(level: Level) -> WeekSnapshot:
    """Build a WeekSnapshot with all five dimensions at *level*."""
    return WeekSnapshot(
        week_of=_WEEK_OF,
        problem_selection=level,
        leverage_ratio=level,
        taste=level,
        ambition_trajectory=level,
        visibility=level,
    )


def _ctx(
    current_levels: WeekSnapshot | None,
    *,
    latest_report: WeeklyReport | None = _LATEST_REPORT,
    sessions_since_report: int = 1,
) -> NudgeContext:
    return NudgeContext(
        latest_report=latest_report,
        current_levels=current_levels,
        sessions_since_report=sessions_since_report,
    )


# ---------------------------------------------------------------------------
# NudgeContext dataclass
# ---------------------------------------------------------------------------


def test_nudge_context_is_a_dataclass() -> None:
    """NudgeContext can be constructed with the three required fields."""
    ctx = NudgeContext(
        latest_report=None,
        current_levels=None,
        sessions_since_report=0,
    )
    assert ctx.latest_report is None
    assert ctx.current_levels is None
    assert ctx.sessions_since_report == 0


def test_nudge_context_accepts_real_report_and_snapshot() -> None:
    """NudgeContext stores the objects passed in."""
    snap = _all_snap(Level.DEVELOPING)
    ctx = NudgeContext(
        latest_report=_LATEST_REPORT,
        current_levels=snap,
        sessions_since_report=3,
    )
    assert ctx.latest_report is _LATEST_REPORT
    assert ctx.current_levels is snap
    assert ctx.sessions_since_report == 3


# ---------------------------------------------------------------------------
# select_nudge_dimension — cold start (returns None)
# ---------------------------------------------------------------------------


def test_select_nudge_dimension_returns_none_when_current_levels_is_none() -> None:
    """Cold start: no current_levels → None."""
    ctx = _ctx(current_levels=None)
    assert select_nudge_dimension(ctx) is None


def test_select_nudge_dimension_returns_none_when_all_dimension_levels_are_none() -> None:
    """WeekSnapshot with all fields None (no data parsed) → None."""
    snap = WeekSnapshot(week_of=_WEEK_OF)  # all dimension fields default to None
    ctx = _ctx(current_levels=snap)
    assert select_nudge_dimension(ctx) is None


def test_select_nudge_dimension_returns_none_on_first_session_ever() -> None:
    """First session ever: no latest_report AND no current_levels → None."""
    ctx = NudgeContext(
        latest_report=None,
        current_levels=None,
        sessions_since_report=0,
    )
    assert select_nudge_dimension(ctx) is None


# ---------------------------------------------------------------------------
# select_nudge_dimension — clear lowest-level winner
# ---------------------------------------------------------------------------


def test_select_nudge_dimension_returns_lowest_level_dimension() -> None:
    """Dimension at LOW is returned when others are higher."""
    snap = _snap(
        problem_selection=Level.STRONG,
        leverage_ratio=Level.DEVELOPING,
        taste=Level.LOW,  # lowest
        ambition_trajectory=Level.STRONG,
        visibility=Level.DEVELOPING,
    )
    assert select_nudge_dimension(_ctx(snap)) == "Taste"


def test_select_nudge_dimension_single_dimension_available() -> None:
    """When only one dimension has a level, it is returned regardless of its value."""
    snap = _snap(visibility=Level.EXCEPTIONAL)
    assert select_nudge_dimension(_ctx(snap)) == "Visibility"


def test_select_nudge_dimension_lowest_is_emerging() -> None:
    """Returns the Emerging dimension when it's clearly the lowest."""
    snap = _snap(
        problem_selection=Level.STRONG,
        leverage_ratio=Level.DEVELOPING,
        ambition_trajectory=Level.EMERGING,  # lowest
        visibility=Level.STRONG,
    )
    assert select_nudge_dimension(_ctx(snap)) == "Ambition Trajectory"


def test_select_nudge_dimension_returns_string() -> None:
    """Return type is str, not Level or anything else."""
    snap = _all_snap(Level.DEVELOPING)
    result = select_nudge_dimension(_ctx(snap))
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# select_nudge_dimension — tie-breaking: explicit priority pairs
# ---------------------------------------------------------------------------


def test_select_nudge_dimension_tiebreak_visibility_over_leverage_ratio() -> None:
    """Visibility wins over Leverage Ratio on equal level."""
    snap = _snap(
        visibility=Level.LOW,
        leverage_ratio=Level.LOW,
        taste=Level.STRONG,
        ambition_trajectory=Level.STRONG,
        problem_selection=Level.STRONG,
    )
    assert select_nudge_dimension(_ctx(snap)) == "Visibility"


def test_select_nudge_dimension_tiebreak_leverage_ratio_over_taste() -> None:
    """Leverage Ratio wins over Taste on equal level (Visibility absent)."""
    snap = _snap(
        leverage_ratio=Level.EMERGING,
        taste=Level.EMERGING,
        ambition_trajectory=Level.STRONG,
        problem_selection=Level.STRONG,
    )
    assert select_nudge_dimension(_ctx(snap)) == "Leverage Ratio"


def test_select_nudge_dimension_tiebreak_taste_over_ambition_trajectory() -> None:
    """Taste wins over Ambition Trajectory on equal level (Visibility/Leverage absent)."""
    snap = _snap(
        taste=Level.DEVELOPING,
        ambition_trajectory=Level.DEVELOPING,
        problem_selection=Level.STRONG,
    )
    assert select_nudge_dimension(_ctx(snap)) == "Taste"


def test_select_nudge_dimension_tiebreak_ambition_trajectory_over_problem_selection() -> None:
    """Ambition Trajectory wins over Problem Selection on equal level."""
    snap = _snap(
        ambition_trajectory=Level.STRONG,
        problem_selection=Level.STRONG,
    )
    assert select_nudge_dimension(_ctx(snap)) == "Ambition Trajectory"


# ---------------------------------------------------------------------------
# select_nudge_dimension — tie-breaking: all five at same level
# ---------------------------------------------------------------------------


def test_select_nudge_dimension_all_same_level_picks_visibility() -> None:
    """When all five dimensions are tied, Visibility (highest priority) is selected."""
    snap = _all_snap(Level.DEVELOPING)
    assert select_nudge_dimension(_ctx(snap)) == "Visibility"


def test_select_nudge_dimension_all_low_picks_visibility() -> None:
    """All LOW → Visibility is still selected (first in priority)."""
    snap = _all_snap(Level.LOW)
    assert select_nudge_dimension(_ctx(snap)) == "Visibility"


def test_select_nudge_dimension_all_exceptional_picks_visibility() -> None:
    """Even at Exceptional across all dimensions, Visibility is selected."""
    snap = _all_snap(Level.EXCEPTIONAL)
    assert select_nudge_dimension(_ctx(snap)) == "Visibility"


def test_select_nudge_dimension_all_strong_picks_visibility() -> None:
    """All STRONG → Visibility wins."""
    snap = _all_snap(Level.STRONG)
    assert select_nudge_dimension(_ctx(snap)) == "Visibility"


# ---------------------------------------------------------------------------
# select_nudge_dimension — partial snapshot (some dimensions None)
# ---------------------------------------------------------------------------


def test_select_nudge_dimension_skips_none_dimensions() -> None:
    """None-valued dimensions are excluded from selection."""
    snap = _snap(
        problem_selection=Level.LOW,
        taste=Level.DEVELOPING,
        # leverage_ratio, ambition_trajectory, visibility all None
    )
    assert select_nudge_dimension(_ctx(snap)) == "Problem Selection"


def test_select_nudge_dimension_partial_tie_respects_priority() -> None:
    """Partial snapshot with a tie: priority order still applies."""
    # Only Taste and Problem Selection present, both EMERGING.
    # Taste has higher priority than Problem Selection.
    snap = _snap(
        taste=Level.EMERGING,
        problem_selection=Level.EMERGING,
    )
    assert select_nudge_dimension(_ctx(snap)) == "Taste"


# ---------------------------------------------------------------------------
# format_nudge — structural requirements (acceptance criteria)
# ---------------------------------------------------------------------------


def test_format_nudge_ends_with_exactly_one_period() -> None:
    """Nudge must end with exactly one terminal period."""
    result = format_nudge("Visibility", Level.LOW)
    assert result.endswith("."), f"Expected nudge to end with '.', got: {result!r}"
    # No double period
    assert not result.endswith(".."), f"Nudge has double period: {result!r}"


def test_format_nudge_contains_no_newlines() -> None:
    """Nudge must be a single line — no newline characters."""
    result = format_nudge("Visibility", Level.LOW)
    assert "\n" not in result
    assert "\r" not in result


def test_format_nudge_contains_dimension_name() -> None:
    """Nudge must contain the dimension name it was generated for."""
    for dim, level in [
        ("Visibility", Level.LOW),
        ("Leverage Ratio", Level.EMERGING),
        ("Taste", Level.DEVELOPING),
        ("Ambition Trajectory", Level.STRONG),
        ("Problem Selection", Level.EXCEPTIONAL),
    ]:
        result = format_nudge(dim, level)
        assert dim in result, f"Dimension '{dim}' not found in nudge: {result!r}"


def test_format_nudge_length_under_200_characters() -> None:
    """Nudge must be under 200 characters."""
    result = format_nudge("Visibility", Level.LOW)
    assert len(result) < 200, f"Nudge too long ({len(result)} chars): {result!r}"


def test_format_nudge_no_generic_keep_going() -> None:
    """Nudge must not contain 'keep going'."""
    result = format_nudge("Visibility", Level.LOW)
    assert "keep going" not in result.lower()


def test_format_nudge_no_generic_push_yourself() -> None:
    """Nudge must not contain 'push yourself'."""
    result = format_nudge("Visibility", Level.LOW)
    assert "push yourself" not in result.lower()


def test_format_nudge_no_generic_stay_focused() -> None:
    """Nudge must not contain 'stay focused'."""
    result = format_nudge("Visibility", Level.LOW)
    assert "stay focused" not in result.lower()


def test_format_nudge_returns_string() -> None:
    """Return type is str."""
    result = format_nudge("Taste", Level.DEVELOPING)
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# format_nudge — parametrized over all 25 dimension×level combinations
# ---------------------------------------------------------------------------

_ALL_DIMENSIONS = [
    "Visibility",
    "Leverage Ratio",
    "Taste",
    "Ambition Trajectory",
    "Problem Selection",
]
_ALL_LEVELS = [
    Level.LOW,
    Level.EMERGING,
    Level.DEVELOPING,
    Level.STRONG,
    Level.EXCEPTIONAL,
]
_ALL_COMBOS = [(dim, lv) for dim in _ALL_DIMENSIONS for lv in _ALL_LEVELS]


@pytest.mark.parametrize("dimension,level", _ALL_COMBOS)
def test_format_nudge_all_combos_single_sentence(dimension: str, level: Level) -> None:
    """Every dimension×level combo returns exactly one sentence (ends with '.', no newlines)."""
    result = format_nudge(dimension, level)
    assert isinstance(result, str)
    assert result.endswith("."), f"{dimension}/{level.value}: nudge does not end with '.'"
    assert "\n" not in result, f"{dimension}/{level.value}: nudge contains newline"


@pytest.mark.parametrize("dimension,level", _ALL_COMBOS)
def test_format_nudge_all_combos_contains_dimension_name(dimension: str, level: Level) -> None:
    """Every combo's nudge contains its dimension name."""
    result = format_nudge(dimension, level)
    assert dimension in result, (
        f"{dimension}/{level.value}: dimension name missing from nudge: {result!r}"
    )


@pytest.mark.parametrize("dimension,level", _ALL_COMBOS)
def test_format_nudge_all_combos_under_200_chars(dimension: str, level: Level) -> None:
    """Every combo's nudge is under 200 characters."""
    result = format_nudge(dimension, level)
    assert len(result) < 200, (
        f"{dimension}/{level.value}: nudge is {len(result)} chars (limit 200): {result!r}"
    )


@pytest.mark.parametrize("dimension,level", _ALL_COMBOS)
def test_format_nudge_all_combos_no_generic_phrases(dimension: str, level: Level) -> None:
    """Every combo's nudge avoids the banned generic phrases."""
    result = format_nudge(dimension, level)
    lowered = result.lower()
    for phrase in ("keep going", "push yourself", "stay focused"):
        assert phrase not in lowered, (
            f"{dimension}/{level.value}: banned phrase '{phrase}' in nudge: {result!r}"
        )


# ---------------------------------------------------------------------------
# format_nudge — optional report_excerpt parameter (does not break contract)
# ---------------------------------------------------------------------------


def test_format_nudge_accepts_report_excerpt_without_error() -> None:
    """Passing a report_excerpt does not raise an exception."""
    result = format_nudge(
        "Visibility",
        Level.DEVELOPING,
        report_excerpt="Visibility remains low — no public posts this week.",
    )
    assert isinstance(result, str)
    assert result.endswith(".")


def test_format_nudge_empty_report_excerpt_same_as_no_excerpt() -> None:
    """Empty string report_excerpt produces the same output as omitting it."""
    without = format_nudge("Taste", Level.STRONG)
    with_empty = format_nudge("Taste", Level.STRONG, report_excerpt="")
    assert without == with_empty
