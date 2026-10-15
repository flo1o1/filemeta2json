"""Use case: determine the metadata of all files under a path."""

import os
from pathlib import Path
from typing import Callable, List

from filemeta2json.exiftool_reader import ExifToolReader
from filemeta2json.filename_check import is_utf8_encodable
from filemeta2json.metadata_filter import SOURCE_FILE_KEY, extract_embedded_metadata
from filemeta2json.report import FileMetadata
from filemeta2json.scanner import collect_files


def _ignore_skipped(_path: Path) -> None:
    """Default callback: skipped files are not reported."""


def collect_metadata(root: Path, reader: ExifToolReader,
                     on_skipped: Callable[[Path], None] = _ignore_skipped) -> List[FileMetadata]:
    """Return entries for all files under `root` that have embedded metadata.

    root: existing file or directory.
    reader: source of the raw data (replaceable).
    on_skipped: called for each file whose name cannot be encoded as UTF-8
                (such files are skipped).
    Returns: sorted by absolute path; files without metadata are omitted.
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
