# sourcery skip: avoid-global-variables
"""
Mad Icon (and Launch Screen) Generator
This cli tool generates PWA icons and launch screens for iOS devices.
The tool reads `data/resolutions.json` to get the resolutions to generate.

By default, the generated files are saved in `assets/splash-screens` and `assets/logo-icons`.

(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).
"""

import typer

import mad_icon.generate_icons as generate_icons
import mad_icon.generate_launch_screens as generate_launch_screens
import mad_icon.get_data as get_data


app = typer.Typer()
app.add_typer(generate_icons.app, name="generate-icons")
app.add_typer(generate_launch_screens.app, name="generate-launch-screens")
app.add_typer(get_data.app, name="get-data")


if __name__ == "__main__":
    app()


__all__ = ["app"]
