# sourcery skip: avoid-global-variables
# src/mad_icon/commands/generate_launch_screens.py
"""
(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).

Command for generating PWA launch screens.
"""

from pathlib import Path
from typing import IO, Annotated  # Use Union for clarity with multiple types

import typer

from mad_icon.types.types import LogoLaunchScreenCLIParam
from mad_icon.utilities import data_path, parse_launch_options


# Assuming FileBinaryRead is IO[bytes] or similar based on previous context
FileBinaryRead = typer.FileBinaryRead


app = typer.Typer()
cwd = Path.cwd()


@app.command("generate-launch-screens")
def generate_launch_screens(
    colored_logo: Annotated[
        LogoLaunchScreenCLIParam | None,
        typer.Option(
            None,  # Default value first
            "--colored-logo",
            parser=parse_launch_options,  # Keep parser as defined in original kwargs
            help="Option 1: Color (hex) and optional logo path (e.g., '#FF5733 path/to/logo.svg').",
        ),
    ] = None,
    launch_screen_image: Annotated[
        FileBinaryRead | None,
        typer.Option(
            None,  # Default value first
            "--launch-screen-image",
            dir_okay=False,
            resolve_path=True,
            readable=True,
            help="Option 2: Path to a rectangular image (SVG, PNG, JPG) for launch screens.",
        ),
    ] = None,
    launch_darkmode_image: Annotated[
        FileBinaryRead | LogoLaunchScreenCLIParam | None,  # Use Union for complex type
        typer.Option(
            None,  # Default value first
            "--launch-darkmode-image",
            parser=parse_launch_options,  # Keep parser
            help="Optional dark mode image or color/logo definition.",
        ),
    ] = None,
    launch_screen_dir_name: Annotated[
        str,
        typer.Option(
            "launch-screens",  # Default value first
            "--launch-screen-dir-name",
            help="Name of the launch screen directory.",
        ),
    ] = "launch-screens",
    launch_screen_base_name: Annotated[
        str,
        typer.Option(
            "apple-launch-screen",  # Default value first
            "--launch-screen-base-name",
            help="Base name of the launch screen files.",
        ),
    ] = "apple-launch-screen",
    generate_darkmode: Annotated[
        bool,
        typer.Option(
            False,  # Default value first
            "--generate-darkmode/--no-generate-darkmode",
            help="Whether to generate dark mode launch screens.",
        ),
    ] = False,
    screen_destination_dir: Annotated[
        Path,
        typer.Option(
            cwd / "assets" / "launch-screens",  # Default value first
            "--screen-destination-dir",
            file_okay=False,
            resolve_path=True,  # Added resolve_path
            help="Destination directory for launch screen assets.",
        ),
    ] = cwd / "assets" / "launch-screens",
    generate_html: Annotated[  # Renamed from generate_HTML
        bool,
        typer.Option(
            True,  # Default value first
            "--generate-html/--no-generate-html",
            help="Whether to generate HTML tags for the launch screens.",
        ),
    ] = True,
    html_file_name: Annotated[  # Renamed from HTML_file_name
        str,
        typer.Option(
            "paste-content-in-site-head-tags.html",  # Default value first
            "--html-file-name",
            help="Name of the HTML file for the launch screens.",
        ),
    ] = "paste-content-in-site-head-tags.html",
    html_destination: Annotated[  # Renamed from HTML_destination
        Path,
        typer.Option(
            cwd,  # Default value first
            "--html-destination",
            file_okay=False,
            resolve_path=True,
            dir_okay=True,
            help="Destination directory for the HTML file.",
        ),
    ] = cwd,
    json_path: Annotated[
        FileBinaryRead | None,  # Made optional, default handled below
        typer.Option(
            None,  # Default value first
            "--json-path",
            dir_okay=False,
            readable=True,
            help="Optional path to an alternate json file.",
        ),
    ] = None,
) -> None:
    """
    Generates PWA launch screens based on the provided image or color/logo and options.
    """
    # Placeholder for actual launch screen generation logic
    print("Generating launch screens...")
    print(f"Colored Logo: {colored_logo}")
    print(f"Launch Screen Image: {launch_screen_image.name if launch_screen_image else 'None'}")
    # ... print other args ...
    print(f"Screen Destination Dir: {screen_destination_dir}")
    print(f"Generate Dark Mode: {generate_darkmode}")
    # ... etc ...

    # Example: Handle default json_path if not provided
    actual_json_path_obj = None
    try:
        if json_path:
            actual_json_path_obj = json_path  # Use user-provided path
        else:
            # Open the default path only if json_path is None
            default_path = data_path()
            actual_json_path_obj = default_path.open("rb")

        print(
            f"Using JSON data from: {actual_json_path_obj.name if hasattr(actual_json_path_obj, 'name') else actual_json_path_obj}"
        )
        # --- Add logic to read/process actual_json_path_obj ---

    finally:
        # Ensure files opened by Typer or default logic are closed
        # Close files associated with LogoLaunchScreenCLIParam if they were opened by the parser
        if isinstance(colored_logo, LogoLaunchScreenCLIParam) and colored_logo.logo:
            colored_logo.logo.close()
        if launch_screen_image:
            launch_screen_image.close()
        # Handle complex type for darkmode image
        if (
            isinstance(launch_darkmode_image, LogoLaunchScreenCLIParam)
            and launch_darkmode_image.logo
        ):
            launch_darkmode_image.logo.close()
        elif isinstance(
            launch_darkmode_image, IO
        ):  # Check if it's specifically a file-like object (IO[bytes])
            launch_darkmode_image.close()

        # Close user-provided json_path if it exists
        if json_path:
            json_path.close()
        # Close the default path object if it was opened and json_path was None
        elif json_path is None and actual_json_path_obj is not None:
            actual_json_path_obj.close()

    print("Launch screen generation complete (placeholder).")


__all__ = ["generate_launch_screens"]
