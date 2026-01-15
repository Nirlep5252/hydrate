"""State management for hydration reminders."""

import json
import os
from pathlib import Path
from typing import Optional

STATE_DIR = Path.home() / ".hydrate"
STATE_FILE = STATE_DIR / "state.json"


def write_state(
    start_time: float,
    interval_seconds: int,
    reminder_count: int,
    pid: Optional[int] = None,
) -> None:
    """
    Write current hydration state to file.

    Args:
        start_time: Unix timestamp when current interval started
        interval_seconds: Total seconds in the interval
        reminder_count: Number of reminders sent
        pid: Process ID of the running hydrate instance
    """
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    state = {
        "start_time": start_time,
        "interval_seconds": interval_seconds,
        "reminder_count": reminder_count,
        "pid": pid or os.getpid(),
    }

    STATE_FILE.write_text(json.dumps(state))


def read_state() -> Optional[dict]:
    """
    Read hydration state from file.

    Returns:
        State dictionary if valid and process is running, None otherwise
    """
    if not STATE_FILE.exists():
        return None

    try:
        state = json.loads(STATE_FILE.read_text())

        # Check if process is still running
        pid = state.get("pid")
        if pid and not _is_process_running(pid):
            clear_state()
            return None

        return state
    except (json.JSONDecodeError, KeyError):
        return None


def clear_state() -> None:
    """Remove state file."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def is_running() -> tuple[bool, Optional[int]]:
    """
    Check if hydrate daemon is running.

    Returns:
        Tuple of (is_running, pid). pid is None if not running.
    """
    state = read_state()
    if state is None:
        return False, None

    pid = state.get("pid")
    if pid and _is_process_running(pid):
        return True, pid

    return False, None


def _is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False
