"""Fachliche Fehler. Die CLI übersetzt sie in Exit-Codes und Meldungen."""


class FileMetaError(Exception):
    """Basisklasse aller erwarteten Fehler dieses Programms."""


class InvalidInputPathError(FileMetaError):
    """Der übergebene Eingabepfad existiert nicht oder ist leer."""


class InvalidOutputPathError(FileMetaError):
    """Der Ausgabepfad ist leer, ein Verzeichnis oder hat kein existierendes Elternverzeichnis."""


class ExifToolNotFoundError(FileMetaError):
    """Das Programm `exiftool` ist nicht installiert oder nicht im PATH."""


class ExifToolExecutionError(FileMetaError):
    """`exiftool` lieferte keine auswertbare Ausgabe."""
