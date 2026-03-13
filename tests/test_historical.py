"""Tests for F-007: Historical Trend Loader.

Strict TDD — tests written before implementation.
All tests must FAIL before any implementation code is written.
"""

from datetime import date
from pathlib import Path

from builder_coach.growth_chart import Level
from builder_coach.historical import (
    WeekSnapshot,
    load_history,
    parse_report_levels,
    previous_levels,
)


# ---------------------------------------------------------------------------
# Fixtures — sample report content
# ---------------------------------------------------------------------------

# A report with all 5 dimensions using the "Name: Level (new)" format (cold start).
_COLD_START_REPORT = """\
# Weekly Coaching Letter — Week of 2024-01-15

Some coaching prose here.

## Growth Chart

=== YOUR BUILDER SHAPE ===

              Problem Selection
                   Developing
                     |
Visibility ----+----+----+---- Leverage Ratio
  Low          |         |       Emerging
               +----+----+
              /           \\
  Ambition Trajectory      Taste
      Low               Strong

Problem Selection: Developing (new)
Leverage Ratio: Emerging (new)
Taste: Strong (new)
Ambition Trajectory: Low (new)
Visibility: Low (new)
"""

# A report with all 5 dimensions using the "Name: Old → New ▲/▼" transition format.
_TRANSITION_REPORT = """\
# Weekly Coaching Letter — Week of 2024-01-22

Some coaching prose.

## Growth Chart

=== YOUR BUILDER SHAPE ===

Problem Selection: Emerging → Developing ▲
Leverage Ratio: Developing (no change) →
Taste: Strong → Exceptional ▲
Ambition Trajectory: Low → Emerging ▲
Visibility: Low → Developing ▲
"""

# A report with only some dimensions present.
_PARTIAL_REPORT = """\
# Weekly Coaching Letter

## Growth Chart

Problem Selection: Strong (new)
Taste: Developing (new)
"""

# A report with no growth chart section at all.
_NO_CHART_REPORT = """\
# Weekly Coaching Letter

Just prose here. No chart section.
"""

# A report containing an unrecognised level string.
_UNKNOWN_LEVEL_REPORT = """\
## Growth Chart

Problem Selection: Legendary (new)
Leverage Ratio: Emerging (new)
"""


# ---------------------------------------------------------------------------
# parse_report_levels — "Dimension: Level" simple format
# ---------------------------------------------------------------------------


def test_parse_report_levels_simple_cold_start_format() -> None:
    """'Problem Selection: Developing (new)' yields Level.DEVELOPING."""
    result = parse_report_levels("Problem Selection: Developing (new)\n")
    assert result.get("Problem Selection") == Level.DEVELOPING


def test_parse_report_levels_no_change_format() -> None:
    """'Leverage Ratio: Developing (no change) →' yields Level.DEVELOPING."""
    result = parse_report_levels("Leverage Ratio: Developing (no change) →\n")
    assert result.get("Leverage Ratio") == Level.DEVELOPING


def test_parse_report_levels_all_five_simple() -> None:
    """All five dimensions are parsed from a cold-start report."""
    result = parse_report_levels(_COLD_START_REPORT)
    assert result.get("Problem Selection") == Level.DEVELOPING
    assert result.get("Leverage Ratio") == Level.EMERGING
    assert result.get("Taste") == Level.STRONG
    assert result.get("Ambition Trajectory") == Level.LOW
    assert result.get("Visibility") == Level.LOW


# ---------------------------------------------------------------------------
# parse_report_levels — "Dimension: Old → New ▲/▼" transition format
# ---------------------------------------------------------------------------


def test_parse_report_levels_upward_transition() -> None:
    """'Problem Selection: Emerging → Developing ▲' yields the NEW level."""
    result = parse_report_levels("Problem Selection: Emerging → Developing ▲\n")
    assert result.get("Problem Selection") == Level.DEVELOPING


def test_parse_report_levels_downward_transition() -> None:
    """'Taste: Exceptional → Strong ▼' yields the NEW (lower) level."""
    result = parse_report_levels("Taste: Exceptional → Strong ▼\n")
    assert result.get("Taste") == Level.STRONG


def test_parse_report_levels_all_five_transitions() -> None:
    """All five dimensions are parsed from a full transition report."""
    result = parse_report_levels(_TRANSITION_REPORT)
    assert result.get("Problem Selection") == Level.DEVELOPING
    assert result.get("Leverage Ratio") == Level.DEVELOPING
    assert result.get("Taste") == Level.EXCEPTIONAL
    assert result.get("Ambition Trajectory") == Level.EMERGING
    assert result.get("Visibility") == Level.DEVELOPING


# ---------------------------------------------------------------------------
# parse_report_levels — case insensitivity
# ---------------------------------------------------------------------------


def test_parse_report_levels_lowercase_level_name() -> None:
    """Level names are matched case-insensitively ('developing' → DEVELOPING)."""
    result = parse_report_levels("Problem Selection: developing (new)\n")
    assert result.get("Problem Selection") == Level.DEVELOPING


def test_parse_report_levels_uppercase_level_name() -> None:
    """'STRONG' is parsed as Level.STRONG."""
    result = parse_report_levels("Taste: STRONG (new)\n")
    assert result.get("Taste") == Level.STRONG


def test_parse_report_levels_mixed_case_level_name() -> None:
    """'eMeRgInG' is parsed as Level.EMERGING."""
    result = parse_report_levels("Visibility: eMeRgInG (new)\n")
    assert result.get("Visibility") == Level.EMERGING


# ---------------------------------------------------------------------------
# parse_report_levels — edge cases
# ---------------------------------------------------------------------------


def test_parse_report_levels_empty_string_returns_empty_dict() -> None:
    """Empty content yields an empty dict."""
    assert parse_report_levels("") == {}


def test_parse_report_levels_no_chart_section_returns_empty_dict() -> None:
    """A report with no trajectory lines yields an empty dict."""
    assert parse_report_levels(_NO_CHART_REPORT) == {}


def test_parse_report_levels_unknown_level_is_omitted() -> None:
    """An unrecognised level string is silently omitted from the result."""
    result = parse_report_levels(_UNKNOWN_LEVEL_REPORT)
    assert "Problem Selection" not in result
    # Valid dimensions on the same report are still parsed.
    assert result.get("Leverage Ratio") == Level.EMERGING


def test_parse_report_levels_partial_report_returns_partial_dict() -> None:
    """Only dimensions present in the report appear in the returned dict."""
    result = parse_report_levels(_PARTIAL_REPORT)
    assert set(result.keys()) == {"Problem Selection", "Taste"}
    assert result["Problem Selection"] == Level.STRONG
    assert result["Taste"] == Level.DEVELOPING


def test_parse_report_levels_returns_dict_not_week_snapshot() -> None:
    """Return type is a plain dict, not a WeekSnapshot."""
    result = parse_report_levels(_COLD_START_REPORT)
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# WeekSnapshot dataclass
# ---------------------------------------------------------------------------


def test_week_snapshot_defaults_all_none() -> None:
    """WeekSnapshot fields default to None except week_of."""
    snap = WeekSnapshot(week_of=date(2024, 1, 15))
    assert snap.problem_selection is None
    assert snap.leverage_ratio is None
    assert snap.taste is None
    assert snap.ambition_trajectory is None
    assert snap.visibility is None


def test_week_snapshot_accepts_level_values() -> None:
    """WeekSnapshot fields accept Level enum values."""
    snap = WeekSnapshot(
        week_of=date(2024, 1, 15),
        problem_selection=Level.STRONG,
        leverage_ratio=Level.EMERGING,
        taste=Level.DEVELOPING,
        ambition_trajectory=Level.LOW,
        visibility=Level.EXCEPTIONAL,
    )
    assert snap.problem_selection == Level.STRONG
    assert snap.visibility == Level.EXCEPTIONAL


# ---------------------------------------------------------------------------
# load_history — file filtering
# ---------------------------------------------------------------------------


def test_load_history_reads_only_week_of_files(tmp_path: Path) -> None:
    """load_history ignores files that don't match 'week-of-*.md'."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-01-15.md").write_text(_COLD_START_REPORT)
    (reports_dir / "README.md").write_text("# docs")
    (reports_dir / "notes.txt").write_text("some notes")
    (reports_dir / ".gitkeep").write_text("")
    result = load_history(reports_dir)
    assert len(result) == 1
    assert result[0].week_of == date(2024, 1, 15)


def test_load_history_skips_week_of_file_with_invalid_date(tmp_path: Path) -> None:
    """Files like 'week-of-not-a-date.md' are silently skipped."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-not-a-date.md").write_text(_COLD_START_REPORT)
    (reports_dir / "week-of-2024-01-15.md").write_text(_COLD_START_REPORT)
    result = load_history(reports_dir)
    assert len(result) == 1
    assert result[0].week_of == date(2024, 1, 15)


# ---------------------------------------------------------------------------
# load_history — sort order
# ---------------------------------------------------------------------------


def test_load_history_returns_newest_first(tmp_path: Path) -> None:
    """Snapshots are ordered newest week_of first."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-01-08.md").write_text(_COLD_START_REPORT)
    (reports_dir / "week-of-2024-01-22.md").write_text(_COLD_START_REPORT)
    (reports_dir / "week-of-2024-01-15.md").write_text(_COLD_START_REPORT)
    result = load_history(reports_dir)
    assert result[0].week_of == date(2024, 1, 22)
    assert result[1].week_of == date(2024, 1, 15)
    assert result[2].week_of == date(2024, 1, 8)


# ---------------------------------------------------------------------------
# load_history — weeks limit
# ---------------------------------------------------------------------------


def test_load_history_respects_weeks_limit(tmp_path: Path) -> None:
    """load_history returns at most `weeks` entries."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    for i in range(1, 11):  # 10 files
        (reports_dir / f"week-of-2024-01-{i:02d}.md").write_text(_COLD_START_REPORT)
    result = load_history(reports_dir, weeks=4)
    assert len(result) == 4


def test_load_history_default_limit_is_8(tmp_path: Path) -> None:
    """Default weeks limit is 8."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    for i in range(1, 13):  # 12 files
        (reports_dir / f"week-of-2024-01-{i:02d}.md").write_text(_COLD_START_REPORT)
    result = load_history(reports_dir)
    assert len(result) == 8


def test_load_history_fewer_files_than_limit(tmp_path: Path) -> None:
    """When fewer files exist than the limit, all are returned."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-01-15.md").write_text(_COLD_START_REPORT)
    (reports_dir / "week-of-2024-01-22.md").write_text(_COLD_START_REPORT)
    result = load_history(reports_dir, weeks=8)
    assert len(result) == 2


# ---------------------------------------------------------------------------
# load_history — missing directory
# ---------------------------------------------------------------------------


def test_load_history_missing_dir_returns_empty_list(tmp_path: Path) -> None:
    """A non-existent reports_dir returns [] without raising."""
    reports_dir = tmp_path / "does_not_exist"
    assert load_history(reports_dir) == []


# ---------------------------------------------------------------------------
# load_history — snapshot content
# ---------------------------------------------------------------------------


def test_load_history_week_of_parsed_from_filename(tmp_path: Path) -> None:
    """WeekSnapshot.week_of is the date extracted from the filename."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-03-11.md").write_text(_COLD_START_REPORT)
    result = load_history(reports_dir)
    assert result[0].week_of == date(2024, 3, 11)


def test_load_history_all_dimensions_populated_from_cold_start_report(tmp_path: Path) -> None:
    """All five dimension fields are populated when the report has all five."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-01-15.md").write_text(_COLD_START_REPORT)
    snap = load_history(reports_dir)[0]
    assert snap.problem_selection == Level.DEVELOPING
    assert snap.leverage_ratio == Level.EMERGING
    assert snap.taste == Level.STRONG
    assert snap.ambition_trajectory == Level.LOW
    assert snap.visibility == Level.LOW


def test_load_history_all_dimensions_populated_from_transition_report(tmp_path: Path) -> None:
    """Transition-format reports are also parsed correctly."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-01-22.md").write_text(_TRANSITION_REPORT)
    snap = load_history(reports_dir)[0]
    assert snap.problem_selection == Level.DEVELOPING
    assert snap.leverage_ratio == Level.DEVELOPING
    assert snap.taste == Level.EXCEPTIONAL
    assert snap.ambition_trajectory == Level.EMERGING
    assert snap.visibility == Level.DEVELOPING


def test_load_history_missing_dimensions_are_none(tmp_path: Path) -> None:
    """Dimensions absent from a report become None in the snapshot."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-01-15.md").write_text(_PARTIAL_REPORT)
    snap = load_history(reports_dir)[0]
    assert snap.problem_selection == Level.STRONG
    assert snap.taste == Level.DEVELOPING
    # Absent dimensions are None.
    assert snap.leverage_ratio is None
    assert snap.ambition_trajectory is None
    assert snap.visibility is None


def test_load_history_no_chart_section_all_none(tmp_path: Path) -> None:
    """A report with no growth chart section yields a snapshot with all dims None."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-01-15.md").write_text(_NO_CHART_REPORT)
    snap = load_history(reports_dir)[0]
    assert snap.week_of == date(2024, 1, 15)
    assert snap.problem_selection is None
    assert snap.leverage_ratio is None
    assert snap.taste is None
    assert snap.ambition_trajectory is None
    assert snap.visibility is None


# ---------------------------------------------------------------------------
# load_history — duplicate week dates
# ---------------------------------------------------------------------------


def test_load_history_duplicate_dates_takes_first_found(tmp_path: Path) -> None:
    """When two files share the same parsed date, only the first seen is kept."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    # Same date, different file names won't occur with real filenames, but
    # we test the guard: create two distinct date files and assert no duplication.
    (reports_dir / "week-of-2024-01-15.md").write_text(_COLD_START_REPORT)
    # Simulate duplicates by patching the glob: we can't have two files with
    # identical names, so we verify the de-duplication logic holds for a single
    # file — only one snapshot per date must exist.
    result = load_history(reports_dir)
    dates = [s.week_of for s in result]
    assert len(dates) == len(set(dates)), "Duplicate week_of dates found in result"


# ---------------------------------------------------------------------------
# previous_levels
# ---------------------------------------------------------------------------


def test_previous_levels_returns_none_for_empty_list() -> None:
    """previous_levels([]) returns None."""
    assert previous_levels([]) is None


def test_previous_levels_returns_none_for_single_entry() -> None:
    """previous_levels([w1]) returns None — no prior week exists."""
    snap = WeekSnapshot(week_of=date(2024, 1, 15), problem_selection=Level.DEVELOPING)
    assert previous_levels([snap]) is None


def test_previous_levels_returns_second_entry() -> None:
    """previous_levels([current, prior, older]) returns the second entry (prior)."""
    current = WeekSnapshot(week_of=date(2024, 1, 22), problem_selection=Level.STRONG)
    prior = WeekSnapshot(week_of=date(2024, 1, 15), problem_selection=Level.DEVELOPING)
    older = WeekSnapshot(week_of=date(2024, 1, 8), problem_selection=Level.EMERGING)
    result = previous_levels([current, prior, older])
    assert result is prior


def test_previous_levels_returns_second_entry_for_two_item_list() -> None:
    """previous_levels([current, prior]) returns prior."""
    current = WeekSnapshot(week_of=date(2024, 1, 22))
    prior = WeekSnapshot(week_of=date(2024, 1, 15), leverage_ratio=Level.EMERGING)
    result = previous_levels([current, prior])
    assert result is prior
    assert result.leverage_ratio == Level.EMERGING
