"""Tests for F-004: Report Store.

Strict TDD — tests written before implementation.
All tests must FAIL before any implementation code is written.
"""

from datetime import date
from pathlib import Path

from builder_coach.report_store import WeeklyReport, latest_report, list_reports, save_report


# ---------------------------------------------------------------------------
# save_report — filename and path
# ---------------------------------------------------------------------------


def test_save_report_returns_path_with_monday_filename(tmp_path: Path) -> None:
    """save_report returns a Path with the week-of-YYYY-MM-DD.md pattern."""
    monday = date(2024, 1, 15)  # confirmed Monday
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    path = save_report("# Report", reports_dir, week_of=monday)
    assert path.name == "week-of-2024-01-15.md"


def test_save_report_writes_content_to_file(tmp_path: Path) -> None:
    """The content passed to save_report is exactly what ends up in the file."""
    monday = date(2024, 1, 15)
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    content = "# Weekly Report\n\nGreat week."
    path = save_report(content, reports_dir, week_of=monday)
    assert path.read_text() == content


def test_save_report_file_is_inside_reports_dir(tmp_path: Path) -> None:
    """The returned path is a child of reports_dir."""
    monday = date(2024, 1, 15)
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    path = save_report("content", reports_dir, week_of=monday)
    assert path.parent == reports_dir


# ---------------------------------------------------------------------------
# save_report — Monday adjustment
# ---------------------------------------------------------------------------


def test_save_report_wednesday_adjusts_to_monday(tmp_path: Path) -> None:
    """week_of on a Wednesday is adjusted back to that week's Monday."""
    wednesday = date(2024, 1, 17)  # Wednesday
    expected_monday = date(2024, 1, 15)
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    path = save_report("content", reports_dir, week_of=wednesday)
    assert path.name == f"week-of-{expected_monday}.md"


def test_save_report_sunday_adjusts_to_monday(tmp_path: Path) -> None:
    """week_of on a Sunday is adjusted back to that week's Monday."""
    sunday = date(2024, 1, 21)  # Sunday
    expected_monday = date(2024, 1, 15)
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    path = save_report("content", reports_dir, week_of=sunday)
    assert path.name == f"week-of-{expected_monday}.md"


def test_save_report_monday_input_unchanged(tmp_path: Path) -> None:
    """A Monday week_of is not altered."""
    monday = date(2024, 1, 15)  # already Monday
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    path = save_report("content", reports_dir, week_of=monday)
    assert path.name == "week-of-2024-01-15.md"


# ---------------------------------------------------------------------------
# save_report — directory creation
# ---------------------------------------------------------------------------


def test_save_report_creates_directory_if_missing(tmp_path: Path) -> None:
    """save_report creates reports_dir when it doesn't exist yet."""
    reports_dir = tmp_path / "new_reports"
    assert not reports_dir.exists()
    save_report("content", reports_dir, week_of=date(2024, 1, 15))
    assert reports_dir.is_dir()


def test_save_report_works_with_existing_directory(tmp_path: Path) -> None:
    """save_report doesn't fail when the directory already exists."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    # Should not raise
    path = save_report("content", reports_dir, week_of=date(2024, 1, 15))
    assert path.exists()


# ---------------------------------------------------------------------------
# save_report — overwrite
# ---------------------------------------------------------------------------


def test_save_report_overwrites_existing_file(tmp_path: Path) -> None:
    """Calling save_report twice for the same week replaces the file content."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    monday = date(2024, 1, 15)
    save_report("original content", reports_dir, week_of=monday)
    path = save_report("updated content", reports_dir, week_of=monday)
    assert path.read_text() == "updated content"


def test_save_report_only_one_file_after_overwrite(tmp_path: Path) -> None:
    """After two saves for the same week, only one file exists."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    monday = date(2024, 1, 15)
    save_report("first", reports_dir, week_of=monday)
    save_report("second", reports_dir, week_of=monday)
    files = list(reports_dir.glob("week-of-*.md"))
    assert len(files) == 1


# ---------------------------------------------------------------------------
# save_report — edge case: empty content
# ---------------------------------------------------------------------------


def test_save_report_empty_content_creates_file(tmp_path: Path) -> None:
    """Empty string content is saved without error."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    path = save_report("", reports_dir, week_of=date(2024, 1, 15))
    assert path.exists()
    assert path.read_text() == ""


# ---------------------------------------------------------------------------
# save_report — default week_of (current week's Monday)
# ---------------------------------------------------------------------------


def test_save_report_defaults_to_current_week_monday(tmp_path: Path) -> None:
    """Omitting week_of saves to the Monday of the current week."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    path = save_report("content", reports_dir)
    today = date.today()
    expected_monday = today - __import__("datetime").timedelta(days=today.weekday())
    assert path.name == f"week-of-{expected_monday}.md"


# ---------------------------------------------------------------------------
# list_reports — basic behaviour
# ---------------------------------------------------------------------------


def test_list_reports_returns_all_weekly_reports(tmp_path: Path) -> None:
    """list_reports returns one WeeklyReport per week-of-*.md file."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-01-08.md").write_text("week 1")
    (reports_dir / "week-of-2024-01-15.md").write_text("week 2")
    (reports_dir / "week-of-2024-01-22.md").write_text("week 3")
    results = list_reports(reports_dir)
    assert len(results) == 3


def test_list_reports_sorted_newest_first(tmp_path: Path) -> None:
    """list_reports returns reports ordered newest week_of first."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-01-08.md").write_text("old")
    (reports_dir / "week-of-2024-01-22.md").write_text("newer")
    (reports_dir / "week-of-2024-01-15.md").write_text("middle")
    results = list_reports(reports_dir)
    assert results[0].week_of == date(2024, 1, 22)
    assert results[1].week_of == date(2024, 1, 15)
    assert results[2].week_of == date(2024, 1, 8)


def test_list_reports_populates_week_of(tmp_path: Path) -> None:
    """WeeklyReport.week_of is parsed from the filename."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-03-11.md").write_text("content")
    results = list_reports(reports_dir)
    assert results[0].week_of == date(2024, 3, 11)


def test_list_reports_populates_path(tmp_path: Path) -> None:
    """WeeklyReport.path is the full path to the file."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    expected = reports_dir / "week-of-2024-03-11.md"
    expected.write_text("content")
    results = list_reports(reports_dir)
    assert results[0].path == expected


def test_list_reports_populates_content(tmp_path: Path) -> None:
    """WeeklyReport.content matches the file's text."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-03-11.md").write_text("# Report\n\nBody here.")
    results = list_reports(reports_dir)
    assert results[0].content == "# Report\n\nBody here."


# ---------------------------------------------------------------------------
# list_reports — filtering non-matching files
# ---------------------------------------------------------------------------


def test_list_reports_ignores_gitkeep(tmp_path: Path) -> None:
    """.gitkeep and other non-matching files are excluded from results."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / ".gitkeep").write_text("")
    (reports_dir / "README.md").write_text("not a report")
    (reports_dir / "week-of-2024-01-15.md").write_text("real report")
    results = list_reports(reports_dir)
    assert len(results) == 1
    assert results[0].week_of == date(2024, 1, 15)


def test_list_reports_skips_unparseable_date_in_filename(tmp_path: Path) -> None:
    """A file named week-of-not-a-date.md is silently skipped."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-not-a-date.md").write_text("bad name")
    (reports_dir / "week-of-2024-01-15.md").write_text("good report")
    results = list_reports(reports_dir)
    assert len(results) == 1
    assert results[0].week_of == date(2024, 1, 15)


# ---------------------------------------------------------------------------
# list_reports — missing / empty directory
# ---------------------------------------------------------------------------


def test_list_reports_empty_directory_returns_empty_list(tmp_path: Path) -> None:
    """An existing but empty reports directory returns []."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    assert list_reports(reports_dir) == []


def test_list_reports_missing_directory_returns_empty_list(tmp_path: Path) -> None:
    """A non-existent reports_dir returns [] without raising."""
    reports_dir = tmp_path / "does_not_exist"
    assert list_reports(reports_dir) == []


# ---------------------------------------------------------------------------
# latest_report
# ---------------------------------------------------------------------------


def test_latest_report_returns_most_recent(tmp_path: Path) -> None:
    """latest_report returns the report with the newest week_of date."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-01-08.md").write_text("older")
    (reports_dir / "week-of-2024-01-22.md").write_text("newer")
    (reports_dir / "week-of-2024-01-15.md").write_text("middle")
    result = latest_report(reports_dir)
    assert result is not None
    assert result.week_of == date(2024, 1, 22)


def test_latest_report_returns_none_for_empty_directory(tmp_path: Path) -> None:
    """latest_report returns None when the directory exists but has no reports."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    assert latest_report(reports_dir) is None


def test_latest_report_returns_none_for_missing_directory(tmp_path: Path) -> None:
    """latest_report returns None when reports_dir doesn't exist."""
    reports_dir = tmp_path / "does_not_exist"
    assert latest_report(reports_dir) is None


def test_latest_report_content_matches_file(tmp_path: Path) -> None:
    """latest_report.content is the actual file content."""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "week-of-2024-01-15.md").write_text("# Best week ever")
    result = latest_report(reports_dir)
    assert result is not None
    assert result.content == "# Best week ever"


# ---------------------------------------------------------------------------
# WeeklyReport dataclass
# ---------------------------------------------------------------------------


def test_weekly_report_is_dataclass() -> None:
    """WeeklyReport can be instantiated with week_of, path, content fields."""
    r = WeeklyReport(
        week_of=date(2024, 1, 15),
        path=Path("/tmp/week-of-2024-01-15.md"),
        content="# Report",
    )
    assert r.week_of == date(2024, 1, 15)
    assert r.path == Path("/tmp/week-of-2024-01-15.md")
    assert r.content == "# Report"
