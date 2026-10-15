"""Prüfung der Benutzereingaben an der Systemgrenze (Fail Fast)."""

import os
from pathlib import Path

from filemeta2json.errors import InvalidInputPathError, InvalidOutputPathError


def validate_input_path(raw_path: str) -> Path:
    """Gibt den Eingabepfad als Path zurück, wenn er existiert.

    raw_path: Datei- oder Verzeichnispfad (str), darf nicht leer sein.
    """
    if not raw_path.strip():
        raise InvalidInputPathError("Eingabepfad ist leer.")
    path = Path(raw_path).expanduser()
    if not path.exists():
        raise InvalidInputPathError(
            f"Eingabepfad existiert nicht: {raw_path}\n"
            "Pfad prüfen; Pfade mit Leerzeichen in Anführungszeichen setzen."
        )
    if not os.access(path, os.R_OK):
        raise InvalidInputPathError(
            f"Keine Leseberechtigung für: {raw_path}\n"
            "Rechte prüfen (Linux/macOS: ls -l, chmod u+r) oder mit einem berechtigten Benutzer starten."
        )
    return path


def validate_output_path(raw_path: str) -> Path:
    """Gibt den Ausgabepfad als Path zurück, wenn dort eine Datei geschrieben werden kann.

    raw_path: Pfad der JSON-Zieldatei (str); das Elternverzeichnis muss existieren.
    """
    if not raw_path.strip():
        raise InvalidOutputPathError("Ausgabepfad ist leer.")
    path = Path(raw_path).expanduser()
    if path.is_dir():
        raise InvalidOutputPathError(f"Ausgabepfad ist ein Verzeichnis: {raw_path}")
    if not path.resolve().parent.is_dir():
        raise InvalidOutputPathError(
            f"Zielverzeichnis existiert nicht: {path.resolve().parent}\n"
            "Verzeichnis anlegen (z. B. mkdir -p) oder einen anderen Ausgabepfad wählen."
        )
    writable_target = path if path.exists() else path.resolve().parent
    if not os.access(writable_target, os.W_OK):
        raise InvalidOutputPathError(
            f"Keine Schreibberechtigung für: {writable_target}\n"
            "Rechte prüfen oder einen anderen Ausgabepfad wählen."
        )
    return path
