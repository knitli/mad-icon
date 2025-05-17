# sourcery skip: avoid-global-variables
"""
(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).

This module defines generic or precursor types for the PWA icon generator.
Types for icon generation are in [`icon_generation_types`](icon_generation_types.py).
"""

from enum import Enum
from typing import IO, Any, Literal, NamedTuple

import typer

from typing_extensions import TypeVar


NoneType = None.__class__

NONE_TYPES: tuple[Any, Any, Any] = (None, NoneType, Literal[None])

EnumType = TypeVar("EnumType", bound=Enum)


class LogoLaunchScreenCLIParam(NamedTuple):
    """Represents a logo or launch screen.

    Attributes:
        color (str): The color for the launch screen in hex format.
        logo (typer.FileBinaryRead): A path to a logo image file.
    """

    color: str
    logo: typer.FileBinaryRead | IO[bytes] | None = None


class FilePrefixes(NamedTuple):
    """Represents the prefixes for filenames based on the resolution.

    Attributes:
        icon (str): The prefix for the apple touch icon.
        launch_screen (str): The prefix for the apple launch screen.
    """

    icon: str
    launch_screen: str


default_prefixes = FilePrefixes("apple-touch-icon", "apple-launch-screen")


__all__ = [
    "NONE_TYPES",
    "EnumType",
    "FilePrefixes",
    "LogoLaunchScreenCLIParam",
    "NoneType",
    "default_prefixes",
]
