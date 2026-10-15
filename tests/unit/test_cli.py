import io
import json
import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from filemeta2json import __version__
from filemeta2json.cli import (EXIT_EXIFTOOL_PROBLEM, EXIT_INVALID_ARGUMENTS,
                               EXIT_OK, main)
from filemeta2json.errors import ExifToolExecutionError, ExifToolNotFoundError


class StubReader:
    def __init__(self, records=(), error=None):
        self._records = list(records)
        self._error = error

    def read(self, files):
        if self._error:
            raise self._error
        return self._records


class MainTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        (self.root / "a.jpg").write_bytes(b"x")
        self.records = [{"SourceFile": str(self.root / "a.jpg"), "EXIF:Make": "Canon"}]
        self.stdout, self.stderr = io.StringIO(), io.StringIO()

    def _run(self, argv, reader=None):
        return main(argv, reader or StubReader(self.records), self.stdout, self.stderr,
                    install_hint=lambda: "HINWEIS: brew install exiftool")

    def test_prints_json_to_stdout_by_default(self):
        self.assertEqual(self._run([str(self.root)]), EXIT_OK)
        self.assertEqual(json.loads(self.stdout.getvalue()),
                         [{"path": str(self.root / "a.jpg"), "metadata": {"EXIF:Make": "Canon"}}])

    def test_writes_to_file_and_keeps_stdout_empty(self):
        target = self.root / "out.json"
        self.assertEqual(self._run([str(self.root), "-o", str(target)]), EXIT_OK)
        self.assertEqual(self.stdout.getvalue(), "")
        self.assertEqual(json.loads(target.read_text(encoding="utf-8"))[0]["metadata"],
                         {"EXIF:Make": "Canon"})

    def test_missing_input_path_returns_invalid_arguments(self):
        self.assertEqual(self._run(["/not/here"]), EXIT_INVALID_ARGUMENTS)
        self.assertIn("existiert nicht", self.stderr.getvalue())

    def test_invalid_output_path_returns_invalid_arguments_and_writes_nothing(self):
        self.assertEqual(self._run([str(self.root), "-o", str(self.root)]), EXIT_INVALID_ARGUMENTS)
        self.assertEqual(self.stdout.getvalue(), "")

    def test_missing_exiftool_returns_exiftool_problem(self):
        reader = StubReader(error=ExifToolNotFoundError("weg"))
        self.assertEqual(self._run([str(self.root)], reader), EXIT_EXIFTOOL_PROBLEM)
        self.assertIn("weg", self.stderr.getvalue())

    def test_missing_exiftool_prints_install_hint(self):
        reader = StubReader(error=ExifToolNotFoundError("weg"))
        self._run([str(self.root)], reader)
        self.assertIn("HINWEIS: brew install exiftool", self.stderr.getvalue())

    def test_other_exiftool_problem_does_not_print_install_hint(self):
        reader = StubReader(error=ExifToolExecutionError("kaputt"))
        self.assertEqual(self._run([str(self.root)], reader), EXIT_EXIFTOOL_PROBLEM)
        self.assertNotIn("HINWEIS", self.stderr.getvalue())

    def test_unwritable_output_file_returns_invalid_arguments_with_hint(self):
        with unittest.mock.patch.object(Path, "write_text", side_effect=OSError("Disk full")):
            code = self._run([str(self.root), "-o", str(self.root / "out.json")])
        self.assertEqual(code, EXIT_INVALID_ARGUMENTS)
        self.assertIn("Disk full", self.stderr.getvalue())
        self.assertIn("anderen Ausgabepfad", self.stderr.getvalue())

    def test_unencodable_filename_is_warned_about_and_run_succeeds(self):
        bad = Path(os.fsdecode(b"/x/caf\xe9.jpg"))
        with unittest.mock.patch("filemeta2json.service.collect_files", return_value=[bad]):
            self.assertEqual(self._run([str(self.root)], StubReader()), EXIT_OK)
        self.assertIn("Warnung", self.stderr.getvalue())
        self.assertIn("\\udce9", self.stderr.getvalue())
        self.assertEqual(json.loads(self.stdout.getvalue()), [])

    def test_version_flag_exits_with_version(self):
        out = io.StringIO()
        with self.assertRaises(SystemExit) as raised, \
                unittest.mock.patch("sys.stdout", out):
            self._run(["--version"])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn(__version__, out.getvalue())


if __name__ == "__main__":
    unittest.main()
