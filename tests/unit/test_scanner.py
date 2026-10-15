import os
import tempfile
import unittest
from pathlib import Path

from filemeta2json.scanner import collect_files


class CollectFilesTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()

    def _touch(self, relative: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x")
        return path

    def test_single_file_returns_only_that_file(self):
        file = self._touch("a.txt")
        self.assertEqual(collect_files(file), [file])

    def test_empty_directory_returns_empty_list(self):
        self.assertEqual(collect_files(self.root), [])

    def test_directory_is_searched_recursively_and_sorted(self):
        deep = self._touch("b/c/deep.txt")
        top = self._touch("a.txt")
        self.assertEqual(collect_files(self.root), [top, deep])

    def test_directories_are_not_returned(self):
        (self.root / "empty_dir").mkdir()
        self._touch("a.txt")
        self.assertEqual([p.name for p in collect_files(self.root)], ["a.txt"])

    def test_relative_input_yields_absolute_paths(self):
        self._touch("a.txt")
        previous = os.getcwd()
        self.addCleanup(os.chdir, previous)
        os.chdir(self.root)
        result = collect_files(Path("."))
        self.assertTrue(all(p.is_absolute() for p in result))
        self.assertEqual(len(result), 1)

    def test_symlink_to_directory_is_not_followed(self):
        self._touch("real/a.txt")
        os.symlink(self.root / "real", self.root / "link")
        self.assertEqual(len(collect_files(self.root)), 1)

    def test_broken_symlink_is_skipped(self):
        os.symlink(self.root / "missing", self.root / "broken")
        self.assertEqual(collect_files(self.root), [])


if __name__ == "__main__":
    unittest.main()
