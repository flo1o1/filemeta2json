"""Instructions for when exiftool is missing (depending on operating system and package manager)."""

import shutil
import sys
from typing import Callable, List, Tuple

DOWNLOAD_URL = "https://exiftool.org/install.html"
HOMEBREW_URL = "https://brew.sh"

# (package manager program, install command), in order of recommendation.
_MACOS = [
    ("brew", "brew install exiftool"),
    ("port", "sudo port install p5-image-exiftool"),
]
_LINUX = [
    ("apt-get", "sudo apt-get install libimage-exiftool-perl"),
    ("dnf", "sudo dnf install perl-Image-ExifTool"),
    ("yum", "sudo yum install perl-Image-ExifTool"),
    ("pacman", "sudo pacman -S perl-image-exiftool"),
    ("zypper", "sudo zypper install exiftool"),
    ("apk", "sudo apk add exiftool"),
    ("nix-env", "nix-env -iA nixpkgs.exiftool"),
    ("brew", "brew install exiftool"),
]
_WINDOWS = [
    ("winget", "winget install OliverBetz.ExifTool"),
    ("choco", "choco install exiftool"),
    ("scoop", "scoop install exiftool"),
]

PackageManagerLookup = Callable[[str], object]


def exiftool_install_hint(platform: str = sys.platform,
                          find_program: PackageManagerLookup = shutil.which) -> str:
    """Build a multi-line guide for installing exiftool.

    platform: value like `sys.platform` ("darwin", "linux", "win32", …).
    find_program: returns a path or None for a program name (default: shutil.which).
    """
    commands = _available_commands(_commands_for(platform), find_program)
    if commands:
        lines = ["Install exiftool with:"] + [f"  {command}" for command in commands]
    else:
        lines = [f"No known package manager found. Download and instructions: {DOWNLOAD_URL}"]
        if platform.startswith("darwin"):
            lines.append(f"Or install Homebrew first: {HOMEBREW_URL}")
    lines.append("Then verify: exiftool -ver (restart the terminal if needed so the PATH is updated).")
    return "\n".join(lines)


def _commands_for(platform: str) -> List[Tuple[str, str]]:
    if platform.startswith("darwin"):
        return _MACOS
    if platform.startswith("linux"):
        return _LINUX
    if platform.startswith(("win", "cygwin", "msys")):
        return _WINDOWS
    return []


def _available_commands(candidates: List[Tuple[str, str]],
                        find_program: PackageManagerLookup) -> List[str]:
    return [command for program, command in candidates if find_program(program)]
