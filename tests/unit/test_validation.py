import os
import tempfile
import unittest
from pathlib import Path

from filemeta2json.errors import InvalidInputPathError, InvalidOutputPathError
from filemeta2json.validation import validate_input_path, validate_output_path


class ValidateInputPathTest(unittest.TestCase):
    def test_existing_directory_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(validate_input_path(tmp), Path(tmp))

    def test_missing_path_is_rejected(self):
        with self.assertRaises(InvalidInputPathError):
            validate_input_path("/definitely/not/here")

    def test_blank_path_is_rejected(self):
        with self.assertRaises(InvalidInputPathError):
            validate_input_path("   ")


@unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root ignoriert Dateirechte")
class PermissionHintsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def _restrict(self, path, mode):
        original = path.stat().st_mode
        path.chmod(mode)
        self.addCleanup(path.chmod, original)

    def test_unreadable_input_names_problem_and_fix(self):
        locked = self.dir / "locked"
        locked.mkdir()
        self._restrict(locked, 0o000)
        with self.assertRaisesRegex(InvalidInputPathError, "(?s)Leseberechtigung.*chmod"):
            validate_input_path(str(locked))

    def test_unwritable_output_directory_names_problem_and_fix(self):
        readonly = self.dir / "readonly"
        readonly.mkdir()
        self._restrict(readonly, 0o500)
        with self.assertRaisesRegex(InvalidOutputPathError, "(?s)Schreibberechtigung.*anderen Ausgabepfad"):
            validate_output_path(str(readonly / "out.json"))

    def test_unwritable_existing_output_file_is_rejected(self):
        target = self.dir / "out.json"
        target.write_text("x")
        self._restrict(target, 0o400)
        with self.assertRaises(InvalidOutputPathError):
            validate_output_path(str(target))


class MessageHintsTest(unittest.TestCase):
    def test_missing_input_hints_at_quoting_paths_with_spaces(self):
        with self.assertRaisesRegex(InvalidInputPathError, "Anführungszeichen"):
            validate_input_path("/definitely/not/here")

    def test_missing_output_directory_hints_at_mkdir(self):
        with self.assertRaisesRegex(InvalidOutputPathError, "mkdir"):
            validate_output_path("/definitely/not/here/out.json")


class ValidateOutputPathTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def test_new_file_in_existing_directory_is_accepted(self):
        target = self.dir / "out.json"
        self.assertEqual(validate_output_path(str(target)), target)

    def test_directory_is_rejected(self):
        with self.assertRaises(InvalidOutputPathError):
            validate_output_path(str(self.dir))

    def test_missing_parent_directory_is_rejected(self):
        with self.assertRaises(InvalidOutputPathError):
            validate_output_path(str(self.dir / "nope" / "out.json"))

    def test_blank_path_is_rejected(self):
        with self.assertRaises(InvalidOutputPathError):
            validate_output_path("")


if __name__ == "__main__":
    unittest.main()
