# Feature 001: Session File Discovery

## Summary

Find Amplifier session files from the past N days across standard session directories.
This is the entry point for the weekly retrospective pipeline — before you can analyze
sessions, you need to find them.

## Module

`src/builder_coach/session_discovery.py`

## Interfaces

```python
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class SessionFile:
    """A discovered Amplifier session file."""
    path: Path
    session_id: str          # derived from directory name
    modified: datetime        # last modification time
    size_bytes: int


def discover_sessions(
    search_paths: list[Path] | None = None,
    days: int = 7,
) -> list[SessionFile]:
    """Find session files modified within the last `days` days.

    Args:
        search_paths: Directories to search. Defaults to
            [~/.amplifier/sessions/, .amplifier/sessions/].
        days: How many days back to look. Default 7.

    Returns:
        List of SessionFile, sorted newest-first.
    """
```

## Acceptance Criteria

1. Returns only directories containing an `events.jsonl` file
2. Filters to sessions modified within the last `days` days (based on events.jsonl mtime)
3. Default search paths are `~/.amplifier/sessions/` and `.amplifier/sessions/`
4. Custom search paths override defaults entirely
5. Returns results sorted by modification time, newest first
6. Session ID is the directory name (e.g., `abc123-def456`)

## Edge Cases

- Search path doesn't exist → skip silently, don't error
- Search path exists but is empty → return empty list
- events.jsonl exists but is 0 bytes → include it (empty session is still a session)
- Duplicate session IDs across search paths → deduplicate, prefer the newer one
- Permission error on a directory → skip with warning, don't crash
- `days=0` → sessions modified today only

## Test File

`tests/test_session_discovery.py`

## Dependencies

- Standard library only (pathlib, datetime, dataclasses)
- No external packages

## Not In Scope

- Parsing events.jsonl content (that's a separate feature)
- Filtering by project or bundle (future feature)
- Watching for new sessions in real-time