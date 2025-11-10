"""Sounds command - List all available sound files."""

import typer
from rich.table import Table

from lib.utils import console, get_player, DEFAULT_SOUND, SOUNDS_DIR


def sounds():
    """List all available sound files."""
    try:
        player = get_player()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    available = player.list_sounds()

    if not available:
        console.print("[yellow]No sound files found in sounds/ directory[/yellow]")
        raise typer.Exit(1)

    table = Table(title="Available Sounds", show_header=True)
    table.add_column("Sound File", style="cyan")
    table.add_column("Default", style="green")

    for sound in available:
        is_default = "✓" if sound == DEFAULT_SOUND else ""
        table.add_row(sound, is_default)

    console.print(table)
    console.print(f"\n[dim]Sounds directory: {SOUNDS_DIR}[/dim]")
