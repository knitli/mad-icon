# sourcery skip: avoid-global-variables
"""
`get_data.py` module. - Command for retrieving the Mad Icon data model as a JSON file.

`get_data` provides the tool's underlying data model in JSON format, the most interesting part is a comprehensive list of Apple devices, screen resolutions, and related data (see [`models module`](models/models.py) for details).

(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).
"""

from pathlib import Path
from typing import Annotated

import typer

from rich.prompt import Prompt
from rich import print_json

from mad_icon.utilities import data_path


app = typer.Typer()

cwd = Path.cwd()


def print_to_stdout() -> None:
    """Prints the data to stdout in JSON format."""
    data = data_path().read_text()
    print_json(data, sort_keys=True)
    raise typer.Exit


@app.command("get-data")
def get_data(
    destination: Annotated[
        Path,
        typer.Option(
            cwd / "data.json",
            resolve_path=True,
            help="Optional path to save the output data file. The default is `data.json` in the current working directory.",
        ),
    ],
    print_data: Annotated[
        bool,
        typer.Option(
            False,
            "--print",
            callback=print_to_stdout,
            is_eager=True,
            help="Print the data to stdout (your terminal) in JSON format.",
        ),
    ],
) -> None:
    """Saves the module's `data.json` file to your specified destination, or the current working directory."""
    if destination.is_dir():
        destination = destination / "data.json"
    if destination.exists():
        overwrite = Prompt.ask(
            f"{destination!s} already exists. Overwrite?", choices=["y", "n"], default="n"
        )
        if overwrite == "n":
            typer.echo("Aborted.")
            raise typer.Exit
    data_file = data_path().read_bytes()
    destination.write_bytes(data_file)
    typer.echo(f"Data saved to {destination!s}")
