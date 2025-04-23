"""
`icon_generation_types` module
Provides types and enums for icon generation configuration in the Mad Icon generator.
Uses the `IconGenerationConfig` TypedDict to define the configuration settings for different icon generation flags, and uses the `IconGenerationFlag` enum to represent the various icon generation options available. `IconGenerationFlag` has a series of properties that define the icon generation configuration based on the flag, using the `IconDescriptiveName`, `IconSourceKey`, `IconSizeGroup`, and `ManifestPurpose` enums.

Externally, the `get_flag_config` function brings all this typing goodness together, allowing you to get the configuration for a given flag.

(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).
"""

from enum import StrEnum
from pathlib import Path
from typing import TypedDict

import typer

from mad_icon.models import Resolution


type IconSizesType = list[int]


class ProcessingRequirements(TypedDict):
    """Processing requirements for icon generation.

    Attributes:
        needs_desat (bool): Whether desaturation is needed.
        needs_opaque (bool): Whether an opaque background is needed
        needs_trans (bool): Whether a transparent background is needed.
        needs_clip (bool): Whether clipping is needed.
    """

    needs_desat: bool
    needs_opaque: bool
    needs_trans: bool
    needs_clip: bool


class IconSizeData(TypedDict):
    """Icon size data for different platforms."""

    touch_icons: list[Resolution]
    macos_icons: list[Resolution]
    ms_tiles: list[Resolution]
    masked_icons: list[Resolution]


class IconDescriptiveName(StrEnum):
    """Descriptive names for icons."""

    APPLE_TOUCH = "Apple Touch"
    ANDROID_MASKED = "Android Masked"
    ANDROID_MONOCHROME = "Android Monochrome"
    APPLE_DARKMODE = "Apple Dark Mode"
    APPLE_TINTED = "Apple Tinted"
    HTML = "HTML"
    NO_ICONS = "No Icons"
    MACOS = "macOS"
    MANIFEST = "Manifest Json"
    MS_TILES = "MS Tiles"


class IconSourceKey(StrEnum):
    """The key for the source image used to generate the icon."""

    BASE = "base"
    MASKED = "masked"
    MONOCHROME = "monochrome"
    DARK = "dark"
    TINTED = "tinted"
    TILE_RECTANGLE = "tile-rectangle"

    @classmethod
    def from_flag(cls, name: str) -> "IconSourceKey":
        """Converts a string to the corresponding enum member."""
        member_name = name.removesuffix("_icon").removeprefix("apple_").upper()
        try:
            return cls.__members__[member_name]
        except KeyError as e:
            raise ValueError(f"Invalid flag: {str}, not a member of {cls.__name__}") from e

    @property
    def fallback_strategy(self) -> "IconSourceKey":
        """Returns the fallback strategy for the icon source key. This is set up so that you can test fallbacks of fallbacks by iterating through their fallback_stregies. For example, if you have a tinted icon, it will fallback to dark, but if there's no dark, it will fallback to base, and then to masked if available."""
        match self:
            case IconSourceKey.MASKED:
                return type(self).BASE
            case IconSourceKey.DARK:
                return type(self).BASE
            case IconSourceKey.TINTED:
                return type(self).DARK
            case IconSourceKey.TILE_RECTANGLE:
                return type(self).BASE
            case _:
                return type(self).MASKED

    @classmethod
    def from_kwargs(cls, kwargs: dict[str, str]) -> "list[IconSourceKey]":
        """Converts a dictionary of keyword arguments to the corresponding enum member."""
        result = (
            [] if kwargs.get("no_icons") else [cls.BASE]
        )  # handle no_icons with other icon flags present
        result.extend([cls.from_flag(k) for k, v in kwargs.items() if v and k.endswith("_icon")])
        return result


class IconSizeGroup(StrEnum):
    """
    Which icon sizes to use for a given icon generation.
    The values are the attribute names in the [data model](../models/models.py#MadIconModel).
    """

    APPLE_TOUCH = "apple.icon_sizes"
    MACOS = "apple.macos_icon_sizes"
    MASKED = "android.masked_icon_sizes"
    MS_TILES = "mstile.sizes"


class ManifestPurpose(StrEnum):
    """
    Purpose attribute for icons in a web app manifest.

    Attributes:
        MASKABLE (str): Purpose for maskable icons.
        MONOCHROME (str): Purpose for monochrome icons.
        ANY (str): General purpose for icons.
        NOT_MANIFESTED (str): Icons are not included in the manifest.
    """

    MASKABLE = "maskable"
    MONOCHROME = "monochrome"
    ANY = "any"
    NOT_MANIFESTED = "not_manifested"


class IconGenerationFlag(StrEnum):
    """
    Feature flags for icon generation.
    """

    APPLE_TOUCH = "apple_touch"  # the default
    NO_ICONS = "no_icons"  # No icons to be generated
    MASKED = "masked"
    MONOCHROME = "monochrome"  # masked-monochrome
    DARKMODE = "darkmode"  # apple-dark
    TINTED = "tinted"  # apple-tinted
    MACOS = "macos"
    MS_TILES = "ms_tiles"
    HTML = "html"  # flag for HTML generation
    MANIFEST = "manifest"  # flag for manifest generation

    def __str__(self) -> str:
        """Returns the string representation of the enum value."""
        return self.value

    @classmethod
    def is_not_icon_flag(cls, flag: "IconGenerationFlag") -> bool:
        """Checks if the given flag is not an icon generation flag."""
        return flag in (cls.NO_ICONS, cls.MANIFEST, cls.HTML)

    @property
    def descriptive_name(self) -> IconDescriptiveName:
        """Returns a descriptive name or pair of possible names for the flag."""
        match self:
            case IconGenerationFlag.MASKED | IconGenerationFlag.MONOCHROME:
                return IconDescriptiveName.__members__.get(
                    f"ANDROID_{self.name.upper()}", IconDescriptiveName.ANDROID_MASKED
                )
            case (
                IconGenerationFlag.APPLE_TOUCH
                | IconGenerationFlag.DARKMODE
                | IconGenerationFlag.TINTED
            ):
                return IconDescriptiveName.__members__.get(
                    f"APPLE_{self.name.upper()}", IconDescriptiveName.APPLE_TOUCH
                )
            case _:
                try:
                    return IconDescriptiveName.__members__[self.name.upper()]
                except KeyError as e:
                    raise ValueError(
                        f"Invalid flag: {self.name}, not a member of {IconDescriptiveName.__name__}"
                    ) from e

    @property
    def source_key(self) -> IconSourceKey | None:
        """Returns the icon source key associated with the flag."""
        match self:
            case self if self.is_not_icon_flag(self):
                return None
            case IconGenerationFlag.MS_TILES:
                return IconSourceKey.TILE_RECTANGLE
            case IconGenerationFlag.MACOS | IconGenerationFlag.APPLE_TOUCH:
                return IconSourceKey.BASE
            case IconGenerationFlag.DARKMODE:
                return IconSourceKey.DARK
            case _:
                return IconSourceKey.__members__.get(self.name.upper(), IconSourceKey.MASKED)

    @property
    def model_attr(self) -> IconSizeGroup | None:
        """Returns the model attribute associated with the flag."""
        match self:
            case self if self.is_not_icon_flag(self):
                return None
            case IconGenerationFlag.MASKED:
                return IconSizeGroup.MASKED
            case IconGenerationFlag.MACOS:
                return IconSizeGroup.MACOS
            case IconGenerationFlag.MS_TILES:
                return IconSizeGroup.MS_TILES
            case _:
                return IconSizeGroup.APPLE_TOUCH

    @property
    def subdir(self) -> str:
        """Returns the subdirectory name associated with the flag."""
        match self:
            case IconGenerationFlag.MASKED:
                return "masked"
            case IconGenerationFlag.MONOCHROME:
                return "masked-monochrome"
            case IconGenerationFlag.DARKMODE:
                return "apple-dark"
            case IconGenerationFlag.TINTED:
                return "tinted"
            case IconGenerationFlag.MACOS:
                return "macos"
            case IconGenerationFlag.MS_TILES:
                return "mstile"
            case IconGenerationFlag.APPLE_TOUCH:
                return ""
            case _:
                return "../"

    @property
    def processing_requirements(self) -> ProcessingRequirements | None:
        """Returns the processing requirements for the flag if it's an icon flag."""
        match self:
            case self if self.is_not_icon_flag(self):
                return None
            case IconGenerationFlag.MASKED:
                return ProcessingRequirements(
                    needs_desat=False, needs_opaque=True, needs_trans=False, needs_clip=False
                )
            case IconGenerationFlag.MONOCHROME:
                return ProcessingRequirements(
                    needs_desat=True, needs_opaque=True, needs_trans=False, needs_clip=False
                )
            case IconGenerationFlag.DARKMODE:
                return ProcessingRequirements(
                    needs_desat=False, needs_opaque=False, needs_trans=True, needs_clip=False
                )
            case IconGenerationFlag.TINTED:
                return ProcessingRequirements(
                    needs_desat=True, needs_opaque=False, needs_trans=True, needs_clip=False
                )
            case IconGenerationFlag.MACOS:
                return ProcessingRequirements(
                    needs_desat=False, needs_opaque=True, needs_trans=False, needs_clip=True
                )
            case IconGenerationFlag.MS_TILES:
                return ProcessingRequirements(
                    needs_desat=False, needs_opaque=True, needs_trans=False, needs_clip=False
                )
            case _:
                return ProcessingRequirements(
                    needs_desat=False, needs_opaque=True, needs_trans=False, needs_clip=False
                )

    @property
    def manifest_purpose(self) -> ManifestPurpose | tuple[ManifestPurpose, ManifestPurpose] | None:
        """Returns the manifest purpose for the flag if it's an icon flag."""
        match self:
            case self if self.is_not_icon_flag(self):
                return None
            case IconGenerationFlag.MASKED:
                return ManifestPurpose.MASKABLE
            case IconGenerationFlag.MONOCHROME:
                return (ManifestPurpose.MASKABLE, ManifestPurpose.MONOCHROME)
            case IconGenerationFlag.TINTED:
                return ManifestPurpose.MONOCHROME
            case IconGenerationFlag.MACOS:
                return ManifestPurpose.ANY
            case _:
                return ManifestPurpose.NOT_MANIFESTED

    @classmethod
    def from_string(cls, flag: str) -> "IconGenerationFlag":
        """Converts a string to the corresponding enum member."""
        try:
            return cls.__members__[flag.upper()]
        except KeyError as e:
            raise ValueError(f"Invalid flag: {flag}, not a member of {cls.__name__}") from e


class IconGenerationConfig(TypedDict, total=False):
    """
    Configuration for icon generation.

    Attributes:
        flag_key (IconGenerationFlag): The flag key for icon generation.
        name (IconDescriptiveName): Descriptive name for the icon.
        source_key (IconSourceKey): The source key for the icon.
        subdir (str): Subdirectory name for the icon.
        model_attr (IconSizeGroup): The model attribute for icon sizes.
        ManifestPurpose (ManifestPurpose): Purpose attribute for the manifest.
        needs_desat (bool): Whether desaturation is needed.
        needs_opaque (bool): Whether an opaque background is needed

    """

    flag_key: IconGenerationFlag
    name: IconDescriptiveName
    subdir: str
    is_icon_flag: bool

    source_key: IconSourceKey | None
    model_attr: IconSizeGroup | None
    purpose: ManifestPurpose | tuple[ManifestPurpose, ManifestPurpose] | None
    # ProcessingRequirements: ProcessingRequirements
    needs_desat: bool | None
    needs_opaque: bool | None
    needs_trans: bool | None
    needs_clip: bool | None


def get_flag_config(flag: IconGenerationFlag) -> IconGenerationConfig:
    """Returns the configuration for the given flag."""
    if IconGenerationFlag.is_not_icon_flag(flag):
        return IconGenerationConfig(
            flag_key=flag, name=flag.descriptive_name, subdir=flag.subdir, is_icon_flag=False
        )
    return IconGenerationConfig(
        flag_key=flag,
        name=flag.descriptive_name,
        subdir=flag.subdir,
        is_icon_flag=True,
        source_key=flag.source_key,
        model_attr=flag.model_attr,
        purpose=flag.manifest_purpose,
        **flag.processing_requirements,  # type: ignore[assignment] # pyright doesn't like the unpacking of TypedDicts
    )


class ProcessedIconKwargs(TypedDict, total=False):
    """Processed icon generation arguments."""

    base_icon: typer.FileBinaryRead | None
    masked_icon: typer.FileBinaryRead | None
    masked_monochrome_icon: typer.FileBinaryRead | None
    apple_darkmode_icon: typer.FileBinaryRead | None
    apple_tinted_icon: typer.FileBinaryRead | None
    tile_rectangle_icon: typer.FileBinaryRead | None
    prefix: str
    destination_dir: Path
    no_icons: bool
    apple_touch: IconGenerationConfig | None
    masked: IconGenerationConfig | None
    monochrome: IconGenerationConfig | None
    darkmode: IconGenerationConfig | None
    tinted: IconGenerationConfig | None
    macos: IconGenerationConfig | None
    ms_tiles: IconGenerationConfig | None
    html: IconGenerationConfig | None
    manifest: IconGenerationConfig | None
    html_file_name: str | None
    html_destination: Path | None
    json_path: typer.FileBinaryRead
    attempt_svg_analysis: bool | None
    sizes: IconSizeData | None


__all__ = [
    "IconDescriptiveName",
    "IconGenerationConfig",
    "IconGenerationFlag",
    "IconSizeData",
    "IconSizeGroup",
    "IconSizesType",
    "IconSourceKey",
    "ManifestPurpose",
    "ProcessingRequirements",
    "get_flag_config",
]
