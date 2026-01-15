#!/usr/bin/env python3
"""Polybar module script for hydrate countdown display."""

import json
import sys
import time
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from lib.state import is_process_running

STATE_FILE = Path.home() / ".hydrate" / "state.json"


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
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
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
