"""Shared utilities for the hydrate CLI."""

from pathlib import Path
from rich.console import Console

from lib.notifier import SoundPlayer

SOUNDS_DIR = Path(__file__).parent.parent / "sounds"
DEFAULT_SOUND = "droplet.wav"
DEFAULT_VOLUME = 1.0

console = Console()


def get_player() -> SoundPlayer:
    """
    Get initialized sound player.

    Returns:
        SoundPlayer instance

    Raises:
        FileNotFoundError: If sounds directory doesn't exist
    """
    return SoundPlayer(SOUNDS_DIR)
