# sourcery skip: avoid-global-variables
"""
(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).

Command for generating icons.
"""

from pathlib import Path
from typing import IO, TYPE_CHECKING, Annotated, Any

import typer

from mad_icon.types import (
    IconGenerationConfig,
    IconGenerationContext,
    IconGenerationFlag,
    IconSourceKey,
    get_flag_config,
)

from mad_icon.utilities import (
    cleanup_resources,
    determine_source_images,
    generate_output_files,
    has_value,  # Keep has_value for base_icon check
    prepare_output_directories,
    process_icon_category,
    retrieve_model,
    validate_and_load_base_icon,
)


if TYPE_CHECKING:
    from mad_icon.models import MadIconModel


app = typer.Typer()
# Define FileBinaryRead for type hinting
FileBinaryRead = typer.FileBinaryRead

# Keep cwd if used for default paths, otherwise remove
cwd = Path.cwd()


def get_non_flag_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """

    """
    non_source_keys = ("prefix", "destination_dir", "html_destination", "html_file_name","json_path")
    image_kwargs, non_image_kwargs = {}, {}
    for k, v in kwargs.items():
        if not has_value(v):
            continue
        if k in non_source_keys:
            non_image_kwargs[k] = v
        image_kwargs[IconSourceKey.from_flag(k)] = v
    if "html_destination" and "html_file_name" in non_image_kwargs:
        name = non_image_kwargs.pop("html_file_name")
        non_image_kwargs["html_destination"] = non_image_kwargs["html_destination"] / name if name not in str(html_destination) else html_destination

    return {k: v for k, v in kwargs.items() if not k.startswith("--") and not k.startswith("-")}


def parse_arguments(kwargs: dict[str, Any]) -> None:
    """
    Parse command line arguments and options.
    This function is called when the script is executed.
    """
    icon_kwargs, non_icon_kwargs = get_non_flag_kwargs(kwargs), get_non_flag_kwargs(kwargs)
    received_flags = {k: IconGenerationFlag.from_value(k) for k, v in kwargs.items() if v and k in IconGenerationFlag.__members__}
    possible_flags = IconGenerationFlag.get_all_flags()
    other_kwargs = {k: v for k, v in kwargs.items() if v and "icon" in k or k in non_source_keys}
    other_kwargs = {k: (IconSourceKey.from_flag(k), v) for k, v in other_kwargs.items() if "icon" in k or k in ("prefix", "destination_dir", "html_destination", "json_path")}
    for k, v in other_kwargs.items():
        if "icon" in k:
            other_kwargs[k] = (IconSourceKey.from_flag(k), v)
        elif "destination" in k or "path" in k:
            if "html" in k and
    non_icon_flags = [flag for flag in received_flags.values() if flag and flag in possible_flags and IconGenerationFlag.is_not_icon_flag(flag)]
    icon_flags = [flag for flag in received_flags.values() if not IconGenerationFlag.is_not_icon_flag(flag)]
    if non_icon_flags and IconGenerationFlag.NO_ICONS in non_icon_flags:
        if icon_flags and not



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
            help="Use `--no-icons` to disable all icon generation, producing only the HTML and manifest. We'll pretend you generated images with whatever settings you provide. You can also use this to only generate certain types of images without generating the base apple touch icons by explicitly passing the flags for those types (such as `--masked`)",
        ),
    ] = False,
    masked: Annotated[
        bool,
        typer.Option(
            True,
            help="Use the negative flag to disable all masked icon generation, including the monochrome masked icons. You can still generate the monochrome icons separately with the `--masked-monochrome-icon` option.",
        ),
    ] = True,
    monochrome: Annotated[
        bool,
        typer.Option(
            True,
            help="Use --monochrome to override a `--no-masked` flag if you want masked monochrome images without masked images.",
        ),
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
            False,
            help="[Experimental] Attempt to analyze input SVG structure to automatically handle backgrounds for dark/tinted modes. If you only provide a base-icon and keep the other flags on their defaults, this will be used to generate the other icons. If you provide a masked-icon, this will be ignored. You can use this flag to override the default behavior.",
        ),
    ] = False,
) -> None:
    """
    Generates various PWA icons based on the provided input image and options.
    Orchestrates the icon generation process by calling helper functions.
    """
    typer.echo("Starting PWA icon generation...")

    # --- Refactored Initialization ---
    mad_model: MadIconModel | None = None
    opened_json_file: IO[bytes] | None = None  # Keep track for cleanup
    all_html_tags: list[str] = []
    all_manifest_icons: list[dict[str, Any]] = []

    try:
        # 1. Load Mad Model (/models/models.py)
        mad_model: 'MadIconModel | None' = retrieve_model(json_path)

        # 2. Parse flags and options
        received_flags = {k: IconGenerationFlag.from_value(k) for k, v in locals().items() if v and k in IconGenerationFlag.__members__}
        flags = IconGenerationFlag.get_all_flags()
        explicit_icon_flags_set = any([masked, monochrome, darkmode, tinted, macos, ms_tiles])
        for flag in flags:
            if flag.value in received_flags:
                active_flags.append(flag)

        # 2. Prepare Output Dirs (Passing explicit args for now)
        # TODO: Refactor prepare_output_directories later to accept context or fewer args
        prep_dir_config = {
            "destination_dir": destination_dir,
            "icon_dir_name": prefix,  # Assuming prefix is used as icon dir name base
            "html_destination": html_destination,
            "generate_masked_icons": masked or monochrome,  # Simplified logic
            "generate_darkmode_icons": darkmode,
            "generate_tinted_icons": tinted,
            "generate_macos_icons": macos,
            "generate_ms_tiles": ms_tiles,
            "generate_html": html,
            "generate_manifest": manifest,
        }
        output_paths = prepare_output_directories(prep_dir_config)

        has_value(base_icon)  # Check base_icon is provided
        # 3. Validate and Load Base Icon
        base_icon_data, _, base_icon_type = validate_and_load_base_icon(
            base_icon,
            masked_icon,  # Pass the arg directly
            generate_masked_icons=masked or monochrome,  # Pass explicit flag
        )

        # 4. Determine Source Images for Each Category
        source_images: dict[IconSourceKey, tuple[bytes, str]] = determine_source_images(
            base_icon_data=base_icon_data,
            base_icon_type=base_icon_type,
            masked_icon_arg=masked_icon,
            monochrome_icon_arg=masked_monochrome_icon,
            dark_icon_arg=apple_darkmode_icon,
            tinted_icon_arg=apple_tinted_icon,
            tile_rect_icon_arg=tile_rectangle_icon,
        )

        # 5. Determine Active Flags & Generate Configs

        if no_icons:
            if html:
                active_flags.append(IconGenerationFlag.HTML)
            if manifest:
                active_flags.append(IconGenerationFlag.MANIFEST)
            # If specific icon flags are also true, add them despite no_icons
            if masked:
                active_flags.append(IconGenerationFlag.MASKED)
            if monochrome:
                active_flags.append(IconGenerationFlag.MONOCHROME)
            if darkmode:
                active_flags.append(IconGenerationFlag.DARKMODE)
            if tinted:
                active_flags.append(IconGenerationFlag.TINTED)
            if macos:
                active_flags.append(IconGenerationFlag.MACOS)
            if ms_tiles:
                active_flags.append(IconGenerationFlag.MS_TILES)
        else:
            # Default: Add APPLE_TOUCH if no other icon flag is explicitly set true
            if not explicit_icon_flags_set:
                active_flags.append(IconGenerationFlag.APPLE_TOUCH)
            # Add flags that are true
            if masked:
                active_flags.append(IconGenerationFlag.MASKED)
            # Handle monochrome potentially overriding --no-masked
            if monochrome and not masked:
                if IconGenerationFlag.MASKED not in active_flags:
                    active_flags.append(IconGenerationFlag.MASKED)  # Add masked base
                active_flags.append(IconGenerationFlag.MONOCHROME)
            elif monochrome and masked:  # If both are true
                active_flags.append(IconGenerationFlag.MONOCHROME)

            if darkmode:
                active_flags.append(IconGenerationFlag.DARKMODE)
            if tinted:
                active_flags.append(IconGenerationFlag.TINTED)
            if macos:
                active_flags.append(IconGenerationFlag.MACOS)
            if ms_tiles:
                active_flags.append(IconGenerationFlag.MS_TILES)
            if html:
                active_flags.append(IconGenerationFlag.HTML)
            if manifest:
                active_flags.append(IconGenerationFlag.MANIFEST)

        # Remove duplicates just in case
        active_flags = sorted(set(active_flags), key=lambda f: f.value)

        active_configs: list[IconGenerationConfig] = [
            get_flag_config(flag) for flag in active_flags
        ]

        # 6. Instantiate Context
        context = IconGenerationContext(
            mad_model=mad_model,
            source_images=source_images,
            output_paths=output_paths,
            active_configs=active_configs,
            html_destination=html_destination,
            destination_dir=destination_dir,
            icon_name_prefix=prefix,
            generate_html=html,
            generate_manifest=manifest,
        )

        # --- Refactored Main Loop ---
        typer.echo("Generating icon sets...")
        for config in context.active_configs:
            # Use .get() for safe access to TypedDict keys
            if not config.get("is_icon_flag", False):  # Default to False if key missing
                typer.echo(f"Skipping non-icon task: {config.get("name", "Unknown Task")}")
                continue

            typer.echo(f"--- Generating {config.get("name", "Unknown Category")} Icons ---")
            try:
                # TODO: Refactor process_icon_category to accept context and config
                # For now, adapt the call signature or pass necessary parts
                # Assuming process_icon_category will be refactored to:
                # process_icon_category(context: IconGenerationContext, config: IconGenerationConfig)
                html_tags, manifest_icons = process_icon_category(
                    context=context,  # Pass context
                    config=config,  # Pass specific config for this category
                    # Remove old args: category_config, mad_model, source_data, source_type, output_paths, cli_config
                )
                # Aggregate results
                all_html_tags.extend(html_tags)
                all_manifest_icons.extend(manifest_icons)
            except Exception as e:
                # Log error and continue with the next category
                typer.echo(
                    f"  Error processing category '{config.get("name", "Unknown Category")}': {e}",
                    err=True,
                )
                # Optionally re-raise if errors should halt the whole process

        # 7. Generate Output Metadata Files
        # TODO: Refactor generate_output_files to accept context
        generate_output_files(all_html_tags, all_manifest_icons, context)  # Pass context

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
        # TODO: Refactor cleanup_resources to accept explicit file args
        # Need to track which files were opened (base_icon, masked_icon etc.)
        files_to_close = [
            f
            for f in [
                base_icon,
                masked_icon,
                masked_monochrome_icon,
                apple_darkmode_icon,
                apple_tinted_icon,
                tile_rectangle_icon,
                json_path,  # Include json_path if it was opened
            ]
            if f is not None
        ]
        cleanup_resources(files_to_close, opened_json_file)  # Pass list of files


if __name__ == "__main__":
    app()

__all__ = ["generate_icons"]
