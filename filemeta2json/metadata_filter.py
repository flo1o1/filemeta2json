"""Trennt eingebettete Metadaten von Dateisystem- und Tool-Informationen."""

from typing import Any, Dict

SOURCE_FILE_KEY = "SourceFile"
GROUP_SEPARATOR = ":"

# Gruppen, die ExifTool immer liefert und die nichts über eingebettete
# Metadaten aussagen (Dateisystem, Tool-Meldungen, Basis-Dateityp, abgeleitete Werte).
NON_EMBEDDED_GROUPS = frozenset({"System", "ExifTool", "File", "Composite"})


def extract_embedded_metadata(record: Dict[str, Any]) -> Dict[str, Any]:
    """Behält nur eingebettete Metadaten eines ExifTool-Datensatzes.

    record: ein Eintrag der ExifTool-JSON-Ausgabe (-G), Schlüssel "Gruppe:Tag".
    Rückgabe: Teilmenge von `record`; leer, wenn die Datei keine Metadaten enthält.
    """
    return {
        key: value
        for key, value in record.items()
        if key != SOURCE_FILE_KEY and _is_embedded(key)
    }


def _is_embedded(key: str) -> bool:
    group = key.split(GROUP_SEPARATOR, 1)[0] if GROUP_SEPARATOR in key else ""
    return group not in NON_EMBEDDED_GROUPS
