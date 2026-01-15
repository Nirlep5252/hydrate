"""Start command - Run hydration reminder daemon."""

import time
import typer
from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.containers import Center, Middle
from textual.reactive import reactive

from lib.utils import (
    console,
    get_player,
    get_notifier,
    DEFAULT_SOUND,
    DEFAULT_VOLUME,
    DEFAULT_NOTIFICATIONS_ENABLED,
)


class HydrationApp(App):
    """Textual TUI app for hydration countdown."""

    CSS = """
    Screen {
        align: center middle;
    }

    #countdown-container {
        width: 70;
        height: 15;
        border: heavy cyan;
        padding: 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: cyan;
    }

    #progress-bar {
        text-align: center;
        text-style: bold;
        color: cyan;
    }

    #timer {
        text-align: center;
        text-style: bold;
        color: yellow;
    }

    #info {
        text-align: center;
        color: gray;
        margin-top: 1;
    }
    """

    total_seconds = reactive(60)
    reminder_count = reactive(0)

    def __init__(
        self,
        interval: int,
        sound: str,
        volume: float,
        player,
        notifier=None,
        enable_notifications: bool = True,
    ):
        super().__init__()
        self.interval = interval
        self.sound = sound
        self.volume = volume
        self.player = player
        self.notifier = notifier
        self.enable_notifications = enable_notifications
        self.total_seconds = interval * 60
        self.start_time = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("💧 HYDRATION COUNTDOWN", id="title")
        yield Static("", id="progress-bar")
        yield Static("", id="timer")

        notif_status = "ON" if self.enable_notifications and self.notifier and self.notifier.is_available else "OFF"
        yield Static(
            f"Interval: {self.interval}min | Sound: {self.sound} | Volume: {int(self.volume * 100)}% | Notifications: {notif_status}\nPress Ctrl+C or 'q' to quit",
            id="info"
        )

    def on_mount(self) -> None:
        """Called when app starts."""
        self.start_time = time.time()
        self.set_interval(1.0, self.update_countdown)

        self._trigger_reminder()

        # Initial display
        self.update_display(0)

    def _trigger_reminder(self) -> None:
        """Trigger sound and notification reminders."""
        self.reminder_count += 1

        # Play sound
        try:
            self.player.play_wav(self.sound, self.volume)
        except Exception:
            pass

        # Send notification
        if self.enable_notifications and self.notifier and self.notifier.is_available:
            try:
                self.notifier.send_hydration_reminder(self.reminder_count)
            except Exception:
                pass

    def update_countdown(self) -> None:
        """Update countdown timer."""
        if self.start_time is None:
            return

        current_time = time.time()
        elapsed = current_time - self.start_time

        if elapsed >= self.total_seconds:
            self._trigger_reminder()

            # Reset timer
            self.start_time = current_time
            elapsed = 0

        self.update_display(elapsed)

    def update_display(self, elapsed: float) -> None:
        """Update the display widgets."""
        # Calculate remaining time and progress
        remaining = max(0, self.total_seconds - elapsed)
        percentage = min(elapsed / self.total_seconds, 1.0) if self.total_seconds > 0 else 0

        # Create progress bar (50 chars)
        total_blocks = 50
        filled = int(percentage * total_blocks)
        empty = total_blocks - filled
        bar = "█" * filled + "░" * empty

        # Format time
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        time_str = f"{mins:02d}:{secs:02d}"

        # Update widgets
        progress_widget = self.query_one("#progress-bar", Static)
        timer_widget = self.query_one("#timer", Static)

        progress_widget.update(f"{bar}  {int(percentage * 100)}%")
        timer_widget.update(f"⏱  {time_str}")

    def action_quit(self) -> None:
        """Quit the app."""
        self.exit()

    def on_key(self, event) -> None:
        """Handle key press."""
        if event.key == "q":
            self.exit()


def start(
    interval: int = typer.Option(
        60,
        "--interval",
        "-i",
        help="Minutes between reminders",
        min=1,
    ),
    sound: str = typer.Option(
        DEFAULT_SOUND,
        "--sound",
        "-s",
        help="Sound file to play (from sounds/ directory)",
    ),
    volume: float = typer.Option(
        DEFAULT_VOLUME,
        "--volume",
        "-v",
        help="Volume level (0.0 to 1.0)",
        min=0.0,
        max=1.0,
    ),
    notifications: bool = typer.Option(
        DEFAULT_NOTIFICATIONS_ENABLED,
        "--notifications/--no-notifications",
        "-n/-N",
        help="Enable desktop notifications",
    ),
):
    """
    Start hydration reminder daemon.

    Plays a sound and shows notifications at regular intervals to remind you to drink water.
    Press Ctrl+C or 'q' to stop.
    """
    try:
        player = get_player()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if not player.validate_sound(sound):
        console.print(f"[red]Error:[/red] Sound file '{sound}' not found!")
        console.print("\n[cyan]Available sounds:[/cyan]")
        for s in player.list_sounds():
            console.print(f"  • {s}")
        raise typer.Exit(1)

    notifier = get_notifier() if notifications else None

    console.print(
        f"[green]Starting hydration reminders every {interval} minute{'s' if interval != 1 else ''}[/green]"
    )
    console.print(f"[cyan]Sound:[/cyan] {sound}")
    console.print(f"[cyan]Volume:[/cyan] {int(volume * 100)}%")

    if notifications:
        if notifier and notifier.is_available:
            console.print("[cyan]Notifications:[/cyan] Enabled ✓")
        else:
            console.print(
                "[yellow]Notifications:[/yellow] Requested but unavailable"
            )
    else:
        console.print("[cyan]Notifications:[/cyan] Disabled")

    console.print("[yellow]Press Ctrl+C or 'q' to stop[/yellow]\n")

    app = HydrationApp(interval, sound, volume, player, notifier, notifications)

    try:
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        console.print("\n[yellow]Stopping reminders. Stay hydrated! 💧[/yellow]")
        console.print(f"[cyan]Total reminders played:[/cyan] {app.reminder_count}")
