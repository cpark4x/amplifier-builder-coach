"""Tests for session_discovery module — F-001.

Tests are written test-first: all tests exist before any implementation.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

from builder_coach.session_discovery import SessionFile, discover_sessions

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

NOW = datetime.now()
YESTERDAY = NOW - timedelta(days=1)
EIGHT_DAYS_AGO = NOW - timedelta(days=8)


def make_session(base: Path, session_id: str, mtime: datetime, size: int = 100) -> Path:
    """Create a session directory with an events.jsonl file at the given mtime.

    Returns the path to events.jsonl.
    """
    session_dir = base / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    events_file = session_dir / "events.jsonl"
    events_file.write_bytes(b"x" * size)
    ts = mtime.timestamp()
    os.utime(events_file, (ts, ts))
    return events_file


# ---------------------------------------------------------------------------
# AC1 — Returns only directories containing an events.jsonl file
# ---------------------------------------------------------------------------


def test_returns_only_sessions_with_events_jsonl(tmp_path):
    make_session(tmp_path, "valid-session", NOW)
    (tmp_path / "no-events-dir").mkdir()  # directory without events.jsonl
    (tmp_path / "not-a-dir.jsonl").write_text("")  # file at top level, not a dir

    results = discover_sessions(search_paths=[tmp_path])

    assert len(results) == 1
    assert results[0].session_id == "valid-session"


# ---------------------------------------------------------------------------
# AC2 — Filters by days based on events.jsonl mtime
# ---------------------------------------------------------------------------


def test_filters_by_days(tmp_path):
    make_session(tmp_path, "recent", NOW)
    make_session(tmp_path, "old", EIGHT_DAYS_AGO)

    results = discover_sessions(search_paths=[tmp_path], days=7)

    session_ids = {r.session_id for r in results}
    assert "recent" in session_ids
    assert "old" not in session_ids


# ---------------------------------------------------------------------------
# AC3 — Default search paths
# ---------------------------------------------------------------------------


def test_default_search_paths(monkeypatch, tmp_path):
    home_sessions = tmp_path / "home" / ".amplifier" / "sessions"
    local_sessions = tmp_path / "local" / ".amplifier" / "sessions"
    home_sessions.mkdir(parents=True)
    local_sessions.mkdir(parents=True)

    make_session(home_sessions, "home-session", NOW)
    make_session(local_sessions, "local-session", NOW)

    monkeypatch.setattr(
        "builder_coach.session_discovery._home_path",
        lambda: tmp_path / "home",
    )
    monkeypatch.chdir(tmp_path / "local")

    results = discover_sessions()

    session_ids = {r.session_id for r in results}
    assert "home-session" in session_ids
    assert "local-session" in session_ids


# ---------------------------------------------------------------------------
# AC4 — Custom search paths override defaults entirely
# ---------------------------------------------------------------------------


def test_custom_paths_override_defaults(monkeypatch, tmp_path):
    home_sessions = tmp_path / "home" / ".amplifier" / "sessions"
    home_sessions.mkdir(parents=True)
    make_session(home_sessions, "home-session", NOW)

    custom_path = tmp_path / "custom"
    custom_path.mkdir()
    make_session(custom_path, "custom-session", NOW)

    monkeypatch.setattr(
        "builder_coach.session_discovery._home_path",
        lambda: tmp_path / "home",
    )

    results = discover_sessions(search_paths=[custom_path])

    session_ids = {r.session_id for r in results}
    assert "custom-session" in session_ids
    assert "home-session" not in session_ids


# ---------------------------------------------------------------------------
# AC5 — Results sorted newest-first
# ---------------------------------------------------------------------------


def test_sorted_newest_first(tmp_path):
    three_days_ago = NOW - timedelta(days=3)
    two_days_ago = NOW - timedelta(days=2)

    make_session(tmp_path, "session-a", three_days_ago)
    make_session(tmp_path, "session-b", NOW)
    make_session(tmp_path, "session-c", two_days_ago)

    results = discover_sessions(search_paths=[tmp_path], days=7)

    assert results[0].session_id == "session-b"
    assert results[1].session_id == "session-c"
    assert results[2].session_id == "session-a"


# ---------------------------------------------------------------------------
# AC6 — Session ID is the directory name
# ---------------------------------------------------------------------------


def test_session_id_is_directory_name(tmp_path):
    make_session(tmp_path, "abc123-def456", NOW)

    results = discover_sessions(search_paths=[tmp_path])

    assert results[0].session_id == "abc123-def456"


# ---------------------------------------------------------------------------
# Edge: Search path doesn't exist → skip silently
# ---------------------------------------------------------------------------


def test_missing_search_path_skipped_silently(tmp_path):
    missing = tmp_path / "does-not-exist"

    results = discover_sessions(search_paths=[missing])

    assert results == []


# ---------------------------------------------------------------------------
# Edge: Search path exists but is empty → return empty list
# ---------------------------------------------------------------------------


def test_empty_search_path_returns_empty(tmp_path):
    results = discover_sessions(search_paths=[tmp_path])

    assert results == []


# ---------------------------------------------------------------------------
# Edge: events.jsonl is 0 bytes → include it
# ---------------------------------------------------------------------------


def test_zero_byte_events_file_included(tmp_path):
    make_session(tmp_path, "empty-session", NOW, size=0)

    results = discover_sessions(search_paths=[tmp_path])

    assert len(results) == 1
    assert results[0].session_id == "empty-session"
    assert results[0].size_bytes == 0


# ---------------------------------------------------------------------------
# Edge: Duplicate session IDs across paths → deduplicate, prefer newer
# ---------------------------------------------------------------------------


def test_duplicate_session_ids_prefer_newer(tmp_path):
    path1 = tmp_path / "path1"
    path2 = tmp_path / "path2"
    path1.mkdir()
    path2.mkdir()

    make_session(path1, "session-xyz", YESTERDAY)
    make_session(path2, "session-xyz", NOW)

    results = discover_sessions(search_paths=[path1, path2], days=7)

    assert len(results) == 1
    # The kept entry must be the newer one (from path2)
    assert results[0].modified >= NOW - timedelta(seconds=5)


# ---------------------------------------------------------------------------
# Edge: Permission error on a directory → skip with warning
# ---------------------------------------------------------------------------


def test_permission_error_skips_with_warning(tmp_path, capsys):
    restricted = tmp_path / "restricted"
    restricted.mkdir()
    make_session(restricted, "hidden-session", NOW)

    os.chmod(restricted, 0o000)
    try:
        discover_sessions(search_paths=[restricted])
        captured = capsys.readouterr()
        # Must not crash, must emit some warning text
        warning_output = captured.err + captured.out
        assert "warning" in warning_output.lower()
    finally:
        os.chmod(restricted, 0o755)  # restore for cleanup


# ---------------------------------------------------------------------------
# Edge: days=0 → sessions modified today only
# ---------------------------------------------------------------------------


def test_days_zero_returns_today_only(tmp_path):
    today_start = datetime.combine(datetime.now().date(), datetime.min.time())
    just_before_today = today_start - timedelta(seconds=1)

    make_session(tmp_path, "today-session", NOW)
    make_session(tmp_path, "yesterday-session", just_before_today)

    results = discover_sessions(search_paths=[tmp_path], days=0)

    session_ids = {r.session_id for r in results}
    assert "today-session" in session_ids
    assert "yesterday-session" not in session_ids


# ---------------------------------------------------------------------------
# Data structure contract — SessionFile fields
# ---------------------------------------------------------------------------


def test_session_file_has_correct_fields(tmp_path):
    events_file = make_session(tmp_path, "test-session", NOW, size=42)

    results = discover_sessions(search_paths=[tmp_path])

    assert len(results) == 1
    sf = results[0]
    assert isinstance(sf, SessionFile)
    assert isinstance(sf.path, Path)
    assert sf.path == events_file
    assert sf.session_id == "test-session"
    assert isinstance(sf.modified, datetime)
    assert sf.size_bytes == 42
