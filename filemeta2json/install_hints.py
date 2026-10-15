"""Handlungsanweisungen, wenn exiftool fehlt (abhängig von Betriebssystem und Paketmanager)."""

import shutil
import sys
from typing import Callable, List, Tuple

DOWNLOAD_URL = "https://exiftool.org/install.html"
HOMEBREW_URL = "https://brew.sh"

# (Programm des Paketmanagers, Installationsbefehl), in Reihenfolge der Empfehlung.
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
    """Erzeugt eine mehrzeilige Anleitung zur Installation von exiftool.

    platform: Wert wie `sys.platform` ("darwin", "linux", "win32", …).
    find_program: liefert für einen Programmnamen einen Pfad oder None (Standard: shutil.which).
    """
    commands = _available_commands(_commands_for(platform), find_program)
    if commands:
        lines = ["exiftool installieren mit:"] + [f"  {command}" for command in commands]
    else:
        lines = [f"Kein bekannter Paketmanager gefunden. Download und Anleitung: {DOWNLOAD_URL}"]
        if platform.startswith("darwin"):
            lines.append(f"Oder zuerst Homebrew installieren: {HOMEBREW_URL}")
    lines.append("Danach prüfen: exiftool -ver (Terminal ggf. neu starten, damit der PATH aktualisiert wird).")
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
