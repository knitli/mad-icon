# sourcery skip: do-not-use-staticmethod
"""
`models/resolution` module.

This module provides the Resolution class, which represents the resolution of an image or screen.

(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).
"""

from dataclasses import dataclass
from typing import Self, TypeGuard

from mad_icon.types.types import FilePrefixes, default_prefixes


@dataclass(frozen=True, slots=True)
class Resolution:
    """Represents the resolution of an image or screen.

    The Resolution class stores the height and width of an image or screen,
    ensuring that width is always greater than or equal to height.


    Attributes:
        height (int): The height of the image or screen.
        width (int): The width of the image or screen.
        aspect_ratio (float): The decimal aspect ratio of the resolution.
        aspect_ratio_str (str): The aspect ratio of the resolution as a string, reduced to the greatest common divisor.

    Methods:
        get_filename: Returns the filename of the resolution object based on its aspect ratio.
        from_number_pair: Creates a Resolution object from a number pair string, like '1024x1366' or '1024:1366'.
    """

    height: int
    width: int

    def __init__(self, height: int, width: int) -> None:
        """Initialize a Resolution object.

        Args:
            height: The height of the image or screen.
            width: The width of the image or screen.

        Raises:
            ValueError: If height or width are not positive integers.
        """
        if height <= 0 or width <= 0:
            raise ValueError("Height and width must be positive integers.")
        if height > width:
            object.__setattr__(self, "height", width)
            object.__setattr__(self, "width", height)
        else:
            object.__setattr__(self, "height", height)
            object.__setattr__(self, "width", width)

    def __hash__(self) -> int:
        """Hashes the Resolution object based on its height and width."""
        return hash((self.height, self.width))

    def __str__(self) -> str:
        """Returns a string representation of the Resolution object as `widthxheight`."""
        if self.height == self.width:
            return f"{self.height}x{self.height}"
        return f"{self.width}x{self.height}"

    @property
    def aspect_ratio(self) -> float:
        """Returns the decimal aspect ratio of the Resolution object."""
        return 1.0 if self.height == self.width else round(self.width / self.height, 2)

    @property
    def aspect_ratio_str(self) -> str:
        """Returns the aspect ratio of the Resolution object as a string."""

        def gcd(a: int, b: int) -> int:
            """Finds the greatest common divisor of a and b."""
            while b:
                a, b = b, a % b
            return a

        divisor = gcd(self.width, self.height)
        return f"{self.width // divisor}:{self.height // divisor}"

    def get_filename(self, filename_prefixes: FilePrefixes = default_prefixes) -> str:
        """Returns the filename of the Resolution object based on its aspect ratio."""
        if self.aspect_ratio == 1.0 or self.height == self.width:
            return f"{filename_prefixes.icon}-{self.width}x{self.height}.png"
        return f"{filename_prefixes.launch_screen}-{self.width}x{self.height}.png"

    @staticmethod
    def _is_valid_number_pair(number_pair: str) -> TypeGuard[str]:
        """Checks if the given string is a valid number pair."""
        if not number_pair:
            return False
        number_pair = number_pair.replace(" ", "")
        if "x" in number_pair:
            return number_pair.count("x") == 1
        return number_pair.count(":") == 1 if ":" in number_pair else False

    @classmethod
    def from_number_pair(cls, number_pair: str | tuple[int, int]) -> Self:
        """Creates a Resolution object from a number pair string, like '1024x1366' or '1024:1366'."""
        if isinstance(number_pair, (tuple, list)) and len(number_pair) == 2:
            return cls(*number_pair)
        if cls._is_valid_number_pair(number_pair):
            number_pair = number_pair.replace(" ", "")
            if (separator := "x" if "x" in number_pair else ":") and separator in number_pair:
                return cls(*[int(x) for x in number_pair.split(separator)])
        raise ValueError(f"Invalid number pair: {number_pair}")


__all__ = ["Resolution"]
