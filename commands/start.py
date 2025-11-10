"""Start command - Run hydration reminder daemon."""

import time
import typer
import schedule

from lib.utils import console, get_player, DEFAULT_SOUND, DEFAULT_VOLUME


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
):
    """
    Start hydration reminder daemon.

    Plays a sound at regular intervals to remind you to drink water.
    Press Ctrl+C to stop.
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

    console.print(
        f"[green]Starting hydration reminders every {interval} minute{'s' if interval != 1 else ''}[/green]"
    )
    console.print(f"[cyan]Sound:[/cyan] {sound}")
    console.print(f"[cyan]Volume:[/cyan] {int(volume * 100)}%")
    console.print("\n[yellow]Press Ctrl+C to stop[/yellow]\n")

    def remind():
        """Play reminder sound and show message."""
        try:
            player.play_wav(sound, volume)
            timestamp = time.strftime("%H:%M:%S")
            console.print(f"[{timestamp}] 💧 [bold cyan]Time to hydrate![/bold cyan]")
        except Exception as e:
            console.print(f"[red]Error playing sound:[/red] {e}")

    schedule.every(interval).minutes.do(remind)

    console.print("[dim]Playing first reminder...[/dim]")
    remind()

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping reminders. Stay hydrated! 💧[/yellow]")
