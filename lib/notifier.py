"""Sound notification handler for hydration reminders."""

from pathlib import Path
import subprocess


class SoundPlayer:
    """Handle sound playback via PowerShell on Windows."""

    def __init__(self, sounds_dir: Path):
        """
        Initialize the sound player.

        Args:
            sounds_dir: Directory containing sound files
        """
        self.sounds_dir = sounds_dir

        if not self.sounds_dir.exists():
            raise FileNotFoundError(f"Sounds directory not found: {sounds_dir}")

    def _wsl_to_windows_path(self, wsl_path: Path) -> str:
        """
        Convert WSL path to Windows path.

        Args:
            wsl_path: Path in WSL filesystem

        Returns:
            Windows-formatted path string
        """
        result = subprocess.check_output(["wslpath", "-w", str(wsl_path)], text=True)
        return result.strip()

    def play_wav(self, sound_file: str, volume: float = 1.0) -> None:
        """
        Play a WAV file using Windows MediaPlayer with volume control.

        Args:
            sound_file: Name of sound file in sounds_dir (e.g., 'simple.wav')
            volume: Volume level from 0.0 (silent) to 1.0 (max). Default is 1.0

        Raises:
            FileNotFoundError: If sound file doesn't exist
            subprocess.CalledProcessError: If playback fails
            ValueError: If volume is out of range
        """
        if not 0.0 <= volume <= 1.0:
            raise ValueError(f"Volume must be between 0.0 and 1.0, got {volume}")

        sound_path = self.sounds_dir / sound_file

        if not sound_path.exists():
            raise FileNotFoundError(f"Sound file not found: {sound_path}")

        win_path = self._wsl_to_windows_path(sound_path)

        powershell_cmd = f"""
        Add-Type -AssemblyName presentationCore
        $mediaPlayer = New-Object system.windows.media.mediaplayer
        $mediaPlayer.Volume = {volume}
        $mediaPlayer.open('{win_path}')
        $mediaPlayer.Play()
        Start-Sleep -Seconds 2
        """

        subprocess.run(
            ["powershell.exe", "-c", powershell_cmd], capture_output=True, check=True
        )

    def list_sounds(self) -> list[str]:
        """
        List available sound files.

        Returns:
            List of WAV filenames
        """
        return sorted([f.name for f in self.sounds_dir.glob("*.wav")])

    def validate_sound(self, sound_file: str) -> bool:
        """
        Check if a sound file exists.

        Args:
            sound_file: Name of sound file

        Returns:
            True if file exists, False otherwise
        """
        return (self.sounds_dir / sound_file).exists()
