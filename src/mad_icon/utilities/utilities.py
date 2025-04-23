"""
`utilities.py` module.

Provides utility functions for the `mad_icon` package.

(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).
"""

import io

from collections import defaultdict
from enum import Enum
from io import BufferedReader
from pathlib import Path
from typing import Any, BinaryIO, TypeGuard

import typer

from pydantic import ValidationError
from typing_extensions import TypeIs

from mad_icon.models import MadIconModel, Resolution, get_pwa_model
from mad_icon.types import NONE_TYPES, EnumType, LogoLaunchScreenCLIParam, NoneType


def load_file(binary_buffer: BinaryIO | typer.FileBinaryRead | Path) -> io.BytesIO:
    """
    Copy bytes from a buffer and close it after reading.
    """
    try:
        if isinstance(binary_buffer, Path):
            binary_buffer = binary_buffer.open("rb")
        file_data = binary_buffer.read()
        binary_buffer.close()
        return io.BytesIO(file_data)
    except OSError as e:
        print(f"Error: Could not open file {binary_buffer}.")
        raise typer.Exit(code=1) from e
    finally:
        if isinstance(binary_buffer, BufferedReader):
            binary_buffer.close()


def is_none_type(value: Any) -> TypeIs[NoneType]:
    """Checks if the value is a None type."""
    type_: type = type(value)
    for none_type in NONE_TYPES:
        return type_ is none_type
    return False


def has_value(value: Any) -> TypeGuard[object]:
    """Verifies the value is Truthy, not NoneType, and not boolean (including True)."""
    return not is_none_type(value) and value and not isinstance(value, bool)


def is_enum_member(value: str, enum_class: Enum) -> TypeGuard[EnumType]:  # type: ignore
    """Checks if the value is a member of the given enum class."""
    try:
        return value in enum_class.__members__.values() or value.upper() in enum_class.__members__  # type: ignore
    except AttributeError as e:
        raise ValueError(f"Invalid enum class: {enum_class}") from e
    except TypeError as e:
        raise ValueError(f"Invalid value: {value}") from e
    except KeyError as e:
        raise ValueError(f"Invalid enum member: {value}") from e


def flag_to_enum(flag: tuple[str, bool], enum_class: EnumType) -> EnumType:  # type: ignore # noqa: RET503  # it will raise an error if not a member
    """Converts a flag tuple to an enum class."""
    if is_enum_member(flag[0], enum_class):
        return enum_class.__members__[flag[0].upper()]  # type: ignore


def process_models(
    model: MadIconModel, *, process_launch_screens: bool = True, process_icons: bool = True
) -> defaultdict[str, list[Resolution]]:
    """Processes the PWA models and generates the necessary files."""
    data = defaultdict[str, list[Resolution]](list)
    if process_launch_screens:
        devices = model.apple.devices
        data["launch_screens"] = list({res.actual_resolution for res in devices})
    if process_icons:
        data["touch_icon_sizes"] = model.apple.icon_sizes
        data["macos_icon_sizes"] = model.apple.macos_icon_sizes
        data["ms_tile_icon_sizes"] = model.mstile.sizes
    return data


def data_path() -> Path:
    """Returns the path to the data json file."""
    return Path(__file__).parent.parent / "data" / "data.json"


def parse_launch_options(
    launch_tuple: tuple[str, str | None] | str,
) -> LogoLaunchScreenCLIParam | BufferedReader:
    """Parses a launch screen tuple and returns a LogoLaunchScreenCLIParam or a BufferedReader for logo_screen options."""
    if isinstance(launch_tuple, str):
        logo_path = Path(launch_tuple)
        if not logo_path.is_file():
            raise ValueError(f"Logo file {logo_path} does not exist.")
        return Path(launch_tuple).open("rb")
    color = launch_tuple[0].removeprefix("#")
    if len(color) == 3:
        color = "".join([c * 2 for c in color])
    if len(color) != 6 or any(c not in "0123456789abcdef" for c in color):
        raise ValueError(f"Invalid color format provided: {color}. Must be a hex color.")
    if launch_tuple[1] is None:
        return LogoLaunchScreenCLIParam(color)
    logo_path = Path(launch_tuple[1])
    if not logo_path.is_file():
        raise ValueError(f"Logo file {logo_path} does not exist.")
    return LogoLaunchScreenCLIParam(color, logo_path.open("rb"))


def make_dirs(dirs: tuple[Path] | list[Path]) -> None:
    """Creates directories if they don't exist."""
    for directory in dirs:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Error: Could not create directory {directory}.")
            raise typer.Exit(code=1) from e


def retrieve_model(path: Path | BufferedReader | None = None) -> MadIconModel:
    """Loads the data from the JSON file."""
    try:
        if path is None:
            path = data_path()
        content: io.BytesIO = load_file(path)
        content.seek(0)  # Reset the pointer to the beginning of the file
        return get_pwa_model(content.getvalue())
    except ValidationError as e:
        print(f"Error: Validation error in JSON file {path}.")
        raise typer.Exit(code=1) from e


__all__ = [
    "data_path",
    "has_value",
    "is_none_type",
    "load_file",
    "make_dirs",
    "parse_launch_options",
    "process_models",
    "retrieve_model",
]
