"""Tests for the growth chart renderer — F-003.

Covers all 8 acceptance criteria from specs/003-growth-chart-renderer.md
"""

import pytest

from builder_coach.growth_chart import (
    BuilderShape,
    DimensionScore,
    Level,
    level_from_string,
    render_chart,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _full_shape_with_history() -> BuilderShape:
    """All five dimensions have a previous value."""
    return BuilderShape(
        problem_selection=DimensionScore("Problem Selection", Level.STRONG, Level.DEVELOPING),
        leverage_ratio=DimensionScore("Leverage Ratio", Level.EMERGING, Level.EMERGING),
        taste=DimensionScore("Taste", Level.DEVELOPING, Level.STRONG),
        ambition_trajectory=DimensionScore("Ambition Trajectory", Level.EMERGING, Level.LOW),
        visibility=DimensionScore("Visibility", Level.LOW, Level.LOW),
    )


def _cold_start_shape() -> BuilderShape:
    """All five dimensions have no previous value (first-ever assessment)."""
    return BuilderShape(
        problem_selection=DimensionScore("Problem Selection", Level.DEVELOPING),
        leverage_ratio=DimensionScore("Leverage Ratio", Level.EMERGING),
        taste=DimensionScore("Taste", Level.DEVELOPING),
        ambition_trajectory=DimensionScore("Ambition Trajectory", Level.LOW),
        visibility=DimensionScore("Visibility", Level.LOW),
    )


def _partial_history_shape() -> BuilderShape:
    """Some dimensions have history; others are brand-new this week."""
    return BuilderShape(
        problem_selection=DimensionScore("Problem Selection", Level.STRONG, Level.DEVELOPING),
        leverage_ratio=DimensionScore("Leverage Ratio", Level.EMERGING),  # no previous
        taste=DimensionScore("Taste", Level.DEVELOPING, Level.DEVELOPING),
        ambition_trajectory=DimensionScore("Ambition Trajectory", Level.LOW),  # no previous
        visibility=DimensionScore("Visibility", Level.LOW, Level.LOW),
    )


# ---------------------------------------------------------------------------
# AC1: render_chart output contains all five dimension names
# ---------------------------------------------------------------------------


def test_render_chart_contains_all_five_dimension_names():
    output = render_chart(_full_shape_with_history())
    assert "Problem Selection" in output
    assert "Leverage Ratio" in output
    assert "Taste" in output
    assert "Ambition Trajectory" in output
    assert "Visibility" in output


# ---------------------------------------------------------------------------
# AC2: Each dimension shows its current level in the visual
# ---------------------------------------------------------------------------


def test_render_chart_shows_current_level_for_each_dimension():
    shape = BuilderShape(
        problem_selection=DimensionScore("Problem Selection", Level.STRONG),
        leverage_ratio=DimensionScore("Leverage Ratio", Level.EXCEPTIONAL),
        taste=DimensionScore("Taste", Level.LOW),
        ambition_trajectory=DimensionScore("Ambition Trajectory", Level.DEVELOPING),
        visibility=DimensionScore("Visibility", Level.EMERGING),
    )
    output = render_chart(shape)
    assert "Strong" in output
    assert "Exceptional" in output
    assert "Low" in output
    assert "Developing" in output
    assert "Emerging" in output


# ---------------------------------------------------------------------------
# AC3: Trajectory arrows — ▲ improvement, ▼ regression, → no change
# ---------------------------------------------------------------------------


def test_render_chart_trajectory_shows_improvement_arrow():
    """▲ appears when current level is higher than previous."""
    shape = BuilderShape(
        problem_selection=DimensionScore("Problem Selection", Level.STRONG, Level.DEVELOPING),
        leverage_ratio=DimensionScore("Leverage Ratio", Level.EMERGING, Level.EMERGING),
        taste=DimensionScore("Taste", Level.DEVELOPING, Level.DEVELOPING),
        ambition_trajectory=DimensionScore("Ambition Trajectory", Level.LOW, Level.LOW),
        visibility=DimensionScore("Visibility", Level.LOW, Level.LOW),
    )
    output = render_chart(shape)
    assert "▲" in output


def test_render_chart_trajectory_shows_regression_arrow():
    """▼ appears when current level is lower than previous."""
    shape = BuilderShape(
        problem_selection=DimensionScore("Problem Selection", Level.DEVELOPING, Level.STRONG),
        leverage_ratio=DimensionScore("Leverage Ratio", Level.EMERGING, Level.EMERGING),
        taste=DimensionScore("Taste", Level.DEVELOPING, Level.DEVELOPING),
        ambition_trajectory=DimensionScore("Ambition Trajectory", Level.LOW, Level.LOW),
        visibility=DimensionScore("Visibility", Level.LOW, Level.LOW),
    )
    output = render_chart(shape)
    assert "▼" in output


def test_render_chart_trajectory_shows_no_change_arrow():
    """→ appears when current level equals previous."""
    shape = BuilderShape(
        problem_selection=DimensionScore("Problem Selection", Level.DEVELOPING, Level.DEVELOPING),
        leverage_ratio=DimensionScore("Leverage Ratio", Level.EMERGING, Level.EMERGING),
        taste=DimensionScore("Taste", Level.DEVELOPING, Level.DEVELOPING),
        ambition_trajectory=DimensionScore("Ambition Trajectory", Level.LOW, Level.LOW),
        visibility=DimensionScore("Visibility", Level.LOW, Level.LOW),
    )
    output = render_chart(shape)
    assert "→" in output


# ---------------------------------------------------------------------------
# AC4: Cold start — all previous None → trajectory table omitted entirely
# ---------------------------------------------------------------------------


def test_render_chart_cold_start_omits_trajectory_table():
    """When every dimension has no previous value, no trajectory section is rendered."""
    output = render_chart(_cold_start_shape())
    assert "▲" not in output
    assert "▼" not in output
    assert "→" not in output


# ---------------------------------------------------------------------------
# AC5: Partial history — some previous None → show (new) instead of arrow
# ---------------------------------------------------------------------------


def test_render_chart_partial_history_shows_new_for_missing_previous():
    """Dimensions with no previous value display '(new)' in the trajectory table."""
    output = render_chart(_partial_history_shape())
    assert "(new)" in output


def test_render_chart_partial_history_still_shows_arrows_for_tracked_dimensions():
    """Dimensions that have history still render their trajectory arrows."""
    # problem_selection: STRONG from DEVELOPING → ▲
    # taste: DEVELOPING from DEVELOPING → →
    output = render_chart(_partial_history_shape())
    assert "▲" in output
    assert "→" in output


# ---------------------------------------------------------------------------
# AC6: Output is valid markdown
# ---------------------------------------------------------------------------


def test_render_chart_output_is_non_empty_string():
    output = render_chart(_cold_start_shape())
    assert isinstance(output, str)
    assert len(output.strip()) > 0


def test_render_chart_output_has_no_balanced_code_fences():
    """Code fences, if any, must be balanced (even count)."""
    output = render_chart(_full_shape_with_history())
    fence_count = output.count("```")
    assert fence_count % 2 == 0, f"Unbalanced code fences: {fence_count}"


def test_render_chart_output_contains_no_raw_none():
    """The literal string 'None' must never appear — previous=None stays invisible."""
    output = render_chart(_partial_history_shape())
    assert "None" not in output


# ---------------------------------------------------------------------------
# AC7: level_from_string is case-insensitive
# ---------------------------------------------------------------------------


def test_level_from_string_case_insensitive():
    assert level_from_string("low") == Level.LOW
    assert level_from_string("LOW") == Level.LOW
    assert level_from_string("Low") == Level.LOW
    assert level_from_string("emerging") == Level.EMERGING
    assert level_from_string("EMERGING") == Level.EMERGING
    assert level_from_string("developing") == Level.DEVELOPING
    assert level_from_string("DEVELOPING") == Level.DEVELOPING
    assert level_from_string("strong") == Level.STRONG
    assert level_from_string("Strong") == Level.STRONG
    assert level_from_string("exceptional") == Level.EXCEPTIONAL
    assert level_from_string("EXCEPTIONAL") == Level.EXCEPTIONAL


# ---------------------------------------------------------------------------
# AC8: level_from_string raises ValueError for unknown strings
# ---------------------------------------------------------------------------


def test_level_from_string_raises_for_unknown_string():
    with pytest.raises(ValueError):
        level_from_string("unknown")


def test_level_from_string_raises_for_empty_string():
    with pytest.raises(ValueError):
        level_from_string("")


def test_level_from_string_raises_for_numeric_string():
    with pytest.raises(ValueError):
        level_from_string("3")
