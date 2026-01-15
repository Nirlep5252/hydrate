"""State management for hydration reminders."""

import fcntl
import json
import os
from pathlib import Path
from typing import Optional

STATE_DIR = Path.home() / ".hydrate"
STATE_FILE = STATE_DIR / "state.json"
LOCK_FILE = STATE_DIR / "state.lock"


def is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def _acquire_lock():
    """Acquire exclusive lock on state file."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    lock_fd = open(LOCK_FILE, "w")
    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    return lock_fd


def _release_lock(lock_fd):
    """Release lock on state file."""
    fcntl.flock(lock_fd, fcntl.LOCK_UN)
    lock_fd.close()


def write_state(
    start_time: float,
    interval_seconds: int,
    reminder_count: int,
    pid: Optional[int] = None,
) -> None:
    """
    Write current hydration state to file with file locking.

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

    lock_fd = _acquire_lock()
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    finally:
        _release_lock(lock_fd)


def read_state() -> Optional[dict]:
    """
    Read hydration state from file.

    Returns:
        State dictionary if valid and process is running, None otherwise
    """
    if not STATE_FILE.exists():
        return None

    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)

        # Check if process is still running
        pid = state.get("pid")
        if pid and not is_process_running(pid):
            clear_state()
            return None

        return state
    except (json.JSONDecodeError, KeyError, IOError):
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
    if pid and is_process_running(pid):
        return True, pid

    return False, None


def acquire_lock_and_check() -> tuple[bool, Optional[int], any]:
    """
    Atomically acquire lock and check if already running.

    Returns:
        Tuple of (is_running, pid, lock_fd). Caller must release lock.
    """
    lock_fd = _acquire_lock()

    if not STATE_FILE.exists():
        return False, None, lock_fd

    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)

        pid = state.get("pid")
        if pid and is_process_running(pid):
            return True, pid, lock_fd

        return False, None, lock_fd
    except (json.JSONDecodeError, KeyError, IOError):
        return False, None, lock_fd


def write_state_locked(
    lock_fd,
    start_time: float,
    interval_seconds: int,
    reminder_count: int,
    pid: int,
) -> None:
    """
    Write state while holding an existing lock.

    Args:
        lock_fd: Lock file descriptor from acquire_lock_and_check()
        start_time: Unix timestamp when current interval started
        interval_seconds: Total seconds in the interval
        reminder_count: Number of reminders sent
        pid: Process ID of the running hydrate instance
    """
    state = {
        "start_time": start_time,
        "interval_seconds": interval_seconds,
        "reminder_count": reminder_count,
        "pid": pid,
    }

    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def release_lock(lock_fd) -> None:
    """Release lock acquired by acquire_lock_and_check()."""
    _release_lock(lock_fd)
