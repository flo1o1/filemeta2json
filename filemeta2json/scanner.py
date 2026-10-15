"""Collects files below a path."""

import os
from pathlib import Path
from typing import List


def collect_files(root: Path) -> List[Path]:
    """Return all regular files under `root` as absolute, sorted paths.

    root: existing path. A file yields a list with exactly that path,
          a directory is searched recursively (symlinks to directories
          are not followed, to avoid cycles).
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
