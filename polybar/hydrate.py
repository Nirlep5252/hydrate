#!/usr/bin/env python3
"""Polybar module script for hydrate countdown display."""

import json
import os
import time
from pathlib import Path

STATE_FILE = Path.home() / ".hydrate" / "state.json"


def is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def format_time(seconds: int) -> str:
    """Format seconds as MM:SS."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def main():
    """Output countdown for polybar."""
    if not STATE_FILE.exists():
        print("\U0001f4a7 h2o")
        return

    try:
        state = json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        print("\U0001f4a7 h2o")
        return

    pid = state.get("pid")
    if not pid or not is_process_running(pid):
        print("\U0001f4a7 h2o")
        return

    start_time = state.get("start_time", time.time())
    interval_seconds = state.get("interval_seconds", 3600)

    elapsed = time.time() - start_time
    remaining = max(0, int(interval_seconds - elapsed))

    print(f"\U0001f4a7 {format_time(remaining)}")


if __name__ == "__main__":
    main()
