"""Session File Discovery — F-001.

Find Amplifier session files from the past N days across standard session
directories. This is the entry point for the weekly retrospective pipeline.
"""

import sys
from dataclasses import dataclass
from datetime import datetime, time as time_type, timedelta
from pathlib import Path


@dataclass
class SessionFile:
    """A discovered Amplifier session file."""

    path: Path
    session_id: str  # derived from directory name
    modified: datetime  # last modification time of events.jsonl
    size_bytes: int


def _home_path() -> Path:
    """Return the current user's home directory. Isolated for testability."""
    return Path.home()


def discover_sessions(
    search_paths: list[Path] | None = None,
    days: int = 7,
) -> list[SessionFile]:
    """Find session files modified within the last ``days`` days.

    Args:
        search_paths: Directories to search. Defaults to
            [~/.amplifier/sessions/, .amplifier/sessions/].
            Custom paths override the defaults entirely.
        days: How many days back to look. Default 7.
            days=0 means sessions modified today only.

    Returns:
        List of SessionFile sorted newest-first.
        Duplicate session IDs across paths are deduplicated; the newer entry wins.
    """
    if search_paths is None:
        search_paths = [
            _home_path() / ".amplifier" / "sessions",
            Path(".amplifier") / "sessions",
        ]

    # Cutoff: start-of-day N days ago.
    # days=0 → midnight today  |  days=7 → midnight seven days ago
    cutoff = datetime.combine(
        (datetime.now() - timedelta(days=days)).date(),
        time_type.min,
    )

    # Keyed by session_id for deduplication (prefer newer).
    seen: dict[str, SessionFile] = {}

    for search_path in search_paths:
        if not search_path.exists():
            continue

        try:
            entries = list(search_path.iterdir())
        except PermissionError as exc:
            print(f"Warning: cannot read directory {search_path}: {exc}", file=sys.stderr)
            continue

        for entry in entries:
            if not entry.is_dir():
                continue

            events_file = entry / "events.jsonl"
            if not events_file.exists():
                continue

            try:
                stat = events_file.stat()
            except PermissionError:
                continue

            mtime = datetime.fromtimestamp(stat.st_mtime)
            if mtime < cutoff:
                continue

            session_id = entry.name
            sf = SessionFile(
                path=events_file,
                session_id=session_id,
                modified=mtime,
                size_bytes=stat.st_size,
            )

            # Deduplicate: keep the newer entry when the same session_id appears
            # in multiple search paths.
            if session_id not in seen or sf.modified > seen[session_id].modified:
                seen[session_id] = sf

    return sorted(seen.values(), key=lambda s: s.modified, reverse=True)
