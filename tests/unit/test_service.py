import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from filemeta2json.report import FileMetadata
from filemeta2json.service import collect_metadata


class FakeReader:
    def __init__(self, records):
        self._records = records
        self.received = None

    def read(self, files):
        self.received = list(files)
        return self._records


class CollectMetadataTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        (self.root / "a.jpg").write_bytes(b"x")
        (self.root / "b.txt").write_bytes(b"x")

    def test_passes_scanned_files_to_reader(self):
        reader = FakeReader([])
        collect_metadata(self.root, reader)
        self.assertEqual(reader.received, [self.root / "a.jpg", self.root / "b.txt"])

    def test_files_without_embedded_metadata_are_omitted(self):
        reader = FakeReader([
            {"SourceFile": str(self.root / "a.jpg"), "EXIF:Make": "x"},
            {"SourceFile": str(self.root / "b.txt"), "File:FileType": "TXT"},
        ])
        self.assertEqual(collect_metadata(self.root, reader),
                         [FileMetadata(str(self.root / "a.jpg"), {"EXIF:Make": "x"})])

    def test_result_is_sorted_by_path(self):
        reader = FakeReader([
            {"SourceFile": str(self.root / "b.txt"), "XMP:Title": "b"},
            {"SourceFile": str(self.root / "a.jpg"), "XMP:Title": "a"},
        ])
        paths = [e.path for e in collect_metadata(self.root, reader)]
        self.assertEqual(paths, sorted(paths))

    def test_unencodable_filenames_are_skipped_and_reported(self):
        bad = Path(os.fsdecode(b"/x/caf\xe9.jpg"))
        good = self.root / "a.jpg"
        reader, skipped = FakeReader([]), []
        with unittest.mock.patch("filemeta2json.service.collect_files", return_value=[bad, good]):
            collect_metadata(self.root, reader, on_skipped=skipped.append)
        self.assertEqual(reader.received, [good])
        self.assertEqual(skipped, [bad])

    def test_no_records_yields_empty_list(self):
        self.assertEqual(collect_metadata(self.root, FakeReader([])), [])


if __name__ == "__main__":
    unittest.main()
