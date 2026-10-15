"""Anwendungsfall: Metadaten aller Dateien unter einem Pfad ermitteln."""

import os
from pathlib import Path
from typing import Callable, List

from filemeta2json.exiftool_reader import ExifToolReader
from filemeta2json.filename_check import is_utf8_encodable
from filemeta2json.metadata_filter import SOURCE_FILE_KEY, extract_embedded_metadata
from filemeta2json.report import FileMetadata
from filemeta2json.scanner import collect_files


def _ignore_skipped(_path: Path) -> None:
    """Standard-Callback: übersprungene Dateien werden nicht gemeldet."""


def collect_metadata(root: Path, reader: ExifToolReader,
                     on_skipped: Callable[[Path], None] = _ignore_skipped) -> List[FileMetadata]:
    """Liefert Einträge für alle Dateien unter `root`, die eingebettete Metadaten besitzen.

    root: existierende Datei oder Verzeichnis.
    reader: Quelle der Rohdaten (austauschbar).
    on_skipped: wird für jede Datei aufgerufen, deren Name nicht als UTF-8 kodierbar ist
                (solche Dateien werden übersprungen).
    Rückgabe: nach absolutem Pfad sortiert; Dateien ohne Metadaten fehlen.
    """
    files = _drop_unencodable(collect_files(root), on_skipped)
    records = reader.read(files)
    entries = []
    for record in records:
        metadata = extract_embedded_metadata(record)
        if metadata:
            entries.append(FileMetadata(os.path.abspath(record[SOURCE_FILE_KEY]), metadata))
    return sorted(entries, key=lambda entry: entry.path)


def _drop_unencodable(files: List[Path], on_skipped: Callable[[Path], None]) -> List[Path]:
    readable = []
    for file in files:
        if is_utf8_encodable(file):
            readable.append(file)
        else:
            on_skipped(file)
    return readable
