"""Adapter for the external `exiftool` program (system boundary)."""

import json
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence

from filemeta2json.errors import ExifToolExecutionError, ExifToolNotFoundError

EXECUTABLE = "exiftool"
# -json: JSON output, -G: tag names with group ("EXIF:Make"),
# -@ -: file list from stdin (avoids command-line length limits).
BASE_ARGUMENTS = ("-json", "-G", "-charset", "filename=utf8", "-@", "-")

CommandRunner = Callable[..., "subprocess.CompletedProcess[bytes]"]


class ExifToolReader:
    """Reads metadata of several files with a single exiftool call."""

    def __init__(self, run_command: CommandRunner = subprocess.run,
                 executable: str = EXECUTABLE) -> None:
        """run_command: replaceable for tests; executable: name or path of exiftool."""
        self._run_command = run_command
        self._executable = executable

    def read(self, files: Sequence[Path]) -> List[Dict[str, Any]]:
        """Return one ExifTool record per file (dict, keys "Group:Tag").

        files: absolute file paths; paths must not contain line breaks.
        Raises: ExifToolNotFoundError, ExifToolExecutionError.
        """
        if not files:
            return []
        completed = self._execute(files)
        return self._parse(completed)

    def _execute(self, files: Sequence[Path]) -> "subprocess.CompletedProcess[bytes]":
        file_list = "\n".join(str(path) for path in files).encode("utf-8")
        try:
            return self._run_command(
                [self._executable, *BASE_ARGUMENTS],
                input=file_list,
                capture_output=True,
                check=False,
            )
        except FileNotFoundError as error:
            raise ExifToolNotFoundError(f"'{self._executable}' not found.") from error
        except PermissionError as error:
            raise ExifToolExecutionError(
                f"'{self._executable}' is not allowed to run. "
                "Check execute permissions (Linux/macOS: chmod +x <path to exiftool>)."
            ) from error

    @staticmethod
    def _parse(completed: "subprocess.CompletedProcess[bytes]") -> List[Dict[str, Any]]:
        # Return code 1 only reports individual unreadable files; as long as JSON is present, that is not an error.
        stdout = completed.stdout.decode("utf-8", errors="replace").strip()
        if not stdout:
            stderr = completed.stderr.decode("utf-8", errors="replace").strip()
            raise ExifToolExecutionError(
                f"exiftool produced no output (exit code {completed.returncode}): {stderr}\n"
                "Check the installation with `exiftool -ver`; if it fails, reinstall exiftool."
            )
        try:
            records = json.loads(stdout)
        except json.JSONDecodeError as error:
            raise ExifToolExecutionError(f"exiftool output is not valid JSON: {error}") from error
        return records
