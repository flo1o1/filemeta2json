"""Data model and JSON serialization of the result."""

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable


@dataclass(frozen=True)
class FileMetadata:
    """Metadata of a file.

    path: absolute file path (str).
    metadata: embedded metadata, keys "Group:Tag", JSON-serializable values.
    """

    path: str
    metadata: Dict[str, Any]


def to_json(entries: Iterable[FileMetadata]) -> str:
    """Serialize entries as a readable JSON array (UTF-8, non-ASCII characters unescaped, trailing newline)."""
    return json.dumps([asdict(entry) for entry in entries], indent=2, ensure_ascii=False) + "\n"
