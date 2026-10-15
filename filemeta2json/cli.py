"""Kommandozeilenschnittstelle."""

import argparse
import sys
from pathlib import Path
from typing import Callable, Optional, Sequence, TextIO

from filemeta2json import __version__
from filemeta2json.errors import (ExifToolExecutionError, ExifToolNotFoundError,
                                  FileMetaError, InvalidOutputPathError)
from filemeta2json.exiftool_reader import ExifToolReader
from filemeta2json.install_hints import exiftool_install_hint
from filemeta2json.report import to_json
from filemeta2json.service import collect_metadata
from filemeta2json.validation import validate_input_path, validate_output_path

EXIT_OK = 0
EXIT_INVALID_ARGUMENTS = 2
EXIT_EXIFTOOL_PROBLEM = 3
OUTPUT_ENCODING = "utf-8"


def build_parser() -> argparse.ArgumentParser:
    """Erzeugt den Argument-Parser."""
    parser = argparse.ArgumentParser(
        prog="filemeta2json",
        description="Liest eingebettete Metadaten aller Dateien unter einem Pfad "
                    "und gibt sie mit absolutem Dateipfad als JSON aus.",
    )
    parser.add_argument("path", help="Datei oder Verzeichnis (wird rekursiv durchsucht)")
    parser.add_argument("-o", "--output", metavar="DATEI",
                        help="JSON in diese Datei schreiben statt nach stdout")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Optional[Sequence[str]] = None,
         reader: Optional[ExifToolReader] = None,
         stdout: Optional[TextIO] = None,
         stderr: Optional[TextIO] = None,
         install_hint: Callable[[], str] = exiftool_install_hint) -> int:
    """Führt das Programm aus und liefert den Exit-Code.

    argv: Argumente ohne Programmnamen (Standard: sys.argv[1:]).
    reader, stdout, stderr, install_hint: austauschbar für Tests.
    """
    reader = reader or ExifToolReader()
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    arguments = build_parser().parse_args(argv)

    try:
        input_path = validate_input_path(arguments.path)
        output_path = validate_output_path(arguments.output) if arguments.output is not None else None
        json_text = to_json(collect_metadata(
            input_path, reader, on_skipped=lambda path: _warn_skipped(path, stderr)))
        _write(json_text, output_path, stdout)
    except ExifToolNotFoundError as error:
        print(f"Fehler: {error}\n{install_hint()}", file=stderr)
        return EXIT_EXIFTOOL_PROBLEM
    except ExifToolExecutionError as error:
        print(f"Fehler: {error}", file=stderr)
        return EXIT_EXIFTOOL_PROBLEM
    except FileMetaError as error:
        print(f"Fehler: {error}", file=stderr)
        return EXIT_INVALID_ARGUMENTS

    return EXIT_OK


def _write(json_text: str, output_path: Optional[Path], stdout: TextIO) -> None:
    if output_path is None:
        stdout.write(json_text)
        return
    try:
        output_path.write_text(json_text, encoding=OUTPUT_ENCODING)
    except OSError as error:
        raise InvalidOutputPathError(
            f"Ausgabedatei konnte nicht geschrieben werden: {error}\n"
            "Rechte und freien Speicherplatz prüfen oder einen anderen Ausgabepfad wählen."
        ) from error


def _warn_skipped(path: Path, stderr: TextIO) -> None:
    # ascii() maskiert ungültige Bytes, damit die Warnung selbst nie fehlschlägt.
    print(f"Warnung: Dateiname nicht als UTF-8 lesbar, übersprungen: {ascii(str(path))}", file=stderr)
