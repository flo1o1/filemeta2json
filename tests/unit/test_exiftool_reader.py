import json
import subprocess
import unittest
from pathlib import Path

from filemeta2json.errors import ExifToolExecutionError, ExifToolNotFoundError
from filemeta2json.exiftool_reader import BASE_ARGUMENTS, ExifToolReader


class FakeRunner:
    """Ersetzt subprocess.run und merkt sich den Aufruf."""

    def __init__(self, stdout=b"[]", stderr=b"", returncode=0, error=None):
        self._result = subprocess.CompletedProcess([], returncode, stdout, stderr)
        self._error = error
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append((command, kwargs))
        if self._error:
            raise self._error
        return self._result


class ExifToolReaderTest(unittest.TestCase):
    def test_empty_file_list_does_not_call_exiftool(self):
        runner = FakeRunner()
        self.assertEqual(ExifToolReader(runner).read([]), [])
        self.assertEqual(runner.calls, [])

    def test_passes_paths_via_stdin_and_uses_base_arguments(self):
        runner = FakeRunner()
        ExifToolReader(runner, executable="et").read([Path("/a b/ä.jpg"), Path("/c.png")])
        command, kwargs = runner.calls[0]
        self.assertEqual(command, ["et", *BASE_ARGUMENTS])
        self.assertEqual(kwargs["input"], "/a b/ä.jpg\n/c.png".encode("utf-8"))

    def test_returns_parsed_records(self):
        records = [{"SourceFile": "/a", "EXIF:Make": "x"}]
        runner = FakeRunner(stdout=json.dumps(records).encode())
        self.assertEqual(ExifToolReader(runner).read([Path("/a")]), records)

    def test_returncode_1_with_json_is_not_an_error(self):
        runner = FakeRunner(stdout=b'[{"SourceFile": "/a"}]', returncode=1)
        self.assertEqual(ExifToolReader(runner).read([Path("/a")]), [{"SourceFile": "/a"}])

    def test_missing_executable_raises_not_found(self):
        runner = FakeRunner(error=FileNotFoundError())
        with self.assertRaises(ExifToolNotFoundError):
            ExifToolReader(runner).read([Path("/a")])

    def test_permission_error_raises_execution_error_with_chmod_hint(self):
        runner = FakeRunner(error=PermissionError())
        with self.assertRaisesRegex(ExifToolExecutionError, "chmod"):
            ExifToolReader(runner).read([Path("/a")])

    def test_empty_output_error_suggests_verifying_installation(self):
        runner = FakeRunner(stdout=b"", returncode=2)
        with self.assertRaisesRegex(ExifToolExecutionError, "exiftool -ver"):
            ExifToolReader(runner).read([Path("/a")])

    def test_empty_output_raises_execution_error_with_stderr(self):
        runner = FakeRunner(stdout=b"", stderr=b"boom", returncode=2)
        with self.assertRaisesRegex(ExifToolExecutionError, "boom"):
            ExifToolReader(runner).read([Path("/a")])

    def test_invalid_json_raises_execution_error(self):
        runner = FakeRunner(stdout=b"not json")
        with self.assertRaises(ExifToolExecutionError):
            ExifToolReader(runner).read([Path("/a")])


if __name__ == "__main__":
    unittest.main()
