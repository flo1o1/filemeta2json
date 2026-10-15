"""Prüft, ob ein Dateipfad an exiftool (UTF-8) und JSON übergeben werden kann."""

from pathlib import Path


def is_utf8_encodable(path: Path) -> bool:
    """True, wenn der Pfad verlustfrei als UTF-8 kodierbar ist.

    Unter Linux dürfen Dateinamen beliebige Bytes enthalten; Python bildet
    ungültige Bytes auf Surrogate ab, die sich nicht als UTF-8 kodieren lassen.
    """
    try:
        str(path).encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True
