# sourcery skip: lambdas-should-be-short
"""
`models/models` module. - Models for icon generation.

(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).
"""

from enum import Enum, auto
from itertools import starmap
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from mad_icon.models.resolution import Resolution
from mad_icon.types import IconSizeData, IconSizesType


class DeviceType(Enum):
    """Represents the type of AppleDevice."""

    IPHONE = auto()
    IPAD = auto()
    IPOD = auto()


class AppleDevice(BaseModel):
    """Represents a AppleDevice."""

    name: str
    model: str
    kind: Annotated[
        DeviceType,
        Field(
            default_factory=lambda x: DeviceType.__members__[
                x.upper() if isinstance(x, str) else x["kind"].upper()
            ]
        ),
    ]
    actual_resolution: Annotated[
        Resolution,
        Field(
            default_factory=lambda data: Resolution.from_number_pair(data["actualResolution"]),
            validate_default=True,
            alias="actualResolution",
        ),
    ]
    logical_resolution: Annotated[
        Resolution,
        Field(
            default_factory=lambda data: Resolution.from_number_pair(data["actualResolution"]),
            validate_default=True,
            alias="logicalResolution",
        ),
    ]
    diagonal_size: Annotated[
        float,
        Field(
            default_factory=lambda data: float(data["diagonalSize"]),
            validate_default=True,
            alias="diagonalSize",
            description="Diagonal size in inches",
        ),
    ]
    ppi: Annotated[int, Field(..., gt=130, description="Pixels per inch")]
    scale_factor: Annotated[int, Field(..., alias="scaleFactor", gt=0)]
    generation: Annotated[int | None, Field(default=None)]
    decimal_aspect_ratio: Annotated[float, Field(..., gt=0)]
    aspect_ratio: Annotated[str, Field(..., alias="aspectRatio")]
    aspect_ratio_str: Annotated[
        str, Field(default_factory=lambda data: data["actualResolution"].aspect_ratio_str)
    ]
    identical_to: Annotated[list[str] | None, Field(default=None, alias="identicalTo")]


def process_icon_sizes(icon_sizes: IconSizesType) -> list[Resolution]:
    """
    Process the values for `iconSizes`, `macOSIconSizes`, and `msTileIconSizes` in the `data.json` file.
    """
    return [Resolution(size, size) for size in icon_sizes]


class AppleModel(BaseModel):
    """The 'apple' key in the `data.json` file."""

    devices: list[AppleDevice]
    icon_sizes: Annotated[
        list[Resolution],
        Field(
            default_factory=lambda data: process_icon_sizes(
                data.get("iconSizes") or data.get("icon_sizes", [])
            ),
            alias="iconSizes",
        ),
    ]
    macos_icon_sizes: Annotated[
        list[Resolution],
        Field(
            default_factory=lambda data: process_icon_sizes(
                data.get("macOSIconSizes") or data.get("macos_icon_sizes", [])
            ),
            alias="macOSIconSizes",
        ),
    ]

    @property
    def screen_sizes(self) -> list[Resolution]:
        """
        Returns a list of unique screen sizes for the devices.
        This is used to generate the launch screens.
        """
        return sorted(
            {device.actual_resolution for device in self.devices}, key=lambda x: (x.width, x.height)
        )


class AndroidModel(BaseModel):
    """The 'android' key in the `data.json` file."""

    masked_icon_sizes: Annotated[
        list[Resolution],
        Field(
            default_factory=lambda data: process_icon_sizes(
                data.get("maskedIconSizes") or data.get("masked_icon_sizes", [])
            ),
            alias="maskedIconSizes",
        ),
    ]


class MsTileModel(BaseModel):
    """The 'mstile' key in the `data.json` file."""

    sizes: list[Resolution]

    @field_validator("sizes", mode="after")
    @classmethod
    def process_sizes(cls, value: list[tuple[int, int]]) -> list[Resolution]:
        """
        Process the values for `sizes` in the `data.json` file.
        """
        return sorted(set(starmap(Resolution, value)), key=lambda x: (x.width, x.height))


class MadIconModel(BaseModel):
    """The root model for the `data.json` file."""

    apple: AppleModel
    android: AndroidModel
    mstile: MsTileModel

    @property
    def size_data(self) -> IconSizeData:
        """
        Get the size data for the Mad Model.
        """
        return IconSizeData(
            touch_icons=self.apple.icon_sizes,
            macos_icons=self.apple.macos_icon_sizes,
            ms_tiles=self.mstile.sizes,
            masked_icons=self.android.masked_icon_sizes,
        )


def get_mad_model(data: str | bytes | bytearray) -> MadIconModel:
    """Get the Mad Model from the `data.json` file."""
    return MadIconModel.model_validate_json(data)


__all__ = [
    "AndroidModel",
    "AppleDevice",
    "AppleModel",
    "DeviceType",
    "MsTileModel",
    "MadIconModel",
    "Resolution",
    "get_mad_model",
]
