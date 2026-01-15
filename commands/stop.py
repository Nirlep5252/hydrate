"""Stop command - Stop running hydration daemon."""

import os
import signal
import typer

from lib.utils import console
from lib.state import is_running, clear_state


def stop():
    """
    Stop running hydration daemon.

    Sends SIGTERM to the running hydrate process.
    """
    running, pid = is_running()

    if not running:
        console.print("[yellow]No hydrate daemon is running.[/yellow]")
        raise typer.Exit(0)

    try:
        os.kill(pid, signal.SIGTERM)
        console.print(f"[green]Stopped hydrate daemon (PID: {pid})[/green]")
        clear_state()
    except ProcessLookupError:
        console.print("[yellow]Process already stopped.[/yellow]")
        clear_state()
    except PermissionError:
        console.print(f"[red]Permission denied to stop process {pid}[/red]")
        raise typer.Exit(1)
