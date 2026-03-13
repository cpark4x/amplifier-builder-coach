"""Tests for F-002: Journal Entry Parser.

Strict TDD — tests written before implementation.
All tests must FAIL before any implementation code is written.
"""

import pytest
from datetime import date
from pathlib import Path

from builder_coach.journal_parser import JournalEntry, filter_entries, parse_journal


# ---------------------------------------------------------------------------
# parse_journal — error handling
# ---------------------------------------------------------------------------


def test_parse_journal_raises_file_not_found(tmp_path: Path) -> None:
    """Missing file must raise FileNotFoundError, not return empty list."""
    missing = tmp_path / "no_such_file.md"
    with pytest.raises(FileNotFoundError):
        parse_journal(missing)


# ---------------------------------------------------------------------------
# parse_journal — date header parsing
# ---------------------------------------------------------------------------


def test_parse_journal_no_date_headers_returns_empty(tmp_path: Path) -> None:
    """File with preamble but no YYYY-MM-DD headers yields no entries."""
    journal = tmp_path / "journal.md"
    journal.write_text("# Growth Journal\n\nInstructions here. No dates.\n")
    assert parse_journal(journal) == []


def test_parse_journal_single_entry(tmp_path: Path) -> None:
    """Single date header produces one entry with correct date."""
    journal = tmp_path / "journal.md"
    journal.write_text("## 2024-01-15\n\nDid some work today.\n")
    entries = parse_journal(journal)
    assert len(entries) == 1
    assert entries[0].date == date(2024, 1, 15)


def test_parse_journal_text_belongs_to_earlier_date(tmp_path: Path) -> None:
    """Text between two headers belongs to the earlier (upper) header."""
    journal = tmp_path / "journal.md"
    journal.write_text("## 2024-01-15\nFirst entry text.\n## 2024-01-16\nSecond entry text.\n")
    entries = parse_journal(journal)
    assert len(entries) == 2
    jan15 = next(e for e in entries if e.date == date(2024, 1, 15))
    jan16 = next(e for e in entries if e.date == date(2024, 1, 16))
    assert "First entry text" in jan15.raw_text
    assert "Second entry text" in jan16.raw_text


def test_parse_journal_preamble_ignored(tmp_path: Path) -> None:
    """Content before the first date header is not included in any entry."""
    journal = tmp_path / "journal.md"
    journal.write_text("# Title\n\nInstructions here.\n\n---\n\n## 2024-01-15\n\nActual entry.\n")
    entries = parse_journal(journal)
    assert len(entries) == 1
    assert "Instructions" not in entries[0].raw_text
    assert "Actual entry" in entries[0].raw_text


def test_parse_journal_sorted_newest_first(tmp_path: Path) -> None:
    """Returned list is ordered newest date first."""
    journal = tmp_path / "journal.md"
    journal.write_text("## 2024-01-10\nOldest\n## 2024-01-15\nNewest\n## 2024-01-12\nMiddle\n")
    entries = parse_journal(journal)
    assert [e.date for e in entries] == [
        date(2024, 1, 15),
        date(2024, 1, 12),
        date(2024, 1, 10),
    ]


def test_parse_journal_malformed_date_header_skipped(tmp_path: Path) -> None:
    """'## March 11' style headers are ignored without raising an error."""
    journal = tmp_path / "journal.md"
    journal.write_text("## March 11\nNot a real entry.\n## 2024-01-15\nReal entry.\n")
    entries = parse_journal(journal)
    assert len(entries) == 1
    assert entries[0].date == date(2024, 1, 15)


def test_parse_journal_empty_content_entry_included(tmp_path: Path) -> None:
    """A date header with no text below it is included with empty raw_text."""
    journal = tmp_path / "journal.md"
    journal.write_text("## 2024-01-15\n## 2024-01-16\nContent here.\n")
    entries = parse_journal(journal)
    assert len(entries) == 2
    jan15 = next(e for e in entries if e.date == date(2024, 1, 15))
    assert jan15.raw_text == ""


def test_parse_journal_same_date_merges_text(tmp_path: Path) -> None:
    """Duplicate date headers produce a single merged entry."""
    journal = tmp_path / "journal.md"
    journal.write_text("## 2024-01-15\nFirst part.\n## 2024-01-15\nSecond part.\n")
    entries = parse_journal(journal)
    assert len(entries) == 1
    assert "First part" in entries[0].raw_text
    assert "Second part" in entries[0].raw_text


# ---------------------------------------------------------------------------
# parse_journal — hashtag extraction
# ---------------------------------------------------------------------------


def test_parse_journal_extracts_hashtags(tmp_path: Path) -> None:
    """#hashtags in entry text are collected into the tags field."""
    journal = tmp_path / "journal.md"
    journal.write_text("## 2024-01-15\nWorked on #visibility and #impact today.\n")
    entries = parse_journal(journal)
    assert "#visibility" in entries[0].tags
    assert "#impact" in entries[0].tags


def test_parse_journal_no_hashtags_yields_empty_tags(tmp_path: Path) -> None:
    """Entries without hashtags have an empty tags list."""
    journal = tmp_path / "journal.md"
    journal.write_text("## 2024-01-15\nNo hashtags here.\n")
    entries = parse_journal(journal)
    assert entries[0].tags == []


def test_parse_journal_hashtag_not_duplicated(tmp_path: Path) -> None:
    """The same hashtag appearing twice is stored only once."""
    journal = tmp_path / "journal.md"
    journal.write_text("## 2024-01-15\nMentioned #visibility twice. #visibility again.\n")
    entries = parse_journal(journal)
    assert entries[0].tags.count("#visibility") == 1


# ---------------------------------------------------------------------------
# parse_journal — placeholder exclusion
# ---------------------------------------------------------------------------


def test_parse_journal_excludes_italic_placeholder(tmp_path: Path) -> None:
    """Entry whose text is only _italic underscores_ is excluded."""
    journal = tmp_path / "journal.md"
    journal.write_text(
        "## 2024-01-15\n\n_Start logging here. Replace this with your first entry._\n"
    )
    entries = parse_journal(journal)
    assert len(entries) == 0


def test_parse_journal_real_entry_not_excluded(tmp_path: Path) -> None:
    """Entry with real text alongside italic is not excluded."""
    journal = tmp_path / "journal.md"
    journal.write_text("## 2024-01-15\n\nDid real work today. _Some italic note._\n")
    entries = parse_journal(journal)
    assert len(entries) == 1


def test_parse_journal_placeholder_mixed_with_real(tmp_path: Path) -> None:
    """Placeholder date excluded; adjacent real entry kept."""
    journal = tmp_path / "journal.md"
    journal.write_text("## 2024-01-14\n_placeholder_\n## 2024-01-15\nReal work done today.\n")
    entries = parse_journal(journal)
    assert len(entries) == 1
    assert entries[0].date == date(2024, 1, 15)


# ---------------------------------------------------------------------------
# filter_entries
# ---------------------------------------------------------------------------


def test_filter_entries_returns_entries_in_range() -> None:
    """Only entries within [since, until] are returned."""
    entries = [
        JournalEntry(date=date(2024, 1, 10), raw_text="Too old"),
        JournalEntry(date=date(2024, 1, 15), raw_text="In range"),
        JournalEntry(date=date(2024, 1, 20), raw_text="Too new"),
    ]
    result = filter_entries(entries, since=date(2024, 1, 12), until=date(2024, 1, 18))
    assert len(result) == 1
    assert result[0].date == date(2024, 1, 15)


def test_filter_entries_inclusive_on_both_ends() -> None:
    """since and until dates themselves are included."""
    entries = [
        JournalEntry(date=date(2024, 1, 10), raw_text="At since"),
        JournalEntry(date=date(2024, 1, 15), raw_text="Middle"),
        JournalEntry(date=date(2024, 1, 20), raw_text="At until"),
    ]
    result = filter_entries(entries, since=date(2024, 1, 10), until=date(2024, 1, 20))
    assert len(result) == 3


def test_filter_entries_since_after_until_returns_empty() -> None:
    """Inverted range returns empty list without raising."""
    entries = [JournalEntry(date=date(2024, 1, 15), raw_text="Entry")]
    result = filter_entries(entries, since=date(2024, 1, 20), until=date(2024, 1, 10))
    assert result == []


def test_filter_entries_sorted_newest_first() -> None:
    """filter_entries result is ordered newest date first."""
    entries = [
        JournalEntry(date=date(2024, 1, 10), raw_text="Older"),
        JournalEntry(date=date(2024, 1, 15), raw_text="Newer"),
    ]
    result = filter_entries(entries, since=date(2024, 1, 1), until=date(2024, 1, 31))
    assert result[0].date == date(2024, 1, 15)
    assert result[1].date == date(2024, 1, 10)


def test_filter_entries_default_until_includes_today() -> None:
    """Omitting until defaults to today, so today's entry is included."""
    today = date.today()
    entries = [
        JournalEntry(date=today, raw_text="Today"),
        JournalEntry(date=date(2020, 1, 1), raw_text="Way old"),
    ]
    result = filter_entries(entries, since=date(2023, 1, 1))
    assert any(e.date == today for e in result)
    assert all(e.date >= date(2023, 1, 1) for e in result)


def test_filter_entries_empty_input_returns_empty() -> None:
    """Empty entries list always returns empty list."""
    result = filter_entries([], since=date(2024, 1, 1), until=date(2024, 1, 31))
    assert result == []
