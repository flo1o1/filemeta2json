"""Command-line interface."""

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
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="filemeta2json",
        description="Reads embedded metadata of all files under a path "
                    "and prints it as JSON with the absolute file path.",
    )
    parser.add_argument("path", help="file or directory (searched recursively)")
    parser.add_argument("-o", "--output", metavar="FILE",
                        help="write JSON to this file instead of stdout")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Optional[Sequence[str]] = None,
         reader: Optional[ExifToolReader] = None,
         stdout: Optional[TextIO] = None,
         stderr: Optional[TextIO] = None,
         install_hint: Callable[[], str] = exiftool_install_hint) -> int:
    """Run the program and return the exit code.

    argv: arguments without the program name (default: sys.argv[1:]).
    reader, stdout, stderr, install_hint: replaceable for tests.
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
        print(f"Error: {error}\n{install_hint()}", file=stderr)
        return EXIT_EXIFTOOL_PROBLEM
    except ExifToolExecutionError as error:
        print(f"Error: {error}", file=stderr)
        return EXIT_EXIFTOOL_PROBLEM
    except FileMetaError as error:
        print(f"Error: {error}", file=stderr)
        return EXIT_INVALID_ARGUMENTS

    return EXIT_OK


def _write(json_text: str, output_path: Optional[Path], stdout: TextIO) -> None:
    if output_path is None:
        # Windows consoles default to a legacy code page that cannot encode all of the JSON.
        if hasattr(stdout, "reconfigure"):
            stdout.reconfigure(encoding=OUTPUT_ENCODING)
        stdout.write(json_text)
        return
    try:
        output_path.write_text(json_text, encoding=OUTPUT_ENCODING)
    except OSError as error:
        raise InvalidOutputPathError(
            f"Could not write output file: {error}\n"
            "Check permissions and free disk space, or choose a different output path."
        ) from error


def _warn_skipped(path: Path, stderr: TextIO) -> None:
    # ascii() escapes invalid bytes so the warning itself never fails.
    print(f"Warning: file name is not valid UTF-8, skipped: {ascii(str(path))}", file=stderr)
