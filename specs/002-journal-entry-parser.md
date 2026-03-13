# Feature 002: Journal Entry Parser

## Summary

Parse the growth journal markdown file into structured entries. The journal is
free-form markdown with date headers — this module extracts entries by date so
the coaching pipeline can filter to a specific time range and classify entries
by type.

## Module

`src/builder_coach/journal_parser.py`

## Interfaces

```python
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class JournalEntry:
    """A single day's journal entries."""
    date: date
    raw_text: str                          # full text under the date header
    tags: list[str] = field(default_factory=list)  # extracted from #hashtags if present


def parse_journal(path: Path) -> list[JournalEntry]:
    """Parse a growth journal markdown file into entries.

    Entries are delimited by ## headers matching date patterns
    (YYYY-MM-DD). Everything between two date headers belongs
    to the earlier date.

    Args:
        path: Path to the growth journal markdown file.

    Returns:
        List of JournalEntry sorted by date, newest first.

    Raises:
        FileNotFoundError: If path doesn't exist.
    """


def filter_entries(
    entries: list[JournalEntry],
    since: date,
    until: date | None = None,
) -> list[JournalEntry]:
    """Filter entries to a date range (inclusive on both ends).

    Args:
        entries: Parsed journal entries.
        since: Start date (inclusive).
        until: End date (inclusive). Defaults to today.

    Returns:
        Filtered list, newest first.
    """
```

## Acceptance Criteria

1. Parses `## YYYY-MM-DD` headers as date boundaries
2. Text between two date headers belongs to the earlier date
3. Preamble text before the first date header is ignored (it's instructions)
4. Extracts `#hashtag` patterns from entry text into the `tags` field
5. `filter_entries` returns only entries within the date range (inclusive)
6. Results sorted newest-first in both functions
7. Placeholder entries (containing only `_italic underscores_`) are excluded

## Edge Cases

- File doesn't exist → raise FileNotFoundError
- File exists but has no date headers → return empty list
- Date header with no content below it → include with empty raw_text
- Malformed date header (e.g., `## March 11`) → skip, don't error
- Multiple entries on the same date → should not happen (one header per date), but if it does, merge text
- `since` is after `until` → return empty list

## Test File

`tests/test_journal_parser.py`

## Dependencies

- Standard library only (pathlib, datetime, dataclasses, re)

## Not In Scope

- Writing or appending journal entries (separate feature)
- Classifying entries by dimension (Visibility, Impact, etc.) — that's the coaching agent's job
- Parsing anything other than the growth journal format