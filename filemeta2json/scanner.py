"""Sammelt Dateien unterhalb eines Pfades."""

import os
from pathlib import Path
from typing import List


def collect_files(root: Path) -> List[Path]:
    """Liefert alle regulären Dateien unter `root` als absolute, sortierte Pfade.

    root: existierender Pfad. Eine Datei ergibt eine Liste mit genau diesem Pfad,
          ein Verzeichnis wird rekursiv durchsucht (Symlinks auf Verzeichnisse
          werden nicht verfolgt, damit keine Zyklen entstehen).
    """
    absolute_root = Path(os.path.abspath(root))
    if absolute_root.is_file():
        return [absolute_root]

    files = []
    for directory, _subdirectories, file_names in os.walk(absolute_root):
        for file_name in file_names:
            candidate = Path(directory) / file_name
            if candidate.is_file():
                files.append(candidate)
    return sorted(files)
