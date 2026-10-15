"""Checks whether a file path can be passed to exiftool (UTF-8) and JSON."""

from pathlib import Path


def is_utf8_encodable(path: Path) -> bool:
    """True if the path can be encoded as UTF-8 without loss.

    On Linux, file names may contain arbitrary bytes; Python maps
    invalid bytes to surrogates, which cannot be encoded as UTF-8.
    """
    try:
        str(path).encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True
