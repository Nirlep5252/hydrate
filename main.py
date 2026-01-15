import sys
import typer

from commands.start import start
from commands.sounds import sounds
from commands.stop import stop

app = typer.Typer(help="Stay hydrated with sound reminders")

app.command()(start)
app.command()(sounds)
app.command()(stop)


if __name__ == "__main__":
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1].startswith('-')):
        sys.argv.insert(1, 'start')

    app()
