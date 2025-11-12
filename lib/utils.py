"""Shared utilities for the hydrate CLI."""

from pathlib import Path
from rich.console import Console

from lib.notifier import SoundPlayer, WindowsNotifier

SOUNDS_DIR = Path(__file__).parent.parent / "sounds"
DEFAULT_SOUND = "droplet.wav"
DEFAULT_VOLUME = 1.0
DEFAULT_NOTIFICATIONS_ENABLED = True

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


def get_notifier(app_id: str = "Hydrate") -> WindowsNotifier:
    """
    Get initialized Windows notifier.

    Args:
        app_id: Application identifier for notifications

    Returns:
        WindowsNotifier instance
    """
    return WindowsNotifier(app_id)
