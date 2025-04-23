# sourcery skip: avoid-global-variables
"""
(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).

Command for generating icons.
"""

# Removed unused imports like io, json, Sequence, cast, etc.
# Removed specific image processing imports as they are now in helpers
from pathlib import Path
from typing import IO, TYPE_CHECKING, Annotated, Any

import typer

# Import the public helper functions
from mad_icon.utilities import (
    cleanup_resources,
    determine_source_images,
    has_value,
    generate_output_files,
    prepare_output_directories,
    process_icon_category,
    validate_and_load_base_icon,
    retrieve_model
)


if TYPE_CHECKING:
    from mad_icon.models import MadIconModel


app = typer.Typer()
# Define FileBinaryRead for type hinting
FileBinaryRead = typer.FileBinaryRead

# Keep cwd if used for default paths, otherwise remove
cwd = Path.cwd()


@app.command("generate-icons")
def generate_icons(
    base_icon: Annotated[
        FileBinaryRead,
        typer.Argument(
            ...,
            dir_okay=False,
            resolve_path=True,
            readable=True,
            help="**Required.** Path to your main icon, or base, file. SVG works best. For best results, use a square `SVG` file with opaque background. If you provide a raster image (PNG, JPG, etc.), it should be at least 1024x1024 pixels. Icons should have no transparent features (background should be solid color).",
            formats=[".svg", ".png", ".jpg", ".jpeg", ".webp"],
        ),
    ],
    masked_icon: Annotated[
        FileBinaryRead | None,
        typer.Option(
            "--masked-icon",
            "-m",
            dir_okay=False,
            resolve_path=True,
            readable=True,
            help="""*Optional.* Path to an icon image to generate android `masked icons`. There should be no content within 20% of the edges of the image (if you want to keep the content). If you don't provide one, we'll use your `base-icon.`""",
            formats=[".svg", ".png", ".jpg", ".jpeg", ".webp"],
        ),
    ] = None,
    masked_monochrome_icon: Annotated[
        FileBinaryRead | None,
        typer.Option(
            "--masked-monochrome-icon",
            "-M",
            dir_okay=False,
            resolve_path=True,
            readable=True,
            help="*Optional.* Path to an icon image to generate android *monochrome* `masked icons`. These are used on some devices for an effect similar to Apple's tinted icons. If you don't provide one, we'll desaturate the `masked-icon` or `base-icon` (in that order).",
            formats=[".svg", ".png", ".jpg", ".jpeg", ".webp"],
        ),
    ] = None,
    apple_darkmode_icon: Annotated[
        FileBinaryRead | None,
        typer.Option(
            "--apple-darkmode-icon",
            "-a",
            dir_okay=False,
            resolve_path=True,
            readable=True,
            help="*Optional.* Path to an icon image to generate Apple darkmode icons. If you don't provide one, we'll use the next-best option (starting with `masked-icon`, then `base-icon`). Darkmode icons should have a transparent background and colorful foreground. Apple adds a dark gradient to the background, so you don't need to add one.",
            formats=[".svg", ".png", ".jpg", ".jpeg", ".webp"],
        ),
    ] = None,
    apple_tinted_icon: Annotated[
        FileBinaryRead | None,
        typer.Option(
            "--apple-tinted-icon",
            "-t",
            dir_okay=False,
            resolve_path=True,
            readable=True,
            help="[Experimental] *Optional.* Path to an icon image to generate Apple tinted icons. If you don't provide one, we'll use the next-best option (starting with desaturating the `apple-darkmode-icon`, then `base-icon`). Tinted icons have the same requirements as Apple Darkmode icons except they are fully grayscale (transparent background, grayscale foreground). Apple adds a dark gradient background.",
            formats=[".svg", ".png", ".jpg", ".jpeg", ".webp"],
        ),
    ] = None,
    tile_rectangle_icon: Annotated[
        FileBinaryRead | None,
        typer.Option(
            "--tile-rect-image",
            dir_okay=False,
            resolve_path=True,
            readable=True,
            help="*Optional.* Provide an special icon for the 310x150 ms-tile rectangle. If you don't provide one, we'll use the `base-icon`,)",
            formats=[".svg", ".png", ".jpg", ".jpeg", ".webp"],
        ),
    ] = None,
    prefix: Annotated[
        str,
        typer.Option(
            "--prefix",  # Explicit option name
            help="*Optional.* The naming prefix for base apple touch icons. Default is `apple-touch-icon`.",
        ),
    ] = "apple-touch-icon",
    destination_dir: Annotated[
        Path,
        typer.Option(
            "-d",
            "--destination-dir",
            file_okay=False,
            resolve_path=True,
            help="*Optional.* Destination directory to save generated assets. Default is an `assets` directory in the current working directory. Icons will be in appropriate subdirectories (such as `apple-touch-icons`, `masked-icons`, etc.).",
        ),
    ] = cwd / "assets",
    no_icons: Annotated[
        bool,
        typer.Option(
            False,
            "--no-icons",
            is_eager=True,
            help="Use `--no-icons` to disable all icon generation, producing only the HTML and manifest. We'll pretend you generated images with whatever settings you provide. You can also use this to only generate certain types of images without generating the base apple touch icons by explicitly passing the flags for those types (such as `--masked`)")] = False,
    masked: Annotated[
        bool,
        typer.Option(
            True,
            help="Use the negative flag to disable all masked icon generation, including the monochrome masked icons. You can still generate the monochrome icons separately with the `--masked-monochrome-icon` option.",
        ),
    ] = True,
    monochrome: Annotated[
        bool, typer.Option(True, help="Use --monochrome to override a `--no-masked` flag if you want masked monochrome images without masked images.")
    ] = True,
    darkmode: Annotated[
        bool, typer.Option(True, help="Use `--no-darkmode` to disable dark mode icon generation.")
    ] = True,
    tinted: Annotated[
        bool, typer.Option(True, help="Use `--no-tinted` to disable tinted icon generation.")
    ] = True,
    macos: Annotated[
        bool, typer.Option(True, help="Use `--no-macos` to disable macOS icon generation.")
    ] = True,
    ms_tiles: Annotated[
        bool, typer.Option(True, help="Use `--no-ms-tiles` to disable MS tile generation.")
    ] = True,
    html: Annotated[
        bool, typer.Option(True, help="Use `--no-html` to disable HTML generation.")
    ] = True,
    manifest: Annotated[
        bool, typer.Option(True, help="Use `--no-manifest` to disable manifest generation.")
    ] = True,
    html_file_name: Annotated[
        str,
        typer.Option(
            "paste-content-in-site-head-tags.html",
            help="Name of the HTML file for the icons. This and the manifest.json will be saved in the parent of the destination directory, by default the current working directory.",
        ),
    ] = "paste-content-in-site-head-tags.html",
    html_destination: Annotated[
        Path,
        typer.Option(
            cwd,
            "--html-destination",
            file_okay=False,
            resolve_path=True,
            dir_okay=True,
            help="*Optional*. Destination directory for the HTML file and manifest.json. Default is the current working directory.",
        ),
    ] = cwd,
    json_path: Annotated[
        FileBinaryRead | None,  # Made optional, default handled below
        typer.Option(
            "--alternate-data",
            dir_okay=False,
            readable=True,
            help="*Very optional.* If for some reason you don't want to use the default data included in the package (like if you want to add a new icon size), you can provide your own json file. You can use the `get-data` command to get a copy of the data, and then edit it. If our data is wrong or incomplete, please open an issue on [GitHub](https://github.com/knitli/mad_icon/issues). The default data is included in the package.",
            formats=[".json"],
        ),
    ] = None,
    attempt_svg_analysis: Annotated[
        bool,
        typer.Option(
            False,  # Default value first
            help="[Experimental] Attempt to analyze input SVG structure to automatically handle backgrounds for dark/tinted modes. If you only provide a base-icon and keep the other flags on their defaults, this will be used to generate the other icons. If you provide a masked-icon, this will be ignored. You can use this flag to override the default behavior.",
        ),
    ] = False,
) -> None:
    """
    Generates various PWA icons based on the provided input image and options.
    Orchestrates the icon generation process by calling helper functions.
    """
    typer.echo("Starting PWA icon generation...")

    # Consolidate CLI args into a single config dict for easier passing
    # Using locals() is convenient but be mindful of potential extra variables
    cli_config = {k: v for k, v in locals().items() if not k.startswith("_")}
    cli_config["sizes"] = retrieve_model(cli_config["json_path"]).size_data
    processed_cli_config = process_icon_kwargs(
        cli_config)

    pwa_model: MadIconModel | None = None
    opened_json_file: IO[bytes] | None = None
    all_html_tags: list[str] = []
    all_manifest_icons: list[dict[str, Any]] = []

    try:
        # 1. Load PWA Model
        pwa_model, opened_json_file = load_mad_model(cli_config["json_path"])

        # 2. Prepare Output Dirs
        output_paths = prepare_output_directories(cli_config)

        # 3. Validate Inputs & Load Base Icon
        # Ensure base-icon is not None before passing (Typer should handle this)
        has_value(cli_config["base-icon"])

        base_icon_data, _, base_icon_type = validate_and_load_base_icon(
            cli_config["base-icon"],
            cli_config["masked_image"],
            generate_masked_icons=cli_config["generate_masked_icons"],
        )

        # 4. Determine Source Images for Each Category
        source_data, source_type = determine_source_images(
            cli_config, base_icon_data, base_icon_type
        )    generate_manifest: Annotated[
        bool,
        typer.Option(
            True,  # Default value first
            "--generate-manifest/--no-generate-manifest",
            help="Whether to generate a manifest.json file.",
        ),
    ] = True,
        # 5. Get Icon Config Categories
        icon_categories_config = ICON_CONFIG

        # 6. Process Each Icon Category
        typer.echo("Generating icon sets...")
        for category_config in icon_categories_config:
            # Check generation flag using the key from the config
            flag_key = category_config.get("flag_key")

            # Check if the category should be skipped based on the flag
            should_skip = False
            if flag_key is not None and (
                isinstance(flag_key, str) and not cli_config.get(flag_key)
            ):
                should_skip = True

            if should_skip:
                typer.echo(
                    f"Skipping {category_config['name']} icons (disabled by flag: {flag_key})."
                )
                continue

            typer.echo(f"--- Generating {category_config['name']} Icons ---")
            try:
                # Call the helper function for this category
                html_tags, manifest_icons = process_icon_category(
                    category_config=category_config,
                    pwa_model=pwa_model,
                    source_data=source_data,
                    source_type=source_type,
                    output_paths=output_paths,
                    cli_config=cli_config,
                )
                # Aggregate results
                all_html_tags.extend(html_tags)
                all_manifest_icons.extend(manifest_icons)
            except Exception as e:
                # Log error and continue with the next category
                typer.echo(
                    f"  Error processing category '{category_config['name']}': {e}", err=True
                )
                # Optionally re-raise if errors should halt the whole process

        # 7. Generate Output Metadata Files
        generate_output_files(all_html_tags, all_manifest_icons, output_paths, cli_config)

        typer.echo("PWA icon generation process complete.")

    except typer.Exit:
        # Allow Typer validation errors to exit cleanly without double message
        raise
    except Exception as e:
        # Catch unexpected errors during orchestration
        typer.echo(f"An unexpected error occurred during icon generation: {e}", err=True)
        # Add traceback here if needed for debugging
        # import traceback
        # typer.echo(traceback.format_exc(), err=True)
        raise typer.Exit(code=1) from e
    finally:
        cleanup_resources(cli_config, opened_json_file)


if __name__ == "__main__":
    app()

__all__ = ["generate_icons"]
