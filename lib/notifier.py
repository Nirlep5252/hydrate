"""Notification handlers for hydration reminders."""

from pathlib import Path
import subprocess
from typing import Optional
import logging

logger = logging.getLogger(__name__)


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
        Play a WAV file using Windows MediaPlayer with volume control (non-blocking).

        Args:
            sound_file: Name of sound file in sounds_dir (e.g., 'simple.wav')
            volume: Volume level from 0.0 (silent) to 1.0 (max). Default is 1.0

        Raises:
            FileNotFoundError: If sound file doesn't exist
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

        subprocess.Popen(
            ["powershell.exe", "-c", powershell_cmd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
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


class WindowsNotifier:
    """Handle Windows toast notifications via PowerShell with BurntToast fallback."""

    def __init__(self, app_id: str = "Hydrate"):
        """
        Initialize the Windows notifier.

        Args:
            app_id: Application identifier for notifications
        """
        self.app_id = app_id
        self._is_available = self._check_availability()
        self._has_burnttoast = self._check_burnttoast()

    def _check_availability(self) -> bool:
        """
        Check if PowerShell is available for notifications.

        Returns:
            True if PowerShell is accessible, False otherwise
        """
        try:
            result = subprocess.run(
                ["powershell.exe", "-Command", "echo 'test'"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"PowerShell not available: {e}")
            return False

    def _check_burnttoast(self) -> bool:
        """
        Check if BurntToast PowerShell module is available.

        Returns:
            True if BurntToast is installed, False otherwise
        """
        if not self._is_available:
            return False

        try:
            result = subprocess.run(
                ["powershell.exe", "-Command", "Get-Module -ListAvailable BurntToast"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return "BurntToast" in result.stdout
        except Exception:
            return False

    @property
    def is_available(self) -> bool:
        """
        Check if notifications are available.

        Returns:
            True if notifications can be sent, False otherwise
        """
        return self._is_available

    def send_notification(
        self,
        title: str,
        message: str,
        duration: str = "short",
    ) -> bool:
        """
        Send a Windows toast notification via PowerShell.

        Args:
            title: Notification title
            message: Notification message body
            duration: Duration of notification ('short' or 'long')

        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.is_available:
            logger.debug("Notifications not available, skipping")
            return False

        if self._has_burnttoast:
            return self._send_via_burnttoast(title, message)
        else:
            return self._send_via_powershell_native(title, message, duration)

    def _send_via_burnttoast(self, title: str, message: str) -> bool:
        """
        Send notification using BurntToast module.

        Args:
            title: Notification title
            message: Notification message body

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            escaped_title = title.replace("'", "''")
            escaped_message = message.replace("'", "''")

            powershell_cmd = f"""
            Import-Module BurntToast
            New-BurntToastNotification -Text '{escaped_title}', '{escaped_message}' -AppLogo '' -Silent
            """

            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", powershell_cmd],
                capture_output=True,
                text=True,
                timeout=10,
            )

            return result.returncode == 0

        except Exception as e:
            logger.error(f"Failed to send notification via BurntToast: {e}")
            return False

    def _send_via_powershell_native(
        self, title: str, message: str, duration: str
    ) -> bool:
        """
        Send notification using native PowerShell Windows Runtime APIs.

        Args:
            title: Notification title
            message: Notification message body
            duration: Duration of notification ('short' or 'long')

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            duration_param = "Long" if duration == "long" else "Short"

            escaped_title = title.replace("'", "''").replace('"', '`"')
            escaped_message = message.replace("'", "''").replace('"', '`"')

            # Use PowerShell's AppID to ensure notifications show
            app_id = "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe"

            powershell_cmd = f"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            $APP_ID = '{app_id}'

            $template = @"
<toast duration="{duration_param}">
    <visual>
        <binding template="ToastGeneric">
            <text>{escaped_title}</text>
            <text>{escaped_message}</text>
        </binding>
    </visual>
    <audio silent="true"/>
</toast>
"@

            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)
            """

            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", powershell_cmd],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0 and result.stderr:
                logger.warning(f"PowerShell notification warning: {result.stderr}")

            return True

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    def send_hydration_reminder(self, reminder_count: int) -> bool:
        """
        Send a hydration reminder notification.

        Args:
            reminder_count: Current count of reminders sent

        Returns:
            True if notification sent successfully, False otherwise
        """
        ordinal = self._get_ordinal(reminder_count)
        title = f"💧 Time to Hydrate! ({ordinal} reminder)"
        message = "Take a moment to drink some water and stay healthy!"

        return self.send_notification(title, message, duration="short")

    @staticmethod
    def _get_ordinal(n: int) -> str:
        """
        Convert number to ordinal string (1st, 2nd, 3rd, etc.).

        Args:
            n: Number to convert

        Returns:
            Ordinal string representation
        """
        if 11 <= n % 100 <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"
