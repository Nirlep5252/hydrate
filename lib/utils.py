"""Shared utilities for the hydrate CLI."""

import platform
import shutil
from pathlib import Path
from rich.console import Console

from lib.notifier import SoundPlayer, WindowsNotifier, LinuxSoundPlayer, LinuxNotifier

SOUNDS_DIR = Path(__file__).parent.parent / "sounds"
DEFAULT_SOUND = "droplet.wav"
DEFAULT_VOLUME = 1.0
DEFAULT_NOTIFICATIONS_ENABLED = True

console = Console()


def get_platform() -> str:
    """
    Detect if running on native Linux, WSL, or Windows.

    Returns:
        'linux' for native Linux, 'wsl' for WSL, 'windows' for Windows,
        or the platform name for other systems.
    """
    system = platform.system().lower()
    if system == "linux":
        # Check if running in WSL
        try:
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    return "wsl"
        except FileNotFoundError:
            pass
        return "linux"
    return system


def get_player() -> SoundPlayer | LinuxSoundPlayer:
    """
    Get initialized sound player for the current platform.

    Returns:
        SoundPlayer instance for Windows/WSL, LinuxSoundPlayer for native Linux

    Raises:
        FileNotFoundError: If sounds directory doesn't exist
    """
    current_platform = get_platform()
    if current_platform == "linux":
        return LinuxSoundPlayer(SOUNDS_DIR)
    return SoundPlayer(SOUNDS_DIR)  # WSL or Windows


def get_notifier(app_id: str = "Hydrate") -> WindowsNotifier | LinuxNotifier:
    """
    Get initialized notifier for the current platform.

    Args:
        app_id: Application identifier for notifications

    Returns:
        WindowsNotifier for Windows/WSL, LinuxNotifier for native Linux
    """
    current_platform = get_platform()
    if current_platform == "linux":
        return LinuxNotifier(app_id)
    return WindowsNotifier(app_id)  # WSL or Windows
