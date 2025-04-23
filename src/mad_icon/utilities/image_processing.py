# src/mad_icon/utilities/image_processing.py
"""
(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).

Image processing utilities for generating icons.
"""

import base64
import io

from typing import Any, cast

import cairosvg
import typer

from lxml import etree  # type: ignore[import]
from PIL import Image, ImageOps


type ColorType = str | tuple[int, int, int] | tuple[int, int, int, int]


# --- Constants for macOS Clipping ---
# Derived from analyzing template SVGs (e.g., 100/1024, 824/1024, 184/1024)
MACOS_CLIP_OFFSET_RATIO = 0.09765625  # Approximately 100 / 1024
MACOS_CLIP_SIZE_RATIO = 0.8046875  # Approximately 824 / 1024
MACOS_CLIP_RADIUS_RATIO = 0.1796875  # Approximately 184 / 1024


def load_image(image_path_or_buffer: io.BytesIO) -> Image.Image:
    """Loads an image (SVG or raster) into a Pillow Image object."""
    # Placeholder: Need to handle SVG vs Raster loading
    # If SVG, render first then load? Or handle differently?
    # For now, assume raster for Pillow
    try:
        img = Image.open(image_path_or_buffer)
        # Ensure image is in RGBA format for consistency
        # Ensure image is in RGBA format for consistency, return directly if already RGBA
        # Ensure image is in RGBA format for consistency (Sourcery suggestion)
        return img if img.mode == "RGBA" else img.convert("RGBA")
    except Exception as e:
        # TODO: Add specific error handling for file not found, invalid format etc.
        print(f"Error loading image: {e}")
        # sourcery skip: raise-specific-error
        raise typer.Exit(1) from e


def render_svg_to_png_bytes(svg_data: bytes | str, width: int, height: int) -> bytes:
    """Renders SVG data to PNG bytes at a specific size."""
    try:
        # Type hint for cairosvg.svg2png is basic, result is bytes
        # Use ignore for the untyped call and cast the result explicitly
        png_bytes_result = cairosvg.svg2png(  # type: ignore[no-untyped-call]
            bytestring=svg_data.encode("utf-8") if isinstance(svg_data, str) else svg_data,
            output_width=width,
            output_height=height,
        )
        return cast("bytes", png_bytes_result)  # Add quotes to cast type
    except Exception as e:
        # TODO: Add specific error handling for cairosvg errors
        print(f"Error rendering SVG: {e}")
        raise


def resize_image(image: Image.Image, width: int, height: int) -> Image.Image:
    """Resizes a Pillow Image object."""
    try:
        return image.resize((width, height), Image.Resampling.LANCZOS) # type: ignore
    except Exception as e:
        # TODO: Add specific error handling
        print(f"Error resizing image: {e}")
        raise


def desaturate_image(image: Image.Image) -> Image.Image:
    """Converts a Pillow Image object to grayscale."""
    try:
        return ImageOps.grayscale(image).convert("RGBA")  # Keep alpha channel
    except Exception as e:
        # TODO: Add specific error handling
        print(f"Error desaturating image: {e}")
        raise


def ensure_opaque_background(
    image: Image.Image, background_color: str | tuple[int, int, int] = "white"
) -> Image.Image:
    """Ensures an image has an opaque background, converting RGBA to RGB."""
    try:
        if image.mode == "RGB":
            return image  # Already opaque RGB
        # Remove unnecessary elif after return (Ruff)
        if image.mode == "RGBA":
            # Convert RGBA to RGB using the specified background color
            return _convert_rgba_to_rgb_with_background(image, background_color)
        # Handle other modes (like P, L) by converting to RGBA first, then to RGB
        rgba_image = image.convert("RGBA")
        return _convert_rgba_to_rgb_with_background(rgba_image, background_color)
    except Exception as e:
        # TODO: Add specific error handling for Pillow conversions
        print(f"Error ensuring opaque background: {e}")
        raise


def _convert_rgba_to_rgb_with_background(
    image: Image.Image, background_color: ColorType
) -> Image.Image:
    """Helper to composite an RGBA image onto a background and return RGB."""
    if image.mode != "RGBA":
        # Ensure input is RGBA before proceeding
        image = image.convert("RGBA")

    # Create a background image of the target color, matching the original size
    # Ensure background is created in RGBA mode initially for proper pasting
    background = Image.new("RGBA", image.size, background_color)

    # Paste the original image onto the background using its alpha channel as a mask
    # The alpha channel is the 4th channel (index 3)
    try:
        alpha_channel = image.split()[3]
        background.paste(image, (0, 0), mask=alpha_channel)
    except IndexError:
        # Handle cases where split() might not return 4 channels (though unlikely for RGBA)
        # Fallback: paste without mask if alpha isn't available as expected
        background.paste(image, (0, 0))

    # Convert the final composited image to RGB mode
    return background.convert("RGB")


def ensure_transparent_background(image: Image.Image) -> Image.Image:
    """Ensures an image has a transparent background (if possible)."""
    # This is tricky without knowing what *should* be transparent.
    # For SVG analysis, transparency is handled by modifying the SVG structure.
    # For raster, this function might just ensure the mode is RGBA.
    # A more advanced version could try color keying, but that's unreliable.
    try:
        return image.convert("RGBA") if image.mode != "RGBA" else image
    except Exception as e:
        # TODO: Add specific error handling
        print(f"Error ensuring transparent background: {e}")
        raise


def check_masked_padding(image: Image.Image, border_ratio: float = 0.2) -> bool:
    """
    Heuristically checks if there's significant non-transparent content
    within the border area defined by border_ratio.
    Returns True if potential padding issues are detected, False otherwise.
    """
    # TODO: Placeholder for heuristic check logic
    # Example: Check average alpha in border regions
    # This needs careful implementation to be useful
    print("Warning: Masked padding check not yet implemented.")
    return False


def analyze_svg_structure(svg_data: bytes | str) -> dict[str, Any]:
    """
    Analyzes SVG structure to identify potential background/foreground elements.
    Returns a dictionary with analysis results (e.g., {'background_found': True}).
    """
    # TODO: Placeholder for SVG analysis logic using lxml
    print("Warning: SVG structure analysis not yet implemented.")
    return {"background_found": False}


def create_macos_clipped_svg(
    content_svg_data: bytes | str | None,
    content_raster_image: Image.Image | None,
    target_width: int,
    target_height: int,
) -> str:
    """
    Creates an SVG string with the macOS clipping mask applied to the input content
    using lxml for robust SVG construction.
    Input content can be either SVG data or a Pillow Image object.
    """
    if not content_svg_data and not content_raster_image:
        raise ValueError("Either SVG data or a raster image must be provided.")
    if target_width != target_height:
        # macOS icons are square
        raise ValueError("Target width and height must be equal for macOS icons.")

    size = target_width  # Use width as the base size

    # Calculate clip path dimensions
    offset = size * MACOS_CLIP_OFFSET_RATIO
    rect_size = size * MACOS_CLIP_SIZE_RATIO
    radius = size * MACOS_CLIP_RADIUS_RATIO

    # Define namespaces
    NSMAP = {None: "http://www.w3.org/2000/svg", "xlink": "http://www.w3.org/1999/xlink"}

    # Create SVG root element
    svg_root = etree.Element(  # type: ignore[attr-defined]
        "svg", width=str(size), height=str(size), viewBox=f"0 0 {size} {size}", nsmap=NSMAP
    )

    # Create defs section
    defs = etree.SubElement(svg_root, "defs")  # type: ignore[attr-defined]

    # Create clipPath
    clip_path_id = "macosIconMask"
    clip_path = etree.SubElement(defs, "clipPath", id=clip_path_id)  # type: ignore[attr-defined]

    # Create rect for clipPath
    etree.SubElement(  # type: ignore[attr-defined]
        clip_path,
        "rect",
        x=str(offset),
        y=str(offset),
        width=str(rect_size),
        height=str(rect_size),
        rx=str(radius),
    )

    # Create main group with clip-path applied
    group = etree.SubElement(svg_root, "g", attrib={"clip-path": f"url(#{clip_path_id})"})  # type: ignore[attr-defined]

    # Embed content
    if content_raster_image:
        # Embed raster image as base64 data URI
        buffer = io.BytesIO()
        content_raster_image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        etree.SubElement(  # type: ignore[attr-defined]
            group,
            "image",
            href=f"data:image/png;base64,{img_str}",
            x="0",
            y="0",
            width=str(size),
            height=str(size),
        )
    elif content_svg_data:
        # Embed SVG content
        try:
            # Ensure content_svg_data is bytes for parsing
            svg_bytes = (
                content_svg_data.encode("utf-8")
                if isinstance(content_svg_data, str)
                else content_svg_data
            )
            # Parse the input SVG content, recovering from errors
            parser: Any = etree.XMLParser(recover=True, remove_blank_text=True)  # type: ignore[attr-defined]
            content_root: Any = etree.fromstring(svg_bytes, parser=parser)  # type: ignore[attr-defined]

            # --- SVG Content Embedding Logic ---
            # Check if the content root is an <svg> element
            if content_root.tag == etree.QName(NSMAP[None], "svg"):  # type: ignore[attr-defined]
                # If it's an SVG, append its children directly to the group
                # This preserves internal structures like <defs>, <style>, etc.
                # We might need to adjust viewBox/transforms later if needed.
                for child in content_root:  # type: ignore[attr-defined]
                    group.append(child)  # Append children directly # type: ignore[attr-defined]
            else:
                # If the root is not <svg> (e.g., just a <g> or shapes), append it directly
                group.append(content_root)  # type: ignore[attr-defined]

            # TODO: Add more sophisticated handling for viewBox, width/height mismatches
            # between the container and the embedded SVG if necessary.

        except etree.XMLSyntaxError as e:  # type: ignore[attr-defined]
            print(
                f"Warning: Could not parse input SVG content for clipping due to XML syntax error: {e}. Adding placeholder."
            )
            etree.SubElement(  # type: ignore[attr-defined]
                group, "rect", x="0", y="0", width=str(size), height=str(size), fill="red"
            ).text = "<!-- Error parsing input SVG -->"
        except Exception as e:
            print(
                f"Warning: Could not process input SVG content for clipping: {e}. Adding placeholder."
            )
            etree.SubElement(  # type: ignore[attr-defined]
                group, "rect", x="0", y="0", width=str(size), height=str(size), fill="red"
            ).text = "<!-- Error processing input SVG -->"

    # Serialize the lxml tree to a string
    # Use pretty_print for readability, remove in production if size matters
    svg_output = etree.tostring(svg_root, encoding="unicode", pretty_print=True)  # type: ignore[attr-defined]
    return cast("str", svg_output)  # Cast for type checker


# --- Helper for base64 encoding if needed ---
# Moved import base64 to the top


__all__ = [
    "analyze_svg_structure",
    "check_masked_padding",
    "create_macos_clipped_svg",
    "desaturate_image",
    "ensure_opaque_background",
    "ensure_transparent_background",
    "load_image",
    "render_svg_to_png_bytes",
    "resize_image",
]
