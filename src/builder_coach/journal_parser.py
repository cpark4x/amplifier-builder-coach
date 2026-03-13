"""F-002: Journal Entry Parser.

Parse a growth journal markdown file (## YYYY-MM-DD date headers) into
structured JournalEntry objects. Standard library only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

# Matches exactly: ## 2024-01-15 (with optional trailing whitespace)
_DATE_HEADER_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$")

# Matches #hashtag tokens
_HASHTAG_RE = re.compile(r"#(\w+)")


@dataclass
class JournalEntry:
    """A single day's journal entries."""

    date: date
    raw_text: str  # full text under the date header
    tags: list[str] = field(default_factory=list)  # extracted #hashtags


def _is_placeholder(text: str) -> bool:
    """Return True if text consists entirely of _italic_ markdown spans.

    A placeholder entry is one where the author has not written real content —
    the text is made up only of _italic underscored_ blocks (e.g. the default
    growth-journal prompt line).
    """
    stripped = text.strip()
    if not stripped:
        return False
    return bool(re.fullmatch(r"(_[^_]+_\s*)+", stripped))


def _extract_tags(text: str) -> list[str]:
    """Extract unique #hashtags from text, preserving the leading # prefix."""
    seen: set[str] = set()
    tags: list[str] = []
    for match in _HASHTAG_RE.finditer(text):
        tag = f"#{match.group(1)}"
        if tag not in seen:
            seen.add(tag)
            tags.append(tag)
    return tags


def parse_journal(path: Path) -> list[JournalEntry]:
    """Parse a growth journal markdown file into entries.

    Entries are delimited by ## headers matching the YYYY-MM-DD date pattern.
    Everything between two date headers belongs to the earlier (upper) date.
    Preamble text before the first date header is ignored.
    Placeholder entries (only _italic_ text) are excluded.

    Args:
        path: Path to the growth journal markdown file.

    Returns:
        List of JournalEntry sorted by date, newest first.

    Raises:
        FileNotFoundError: If path doesn't exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Journal file not found: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()

    # sections: date → accumulated body lines
    # section_order: preserves first-seen ordering (for duplicate-date merging)
    sections: dict[date, list[str]] = {}
    section_order: list[date] = []
    current_date: date | None = None

    for line in lines:
        m = _DATE_HEADER_RE.match(line)
        if m:
            try:
                entry_date = date.fromisoformat(m.group(1))
            except ValueError:
                # Malformed date string despite matching the regex — skip it
                current_date = None
                continue
            current_date = entry_date
            if entry_date not in sections:
                sections[entry_date] = []
                section_order.append(entry_date)
            # Duplicate date: current_date already in sections → lines will
            # be appended to the existing bucket (merge behaviour).
        elif current_date is not None:
            # Body line belonging to the current date section
            sections[current_date].append(line)
        # else: preamble line before any date header — discard

    entries: list[JournalEntry] = []
    for entry_date in section_order:
        raw_text = "\n".join(sections[entry_date]).strip()
        if _is_placeholder(raw_text):
            continue
        tags = _extract_tags(raw_text)
        entries.append(JournalEntry(date=entry_date, raw_text=raw_text, tags=tags))

    entries.sort(key=lambda e: e.date, reverse=True)
    return entries


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
    if until is None:
        until = date.today()

    if since > until:
        return []

    result = [e for e in entries if since <= e.date <= until]
    result.sort(key=lambda e: e.date, reverse=True)
    return result
