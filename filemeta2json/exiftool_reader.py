"""Adapter zum externen Programm `exiftool` (Systemgrenze)."""

import json
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence

from filemeta2json.errors import ExifToolExecutionError, ExifToolNotFoundError

EXECUTABLE = "exiftool"
# -json: JSON-Ausgabe, -G: Tagnamen mit Gruppe ("EXIF:Make"),
# -@ -: Dateiliste von stdin (umgeht Längenlimits der Kommandozeile).
BASE_ARGUMENTS = ("-json", "-G", "-charset", "filename=utf8", "-@", "-")

CommandRunner = Callable[..., "subprocess.CompletedProcess[bytes]"]


class ExifToolReader:
    """Liest Metadaten mehrerer Dateien mit einem einzigen exiftool-Aufruf."""

    def __init__(self, run_command: CommandRunner = subprocess.run,
                 executable: str = EXECUTABLE) -> None:
        """run_command: austauschbar für Tests; executable: Name oder Pfad von exiftool."""
        self._run_command = run_command
        self._executable = executable

    def read(self, files: Sequence[Path]) -> List[Dict[str, Any]]:
        """Liefert pro Datei einen ExifTool-Datensatz (dict, Schlüssel "Gruppe:Tag").

        files: absolute Dateipfade; Pfade dürfen keine Zeilenumbrüche enthalten.
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
            raise ExifToolNotFoundError(f"'{self._executable}' nicht gefunden.") from error
        except PermissionError as error:
            raise ExifToolExecutionError(
                f"'{self._executable}' darf nicht ausgeführt werden. "
                "Ausführungsrechte prüfen (Linux/macOS: chmod +x <Pfad zu exiftool>)."
            ) from error

    @staticmethod
    def _parse(completed: "subprocess.CompletedProcess[bytes]") -> List[Dict[str, Any]]:
        # Returncode 1 meldet nur einzelne unlesbare Dateien; solange JSON vorliegt, ist das kein Fehler.
        stdout = completed.stdout.decode("utf-8", errors="replace").strip()
        if not stdout:
            stderr = completed.stderr.decode("utf-8", errors="replace").strip()
            raise ExifToolExecutionError(
                f"exiftool lieferte keine Ausgabe (Exit-Code {completed.returncode}): {stderr}\n"
                "Installation prüfen mit `exiftool -ver`; bei Fehlern exiftool neu installieren."
            )
        try:
            records = json.loads(stdout)
        except json.JSONDecodeError as error:
            raise ExifToolExecutionError(f"exiftool-Ausgabe ist kein gültiges JSON: {error}") from error
        return records
