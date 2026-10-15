"""Datenmodell und JSON-Serialisierung des Ergebnisses."""

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable


@dataclass(frozen=True)
class FileMetadata:
    """Metadaten einer Datei.

    path: absoluter Dateipfad (str).
    metadata: eingebettete Metadaten, Schlüssel "Gruppe:Tag", JSON-serialisierbare Werte.
    """

    path: str
    metadata: Dict[str, Any]


def to_json(entries: Iterable[FileMetadata]) -> str:
    """Serialisiert Einträge als lesbares JSON-Array (UTF-8, Umlaute unmaskiert, mit Zeilenende)."""
    return json.dumps([asdict(entry) for entry in entries], indent=2, ensure_ascii=False) + "\n"
