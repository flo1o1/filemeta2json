"""Validation of user input at the system boundary (fail fast)."""

import os
from pathlib import Path

from filemeta2json.errors import InvalidInputPathError, InvalidOutputPathError


def validate_input_path(raw_path: str) -> Path:
    """Return the input path as a Path if it exists.

    raw_path: file or directory path (str), must not be empty.
    """
    if not raw_path.strip():
        raise InvalidInputPathError("Input path is empty.")
    path = Path(raw_path).expanduser()
    if not path.exists():
        raise InvalidInputPathError(
            f"Input path does not exist: {raw_path}\n"
            "Check the path; quote paths that contain spaces."
        )
    if not os.access(path, os.R_OK):
        raise InvalidInputPathError(
            f"No read permission for: {raw_path}\n"
            "Check permissions (Linux/macOS: ls -l, chmod u+r) or run as a user with access."
        )
    return path


def validate_output_path(raw_path: str) -> Path:
    """Return the output path as a Path if a file can be written there.

    raw_path: path of the JSON target file (str); the parent directory must exist.
    """
    if not raw_path.strip():
        raise InvalidOutputPathError("Output path is empty.")
    path = Path(raw_path).expanduser()
    if path.is_dir():
        raise InvalidOutputPathError(f"Output path is a directory: {raw_path}")
    if not path.resolve().parent.is_dir():
        raise InvalidOutputPathError(
            f"Target directory does not exist: {path.resolve().parent}\n"
            "Create the directory (e.g. mkdir -p) or choose a different output path."
        )
    writable_target = path if path.exists() else path.resolve().parent
    if not os.access(writable_target, os.W_OK):
        raise InvalidOutputPathError(
            f"No write permission for: {writable_target}\n"
            "Check permissions or choose a different output path."
        )
    return path
