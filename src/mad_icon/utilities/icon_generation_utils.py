# src/mad_icon/_generate_icons_helpers.py
# sourcery skip: avoid-global-variables
"""
`icon_generation_utils` module.
Provides utility functions for icon generation in the PWA icon generator. Handles most of the heavy lifting, while the main script handles the pipeline.

(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).
"""

import io
import json

from collections.abc import Sequence
from pathlib import Path
from typing import Any, TypeGuard, cast

import typer

from PIL import Image

from mad_icon.models import MadIconModel, Resolution, get_pwa_model
from mad_icon.types import IconGenerationConfig, IconGenerationFlag, get_flag_config
from mad_icon.utilities import (
    analyze_svg_structure,
    check_masked_padding,
    create_macos_clipped_svg,
    desaturate_image,
    ensure_opaque_background,
    ensure_transparent_background,
    load_file,
    make_dirs,
    render_svg_to_png_bytes,
    resize_image,
    retrieve_model,
)


# Define FileBinaryRead for type hinting if not directly available
# (Typer often uses this internally, but explicit definition might be needed)
FileBinaryRead = typer.FileBinaryRead


def handle_no_icons(kwargs: dict[str, Any], no_icons_present: bool = True) -> dict[str, Any]:  # noqa: FBT001
    """
    Handle the case where the `no_icons` flag is set in the configuration. We need to determine if any other flags are explicitly set that would override part of the no_icons flag.
    """
    if no_icons_present:
        icons_to_generate = any(
            v
            for k, v in kwargs.items()
            if isinstance(v, bool) and k not in ["no_icons", "html", "manifest"]
        )
        if not icons_to_generate:
            kwargs = {
                k: v for k, v in kwargs.items() if "icon" not in k or k != "attempt_svg_analysis"
            }
            kwargs["no_icons"] = True
            kwargs["icons_to_generate"] = False
        else:
            kwargs["icons_to_generate"] = True
    return kwargs


def get_flag_configs(kwargs: dict[str, Any]) -> dict[str, IconGenerationConfig]:
    """
    Get the flag configurations for icon generation.

    Args:
        icon: The icon object from the PWA model.
        kwargs: The keyword arguments containing the flags.

    Returns:
        A dictionary mapping flag names to their configurations.
    """
    for key, value in kwargs.items():
        if not value and not isinstance(value, bool):
            kwargs.pop(key)
            continue
        if value and isinstance(value, bool) and key != "attempt_svg_analysis":
            config = get_flag_config(IconGenerationFlag.from_string(key))
            kwargs[key] = config
    return kwargs


def process_imaginary_icon_kwargs(kwargs: dict[str, Any]) -> None:
    pass  # TODO: Placeholder for the actual implementation


def process_icon_kwargs(kwargs: dict[str, Any]):
    """
    Process the keyword arguments for icon generation.
    """
    if no_icons_present := kwargs.pop("no_icons", False):
        kwargs = handle_no_icons(kwargs, no_icons_present)
    else:
        kwargs["icons_to_generate"] = True
    kwargs = get_flag_configs(kwargs)
    if not kwargs.get("icons_to_generate"):
        process_imaginary_icon_kwargs(kwargs)
        raise typer.Exit


def get_image_from_buffer(image_buffer: io.BytesIO, formatted_size: str = "") -> Image.Image:
    """
    Load an image from a buffer and return a PIL Image object.
    """
    try:
        image_buffer.seek(0)  # Reset buffer position
        return Image.open(image_buffer)
    except OSError as e:
        raise ValueError(f"Error loading image for size {formatted_size} from buffer: {e}") from e


def prepare_output_directories(config: dict[str, Any]) -> dict[str, Path]:
    """
    Creates the main destination directory and all necessary subdirectories
    based on the generation flags. Ensures the HTML/Manifest destination exists.

    Args:
        config: A configuration dictionary containing `destination_dir`,
                `icon_dir_name`, `html_destination`, and all `generate_*`
                boolean flags.

    Returns:
        A dictionary mapping logical names (e.g., "base_icon_path",
        "masked_path", "html_dest_path") to the corresponding Path objects.

    Raises:
        typer.Exit: If directories cannot be created.
    """
    typer.echo("Ensuring output directories exist...")
    destination_dir = config["destination_dir"]
    icon_dir_name = config["icon_dir_name"]
    html_destination = config["html_destination"]

    dirs_to_create: list[Path] = [destination_dir]
    output_paths: dict[str, Path] = {
        "destination_dir": destination_dir,
        "html_dest_path": html_destination,
    }

    base_icon_path = destination_dir / icon_dir_name
    dirs_to_create.append(base_icon_path)
    output_paths["base_icon_path"] = base_icon_path

    if config.get("generate_masked_icons"):
        masked_path = base_icon_path / "masked"
        monochrome_path = masked_path / "monochrome"
        dirs_to_create.extend([masked_path, monochrome_path])
        output_paths["masked_path"] = masked_path
        output_paths["monochrome_path"] = monochrome_path
    if config.get("generate_darkmode_icons"):
        darkmode_path = base_icon_path / "darkmode"
        dirs_to_create.append(darkmode_path)
        output_paths["darkmode_path"] = darkmode_path
    if config.get("generate_tinted_icons"):
        tinted_path = base_icon_path / "tinted"
        dirs_to_create.append(tinted_path)
        output_paths["tinted_path"] = tinted_path
    if config.get("generate_macos_icons"):
        macos_path = base_icon_path / "macos"
        dirs_to_create.append(macos_path)
        output_paths["macos_path"] = macos_path
    if config.get("generate_ms_tiles"):
        mstile_path = base_icon_path / "mstile"
        dirs_to_create.append(mstile_path)
        output_paths["mstile_path"] = mstile_path

    if (
        config.get("generate_html") or config.get("generate_manifest")
    ) and html_destination not in dirs_to_create:
        dirs_to_create.append(html_destination)

    try:
        make_dirs(dirs_to_create)
        typer.echo("Output directories ensured.")
    except OSError as e:
        typer.echo(f"Error creating output directories: {e}", err=True)
        raise typer.Exit(code=1) from e
    else:
        return output_paths

def load_icon_image(icon_image_arg: FileBinaryRead) -> tuple[bytes, str, str, "Image.Image | None"]:
    """
    Load the icon image and determine its type.

    Args:
        icon_image_arg: The icon image file argument.

    Returns:
        A tuple of (image_data, image_name, image_type, pil_image).
        image_type is 'svg' or 'raster'.
        pil_image is None for SVG images.

    Raises:
        typer.Exit: If the image cannot be loaded.
    """
    try:
        image_name = icon_image_arg.name
        image_data = icon_image_arg.read()
        image_ext = Path(image_name).suffix.lower()

        is_svg = image_ext == ".svg"
        pil_image = None

        if is_svg:
            image_type = "svg"
            typer.echo(f"Input icon is SVG: {image_name}")
            # Further SVG validation could be added here if needed
        else:
            image_type = "raster"
            # Load raster image with Pillow
            pil_image = get_image_from_buffer(io.BytesIO(image_data))
            width, height = pil_image.size
            typer.echo(f"Input icon is Raster ({width}x{height}): {image_name}")
    except Exception as e:
        typer.echo(
            f"Error loading input icon '{getattr(icon_image_arg, 'name', 'unknown')}': {e}",
            err=True,
        )
        raise typer.Exit(code=1) from e
    else:
        return image_data, image_name, image_type, pil_image


def validate_raster_image(image: "Image.Image", image_name: str) -> None:
    """
    Validate raster image properties (size and aspect ratio).

    Args:
        image: The PIL Image to validate.
        image_name: The name of the image for error messages.
    """
    width, height = image.size

    # Check dimensions for raster
    min_size = 1024  # As per README/docs
    if width < min_size or height < min_size:
        typer.echo(
            f"Warning: Raster input image '{image_name}' is smaller than the recommended {min_size}x{min_size} pixels.",
            err=True,
        )
        # Consider if this should be a hard error: raise typer.Exit(code=1)

    # Check aspect ratio (should be square)
    if abs(width - height) > 1:  # Allow 1px tolerance
        typer.echo(
            f"Warning: Input image '{image_name}' is not square ({width}x{height}). Results may be distorted.",
            err=True,
        )
        # Consider if this should be a hard error


def get_masked_image_data(
    masked_image_arg: FileBinaryRead | None,
    fallback_data: bytes,
    fallback_name: str,
    fallback_type: str,
) -> tuple[bytes | None, str, bool]:
    """
    Get the masked image data, falling back to the base icon if needed.

    Args:
        masked_image_arg: The masked image file argument, if provided.
        fallback_data: The fallback image data (usually the base icon).
        fallback_name: The fallback image name.
        fallback_type: The fallback image type ('svg' or 'raster').

    Returns:
        A tuple of (image_data, image_name, is_svg).
    """
    if masked_image_arg:
        try:
            image_name = masked_image_arg.name
            image_data = masked_image_arg.read()
            is_svg = Path(image_name).suffix.lower() == ".svg"
        except Exception as e:
            typer.echo(
                f"Warning: Could not read provided masked image '{masked_image_arg.name}' for padding check: {e}",
                err=True,
            )
        else:
            return image_data, image_name, is_svg

        # Fall back to base icon

    # Use fallback (base icon)
    return fallback_data, fallback_name, fallback_type == "svg"


def check_masked_image_padding(image_data: bytes | None, image_name: str, *, is_svg: bool) -> None:
    """
    Check if a masked image has appropriate padding.

    Args:
        image_data: The image data to check.
        image_name: The name of the image for error messages.
        is_svg: Whether the image is an SVG.
    """
    if not image_data:
        typer.echo(
            f"Warning: Could not obtain data for masked padding check (source: '{image_name or 'Fallback'}').",
            err=True,
        )
        return

    try:
        if not is_svg:
            padding_pil = get_image_from_buffer(io.BytesIO(image_data))
            if check_masked_padding(padding_pil):
                typer.echo(
                    f"Warning: Potential padding issue detected in '{image_name}' used for masked icons. "
                    f"Ensure important content is within the central 80% (20% margin). See docs.",
                    err=True,
                )
        else:
            typer.echo(
                f"Info: Skipping masked padding check for SVG input '{image_name}'. "
                f"Please ensure SVG content respects safe zones."
            )
    except Exception as e:
        typer.echo(
            f"Warning: Could not perform masked padding check on '{image_name}': {e}", err=True
        )


def validate_and_load_base_icon(
    icon_image_arg: FileBinaryRead,
    masked_image_arg: FileBinaryRead | None,
    *,
    generate_masked_icons: bool,
) -> tuple[bytes, str, str]:
    """
    Validates the primary icon_image argument, loads its content, determines type,
    validates raster properties, and performs masked padding check if needed.

    Args:
        icon_image_arg: The `icon_image` CLI argument (typer.FileBinaryRead).
        masked_image_arg: The `masked_image` CLI argument (typer.FileBinaryRead | None).
        generate_masked_icons: Boolean flag indicating if masked icons are generated.

    Returns:
        A tuple: (icon_image_data: bytes, icon_image_name: str, icon_image_type: str)
        where type is 'svg' or 'raster'.

    Raises:
        typer.Exit: On critical validation errors (missing file, load error, invalid raster).
    """
    typer.echo("Validating inputs...")

    # 1. Check required icon_image
    if not icon_image_arg:
        typer.echo("Error: Input icon image is required (--icon-image).", err=True)
        raise typer.Exit(code=1)

    # 2. Load and validate base icon
    icon_image_data, icon_image_name, icon_image_type, pil_image = load_icon_image(icon_image_arg)

    # 3. Validate raster properties if applicable
    if icon_image_type == "raster" and pil_image:
        validate_raster_image(pil_image, icon_image_name)

    # 4. Masked Padding Check (if needed)
    if generate_masked_icons:
        # Get masked image data (or fall back to base icon)
        masked_data, masked_name, is_masked_svg = get_masked_image_data(
            masked_image_arg, icon_image_data, icon_image_name, icon_image_type
        )

        # Check padding
        check_masked_image_padding(masked_data, masked_name, is_svg=is_masked_svg)

    return icon_image_data, icon_image_name, icon_image_type


def read_source_from_arg(file_arg: Any, category: str) -> tuple[bytes | None, str]:
    """
    Read image data from a CLI argument and determine its type.

    Args:
        file_arg: The file argument from CLI (FileBinaryRead).
        category: The category name for logging purposes.

    Returns:
        A tuple of (image_data, image_type) where image_type is 'svg' or 'raster'.
    """
    if not (file_arg and isinstance(file_arg, io.IOBase) and not file_arg.closed):
        return None, ""

    # Safely get the filename before the try block
    file_name = getattr(file_arg, "name", "unknown_file")
    try:
        # Read data into memory. Typer should close the file later.
        data = file_arg.read()
        image_type = "svg" if Path(file_name).suffix.lower() == ".svg" else "raster"
        typer.echo(f"  Using provided '{file_name}' for {category} icons.")
    except Exception as e:
        # Use the safely retrieved filename in the error message too
        typer.echo(
            f"Warning: Could not read provided {category} image '{file_name}': {e}", err=True
        )
        return None, ""
    else:
        return data, image_type


def get_source_images_from_args(
    cli_args: dict[str, Any], source_data: dict[str, bytes | None], source_type: dict[str, str]
) -> None:
    """
    Extract source images from CLI arguments and populate source dictionaries.

    Args:
        cli_args: Dictionary containing all relevant CLI arguments.
        source_data: Dictionary to populate with image data.
        source_type: Dictionary to populate with image types.
    """
    # Map of CLI argument keys to category names
    arg_to_category = {
        "masked_image": "masked",
        "masked_image_monochrome": "monochrome",
        "darkmode_image": "dark",
        "tinted_image": "tinted",
        "tile_rectangle_image": "tile_rect",
    }

    # Get explicit sources if provided
    for arg_key, category in arg_to_category.items():
        file_arg = cli_args.get(arg_key)
        data, image_type = read_source_from_arg(file_arg, category)
        if data:
            source_data[category] = data
            source_type[category] = image_type


def perform_svg_analysis(
    cli_args: dict[str, Any], source_data: dict[str, bytes | None], source_type: dict[str, str]
) -> None:
    """
    Perform experimental SVG analysis if enabled.

    Args:
        cli_args: Dictionary containing CLI arguments.
        source_data: Dictionary containing image data.
        source_type: Dictionary containing image types.
    """
    if not cli_args.get("attempt_svg_analysis"):
        return

    typer.echo("  Info: [Experimental] Attempting SVG analysis...")

    # Analyze dark mode SVG
    if source_type["dark"] == "svg" and source_data["dark"]:
        try:
            analysis_result = analyze_svg_structure(source_data["dark"])
            if analysis_result.get("background_found"):
                typer.echo(
                    "  Info: SVG analysis suggests background found for dark mode. (Modification logic TBD)"
                )
                # TODO: Implement SVG modification logic here if analysis is successful
        except Exception as e:
            typer.echo(f"  Warning: SVG analysis for dark mode failed: {e}", err=True)

    # Analyze tinted mode SVG
    if source_type["tinted"] == "svg" and source_data["tinted"]:
        try:
            analysis_result = analyze_svg_structure(source_data["tinted"])
            if analysis_result.get("background_found"):
                typer.echo(
                    "  Info: SVG analysis suggests background found for tinted mode. (Modification logic TBD)"
                )
                # TODO: Implement SVG modification logic here
        except Exception as e:
            typer.echo(f"  Warning: SVG analysis for tinted mode failed: {e}", err=True)


def determine_source_images(
    cli_args: dict[str, Any], base_icon_data: bytes, base_icon_type: str
) -> tuple[dict[str, bytes | None], dict[str, str]]:
    """
    Determines the definitive source image data (bytes) and type ('svg'/'raster')
    for each icon category by applying fallback logic and reading optional inputs.

    Args:
        cli_args: Dictionary containing all relevant CLI arguments (FileBinaryRead, flags).
        base_icon_data: The loaded bytes of the primary icon image.
        base_icon_type: The type ('svg' or 'raster') of the primary icon image.

    Returns:
        A tuple of two dictionaries:
        - source_data: Mapping category key (e.g., "masked") to bytes or None.
        - source_type: Mapping category key to 'svg'/'raster' or empty string.
    """
    typer.echo("Determining source images...")

    # Initialize source data and type dictionaries
    source_data: dict[str, bytes | None] = {
        "base": base_icon_data,
        "masked": None,
        "monochrome": None,
        "dark": None,
        "tinted": None,
        "tile_rect": None,
    }
    source_type: dict[str, str] = {
        "base": base_icon_type,
        "masked": "",
        "monochrome": "",
        "dark": "",
        "tinted": "",
        "tile_rect": "",
    }

    # Step 1: Extract source images from CLI arguments
    get_source_images_from_args(cli_args, source_data, source_type)

    # Step 2: Apply fallback logic for missing sources
    # TODO: Use fallback logic from model

    # Step 3: Perform experimental SVG analysis if enabled
    perform_svg_analysis(cli_args, source_data, source_type)

    # Note: Typer is responsible for closing the FileBinaryRead arguments
    typer.echo("Source image determination complete.")
    return source_data, source_type


def sequence_or_string_guard(
    value: Any, attr: str = ""
) -> TypeGuard[Sequence[int | tuple[int, int]] | str]:
    """
    Validate that the given value is a sequence or a string.

    Raises:
        TypeError: If the value is not a sequence or a string.
    """
    # Validate the retrieved value is a sequence
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise TypeError(
            f"Expected a sequence for model attribute '{attr or 'unknown'}', got {type(value).__name__}"
        )
    return True


def get_target_sizes(
    pwa_model: MadIconModel, model_attr: str, cat_name: str
) -> list[tuple[int, int]] | None:
    """
    Extract target sizes from the PWA model for a specific category.

    Args:
        pwa_model: The loaded PWA data model.
        model_attr: The attribute path to access sizes in the model.
        cat_name: The category name for logging purposes.

    Returns:
        A list of (width, height) tuples or None if sizes cannot be determined.
    """
    try:
        # Navigate to the specified attribute in the model
        sizes_or_resolutions = pwa_model
        for attr in model_attr.split("."):
            sizes_or_resolutions = getattr(sizes_or_resolutions, attr)

        sequence_or_string_guard(sizes_or_resolutions, model_attr)

        # Check if the sequence is empty
        if not sizes_or_resolutions:
            typer.echo(
                f"  Info: No sizes defined for {cat_name} in model attribute '{model_attr}'. Skipping.",
                err=False,
            )
            return None

        # Cast to the expected type for type checking
        typed_sizes_or_resolutions = cast(
            "Sequence[int | tuple[int, int] | Resolution]", sizes_or_resolutions
        )

        # Convert all size formats to (width, height) tuples
        target_sizes: list[tuple[int, int]] = []
        for item in typed_sizes_or_resolutions:
            if isinstance(item, tuple) and len(item) == 2:
                target_sizes.append(item)  # item is tuple[int, int]
            elif isinstance(item, Resolution):
                target_sizes.append((item.width, item.height))  # item is Resolution
            else:
                # Handle the integer case (square dimensions)
                target_sizes.append((item, item))  # item is int

        # Check if we successfully extracted any sizes
        if not target_sizes:
            typer.echo(
                f"  Warning: No valid sizes could be processed for {cat_name} from model attribute '{model_attr}'. Skipping.",
                err=True,
            )
            return None
    except (AttributeError, TypeError, ValueError) as e:
        typer.echo(
            f"  Warning: Error retrieving/processing sizes for {cat_name} from model attribute '{model_attr}': {e}. Skipping category.",
            err=True,
        )
        return None
    else:
        return target_sizes


def has_value(value: Any) -> bool:
    """Validate that the value is not None or empty."""
    if value:
        return True
    raise ValueError(f"Expected a value, got {value}")


def process_macos_clipped_icon(
    source_data: bytes, source_type: str | None, width: int, height: int, size_formatted: str
) -> Image.Image | None:
    """
    Process an icon with macOS clipping applied.

    Args:
        source_data: The source image data.
        source_type: The type of source image ('svg' or 'raster'), or None.
        width: The target width.
        height: The target height.
        size_formatted: Formatted size string for error messages.

    Returns:
        A processed PIL Image or None if processing failed.
    """
    try:
        temp_svg: str | None = None

        # Default to raster if source_type is None
        if source_type == "svg":
            svg_data = source_data.decode("utf-8")
            temp_svg = create_macos_clipped_svg(svg_data, None, width, height)
        else:  # Raster source or None
            raster_img = load_file(io.BytesIO(source_data))
            temp_svg = create_macos_clipped_svg(None, raster_img, width, height)

        has_value(temp_svg)
        png_bytes = render_svg_to_png_bytes(temp_svg, width, height)
        return get_image_from_buffer(io.BytesIO(png_bytes), size_formatted)

    except Exception as clip_err:
        typer.echo(
            f"    Error during macOS clipping for size {size_formatted}: {clip_err}", err=True
        )
        return None


def process_svg_icon(
    source_data: bytes, width: int, height: int, size_formatted: str
) -> Image.Image | None:
    """
    Process an SVG icon by rendering it to the target size.

    Args:
        source_data: The SVG source data.
        width: The target width.
        height: The target height.
        size_formatted: Formatted size string for error messages.

    Returns:
        A processed PIL Image or None if processing failed.
    """
    try:
        png_bytes = render_svg_to_png_bytes(source_data, width, height)
        return get_image_from_buffer(io.BytesIO(png_bytes), size_formatted)
    except Exception as render_err:
        typer.echo(f"    Error rendering SVG for size {size_formatted}: {render_err}", err=True)
        return None


def process_raster_icon(
    source_data: bytes, width: int, height: int, size_formatted: str
) -> Image.Image | None:
    """
    Process a raster icon by loading and resizing it if needed.

    Args:
        source_data: The raster source data.
        width: The target width.
        height: The target height.
        size_formatted: Formatted size string for error messages.

    Returns:
        A processed PIL Image or None if processing failed.
    """
    try:
        img = get_image_from_buffer(io.BytesIO(source_data), size_formatted)
        if img.size != (width, height):  # type: ignore
            img = resize_image(img, width, height)  # type: ignore
    except Exception as load_resize_err:
        typer.echo(
            f"    Error loading/resizing raster image for size {size_formatted}: {load_resize_err}",
            err=True,
        )
        return None
    else:
        return img  # type: ignore


def apply_post_processing(
    img: Image.Image, *, needs_desat: bool, needs_opaque: bool, needs_trans: bool
) -> Image.Image:
    """
    Apply post-processing effects to an image.

    Args:
        img: The image to process.
        needs_desat: Whether to desaturate the image.
        needs_opaque: Whether to ensure an opaque background.
        needs_trans: Whether to ensure a transparent background.

    Returns:
        The processed image.
    """
    if needs_desat:
        img = desaturate_image(img)  # type: ignore
    if needs_opaque:
        # TODO: Make background color configurable? Default white.
        img = ensure_opaque_background(img, "white")  # type: ignore
    elif needs_trans:
        img = ensure_transparent_background(img)  # type: ignore
    return img  # type: ignore


def get_relative_path(
    output_path: Path, html_destination: Path, destination_dir_parent: Path
) -> tuple[Path, str | None]:
    """
    Calculate the relative path for an icon file.

    Args:
        output_path: The absolute path to the icon file.
        html_destination: The HTML destination directory.
        destination_dir_parent: The parent of the destination directory.

    Returns:
        A tuple of (relative_path, warning_message or None).
    """
    try:
        relative_path = output_path.relative_to(html_destination)
    except ValueError:
        # Fallback if assets are outside html_destination
        relative_path = output_path.relative_to(destination_dir_parent)
        warning = (
            f"    Warning: Icon '{output_path.name}' is outside HTML destination "
            f"'{html_destination}'. Using path relative to assets parent: '{relative_path}'"
        )
        return relative_path, warning
    else:
        return relative_path, None


def generate_html_tag(
    cat_name: str, size_fmt: str, relative_path: Path, width: int, height: int
) -> str | None:
    """
    Generate an HTML tag for an icon.

    Args:
        cat_name: The category name.
        size_fmt: The formatted size string.
        relative_path: The relative path to the icon.
        width: The icon width.
        height: The icon height.

    Returns:
        An HTML tag string or None if no tag should be generated.
    """
    if cat_name == "Apple Touch":
        return f'<link rel="apple-touch-icon" sizes="{size_fmt}" href="{relative_path}">'
    if cat_name == "Apple Dark Mode":
        return f'<link rel="apple-touch-icon" sizes="{size_fmt}" href="{relative_path}" media="(prefers-color-scheme: dark)">'
    if cat_name.startswith("MS Tile"):
        meta_name = "msapplication-square" if width == height else "msapplication-wide"
        meta_size = f"{width}x{height}logo"
        return f'<meta name="{meta_name}{meta_size}" content="{relative_path}">'
    return None


def generate_manifest_entry(
    cat_name: str, relative_path: Path, size_fmt: str, manifest_purp: str
) -> dict[str, Any] | None:
    """
    Generate a manifest entry for an icon.

    Args:
        cat_name: The category name.
        relative_path: The relative path to the icon.
        size_fmt: The formatted size string.
        manifest_purp: The manifest purpose.

    Returns:
        A manifest entry dictionary or None if no entry should be generated.
    """
    if cat_name not in ["Apple Dark Mode", "Apple Touch"]:
        entry = {"src": str(relative_path), "sizes": size_fmt, "type": "image/png"}
        if manifest_purp != "any":
            entry["purpose"] = manifest_purp
        return entry
    return None


def extract_category_params(
    category_config: dict[str, Any],
) -> tuple[str, str, str, str, bool, bool, bool, bool, str]:
    """
    Extract and return the parameters from a category configuration.

    Args:
        category_config: Dict defining the category configuration.

    Returns:
        A tuple containing the extracted parameters:
        (cat_name, src_key, subdir, model_attr, needs_desat, needs_opaque, needs_trans, needs_clip, manifest_purp)
    """
    return (
        category_config["name"],
        category_config["source_key"],
        category_config["subdir"],
        category_config["model_attr"],
        category_config["needs_desat"],
        category_config["needs_opaque"],
        category_config["needs_trans"],
        category_config["needs_clip"],
        category_config["manifest_purp"],
    )


def setup_output_paths(
    base_icon_path: Path,
    subdir: str,
    html_destination: Path,
    destination_dir: Path,
    icon_name: str,
    cat_name: str,
) -> tuple[Path, Path, str]:
    """
    Set up output paths and filename prefix for icon generation.

    Args:
        base_icon_path: The base path for icon output.
        subdir: The subdirectory for this category, if any.
        html_destination: The HTML destination path.
        destination_dir: The main destination directory.
        icon_name: The base name for the icon files.
        cat_name: The category name.

    Returns:
        A tuple of (output_dir, destination_dir_parent, icon_name_prefix).
    """
    # Set up output directory
    output_dir = base_icon_path / subdir if subdir else base_icon_path
    destination_dir_parent = destination_dir.parent

    # Determine filename prefix based on category
    icon_name_prefix = (
        icon_name
        if cat_name == "Apple Touch"
        else f"{icon_name}-{cat_name.lower().replace(' ', '-')}"
    )

    return output_dir, destination_dir_parent, icon_name_prefix


def process_single_icon(
    width: int,
    height: int,
    output_dir: Path,
    icon_name_prefix: str,
    current_source_data: bytes,
    current_source_type: str | None,
    html_destination: Path,
    destination_dir_parent: Path,
    cat_name: str,
    manifest_purp: str,
    *,
    needs_clip: bool,
    needs_desat: bool,
    needs_opaque: bool,
    needs_trans: bool,
) -> tuple[str | None, dict[str, Any] | None]:
    """
    Process a single icon of a specific size.

    Args:
        width: The icon width.
        height: The icon height.
        output_dir: The output directory.
        icon_name_prefix: The prefix for the icon filename.
        current_source_data: The source image data.
        current_source_type: The source image type.
        html_destination: The HTML destination path.
        destination_dir_parent: The parent of the destination directory.
        cat_name: The category name.
        manifest_purp: The manifest purpose.

        needs_clip: Whether the icon needs clipping.
        needs_desat: Whether the icon needs desaturation.
        needs_opaque: Whether the icon needs an opaque background.
        needs_trans: Whether the icon needs a transparent background.

    Returns:
        A tuple of (html_tag, manifest_entry) or (None, None) if processing failed.
    """
    # Construct filename
    size_formatted = f"{width}x{height}"
    base_filename = f"{icon_name_prefix}-{size_formatted}.png"
    output_path = output_dir / base_filename

    typer.echo(f"    Generating {output_path.name}...")

    # Process the image based on type and requirements
    processed_img: Image.Image | None = None

    if needs_clip:  # macOS specific path
        processed_img = process_macos_clipped_icon(
            current_source_data, current_source_type, width, height, size_formatted
        )
    elif current_source_type == "svg":
        processed_img = process_svg_icon(current_source_data, width, height, size_formatted)
    else:  # Raster source
        processed_img = process_raster_icon(current_source_data, width, height, size_formatted)

    # Skip if processing failed
    if not processed_img:
        typer.echo(
            f"    Skipping save/metadata for {output_path.name} due to processing error.", err=True
        )
        return None, None

    try:
        # Apply post-processing effects
        processed_img = apply_post_processing(
            processed_img,
            needs_desat=needs_desat,
            needs_opaque=needs_opaque,
            needs_trans=needs_trans,
        )

        # Save the processed image
        processed_img.save(output_path, "PNG")

        # Get relative path for metadata
        relative_path, warning = get_relative_path(
            output_path, html_destination, destination_dir_parent
        )
        if warning:
            typer.echo(warning, err=True)

        size_fmt = f"{width}x{height}"

        # Generate HTML tag and manifest entry
        html_tag = generate_html_tag(cat_name, size_fmt, relative_path, width, height)
        manifest_entry = generate_manifest_entry(cat_name, relative_path, size_fmt, manifest_purp)

    except Exception as post_process_err:
        typer.echo(
            f"    Error during post-processing/saving/metadata for {output_path.name}: {post_process_err}",
            err=True,
        )
        return None, None
    else:
        return html_tag, manifest_entry


def process_icon_category(
    category_config: dict[str, Any],
    pwa_model: MadIconModel,
    source_data: dict[str, bytes | None],
    source_type: dict[str, str],
    output_paths: dict[str, Path],
    cli_config: dict[str, Any],
) -> tuple[list[str], list[dict[str, Any]]]:
    """
    Generates all icons for a single category based on the provided configuration.

    Handles retrieving sizes, processing images (SVG/raster, clipping, effects),
    saving files, and generating metadata entries.

    Args:
        category_config: Dict defining the category (name, source_key, subdir, etc.).
        pwa_model: The loaded PWA data model.
        source_data: Dict mapping source keys to image data (bytes).
        source_type: Dict mapping source keys to image type ('svg'/'raster').
        output_paths: Dict mapping logical path names to Path objects.
        cli_config: Dict containing general CLI config (icon_name, html_destination, etc.).

    Returns:
        A tuple containing two lists: (html_tags, manifest_icons) for this category.

    Raises:
        ValueError: If required source data is missing or processing fails.
        TypeError: If model data for sizes is incorrect.
        AttributeError: If model attribute path is incorrect.
    """
    # Extract configuration parameters
    (
        cat_name,
        src_key,
        subdir,
        model_attr,
        needs_desat,
        needs_opaque,
        needs_trans,
        needs_clip,
        manifest_purp,
    ) = extract_category_params(category_config)

    html_tags: list[str] = []
    manifest_icons: list[dict[str, Any]] = []

    # Validate source data
    current_source_data = source_data.get(src_key)
    current_source_type = source_type.get(src_key)

    if not current_source_data:
        typer.echo(
            f"  Warning: Source data for '{cat_name}' (key: {src_key}) not found. Skipping category.",
            err=True,
        )
        return html_tags, manifest_icons  # Return empty lists

    # Get target sizes from the model
    target_sizes = get_target_sizes(pwa_model, model_attr, cat_name)
    if not target_sizes:
        return html_tags, manifest_icons  # Return empty lists if no sizes

    # Set up output paths
    icon_name = cli_config.get("icon_name", "icon")  # Default name if not in config
    output_dir, destination_dir_parent, icon_name_prefix = setup_output_paths(
        output_paths["base_icon_path"],
        subdir,
        output_paths["html_dest_path"],
        output_paths["destination_dir"],
        icon_name,
        cat_name,
    )

    # Process each size
    for width, height in target_sizes:
        try:
            html_tag, manifest_entry = process_single_icon(
                width,
                height,
                output_dir,
                icon_name_prefix,
                current_source_data,
                current_source_type,
                output_paths["html_dest_path"],
                destination_dir_parent,
                cat_name,
                manifest_purp,
                needs_clip=needs_clip,
                needs_desat=needs_desat,
                needs_opaque=needs_opaque,
                needs_trans=needs_trans,
            )

            if html_tag:
                html_tags.append(html_tag)
            if manifest_entry:
                manifest_icons.append(manifest_entry)

        except Exception as e:
            # Catch-all for unexpected errors
            typer.echo(
                f"    Unexpected error processing size {width}x{height} for {cat_name}: {e}",
                err=True,
            )
            # Continue to next size

    return html_tags, manifest_icons


def generate_output_files(
    html_tags: list[str],
    manifest_icons: list[dict[str, Any]],
    output_paths: dict[str, Path],
    cli_config: dict[str, Any],
) -> None:
    """
    Writes the aggregated HTML tags and manifest icon entries to output files.

    Args:
        html_tags: List of generated HTML tag strings.
        manifest_icons: List of generated manifest icon dictionaries.
        output_paths: Dictionary mapping logical path names to Path objects.
        cli_config: Dictionary containing CLI config (filenames, generation flags).
    """
    generate_html = cli_config.get("generate_html")
    generate_manifest = cli_config.get("generate_manifest")
    html_destination = output_paths["html_dest_path"]
    html_file_name = cli_config.get("html_file_name", "paste-content-in-site-head-tags.html")
    if generate_html:
        typer.echo("Generating HTML snippet...")
        if html_tags:
            # Sort tags for consistent output (optional, but nice)
            html_tags.sort()
            html_content = "\n".join(f"  {tag}" for tag in html_tags)
            html_output_path = html_destination / html_file_name
            try:
                html_output_path.write_text(
                    f"<!-- PWA Icons Generated by mad-icon -->\n{html_content}\n<!-- End PWA Icons -->",
                    encoding="utf-8",
                )
                typer.echo(f"  HTML snippet saved to: {html_output_path}")
            except OSError as e:
                typer.echo(f"  Error writing HTML file '{html_output_path}': {e}", err=True)
        else:
            typer.echo("  No HTML tags generated.")

    if generate_manifest:
        typer.echo("Generating Manifest fragment...")
        if manifest_icons:
            # Sort manifest icons for consistent output (optional)
            # Sorting by 'src' path is a reasonable default
            manifest_icons.sort(key=lambda x: x.get("src", ""))
            # Consider a different name for manifest fragment if needed
            manifest_file_name = "manifest-icons-fragment.json"

            manifest_output_path = html_destination / manifest_file_name
            try:
                with manifest_output_path.open("w", encoding="utf-8") as f:
                    json.dump(manifest_icons, f, indent=2)
                typer.echo(f"  Manifest icons fragment saved to: {manifest_output_path}")
            except OSError as e:
                typer.echo(
                    f"  Error writing Manifest fragment file '{manifest_output_path}': {e}",
                    err=True,
                )
            except TypeError as e:
                typer.echo(f"  Error serializing manifest icons to JSON: {e}", err=True)
        else:
            typer.echo("  No Manifest icons generated.")


def cleanup_resources(cli_args: dict[str, Any], opened_json_file: io.IOBase | None) -> None:
    """
    Closes all file handles that were passed as Typer arguments or opened internally.

    Args:
        cli_args: Dictionary containing all CLI arguments (including FileBinaryRead).
        opened_json_file: The file handle returned by _load_mad_model (if any).
    """
    typer.echo("Cleaning up resources...")

    # List of keys corresponding to FileBinaryRead arguments in cli_args
    file_arg_keys = [
        "icon_image",
        "masked_image",
        "masked_image_monochrome",
        "darkmode_image",
        "tinted_image",
        "tile_rectangle_image",
        "json_path",  # User-provided JSON path arg
    ]

    for key in file_arg_keys:
        file_arg = cli_args.get(key)
        # Check if it's an IOBase instance and if it's not already closed
        if file_arg and isinstance(file_arg, io.IOBase) and not file_arg.closed:
            try:
                file_arg.close()
                # typer.echo(f"  Closed file argument: {getattr(file_arg, 'name', key)}") # Optional debug echo
            except Exception as e:
                # Log error but don't stop cleanup
                typer.echo(
                    f"  Warning: Error closing file argument '{getattr(file_arg, 'name', key)}': {e}",
                    err=True,
                )

    # Close the file handle returned by _load_mad_model (could be default data or user json)
    # This might be redundant if json_path was provided AND Typer closes it,
    # but ensures closure if retrieve_model opened the default one.
    if opened_json_file and not opened_json_file.closed:
        try:
            opened_json_file.close()
            # typer.echo(f"  Closed PWA model file: {getattr(opened_json_file, 'name', 'default data')}") # Optional debug echo
        except Exception as e:
            typer.echo(
                f"  Warning: Error closing PWA model file '{getattr(opened_json_file, 'name', 'unknown')}': {e}",
                err=True,
            )

    typer.echo("Resource cleanup finished.")


__all__ = [
    "apply_post_processing",
    "check_masked_image_padding",
    "cleanup_resources",
    "determine_source_images",
    "extract_category_params",
    "generate_html_tag",
    "generate_manifest_entry",
    "generate_output_files",
    "get_masked_image_data",
    "get_relative_path",
    "get_source_images_from_args",
    "get_target_sizes",
    "has_value",
    "load_icon_image",
    "perform_svg_analysis",
    "prepare_output_directories",
    "process_icon_category",
    "process_icon_kwargs",
    "process_macos_clipped_icon",
    "process_raster_icon",
    "process_single_icon",
    "process_svg_icon",
    "read_source_from_arg",
    "sequence_or_string_guard",
    "setup_output_paths",
    "validate_and_load_base_icon",
    "validate_raster_image",
]
