"""Separates embedded metadata from file system and tool information."""

from typing import Any, Dict

SOURCE_FILE_KEY = "SourceFile"
GROUP_SEPARATOR = ":"

# Groups that ExifTool always returns and that say nothing about embedded
# metadata (file system, tool messages, base file type, derived values).
NON_EMBEDDED_GROUPS = frozenset({"System", "ExifTool", "File", "Composite"})


def extract_embedded_metadata(record: Dict[str, Any]) -> Dict[str, Any]:
    """Keep only the embedded metadata of an ExifTool record.

    record: one entry of the ExifTool JSON output (-G), keys "Group:Tag".
    Returns: subset of `record`; empty if the file contains no metadata.
    """
    return {
        key: value
        for key, value in record.items()
        if key != SOURCE_FILE_KEY and _is_embedded(key)
    }


def _is_embedded(key: str) -> bool:
    group = key.split(GROUP_SEPARATOR, 1)[0] if GROUP_SEPARATOR in key else ""
    return group not in NON_EMBEDDED_GROUPS
