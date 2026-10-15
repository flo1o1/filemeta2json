import unittest

from filemeta2json.metadata_filter import extract_embedded_metadata


class ExtractEmbeddedMetadataTest(unittest.TestCase):
    def test_keeps_embedded_groups(self):
        record = {"SourceFile": "/a.jpg", "EXIF:Make": "Canon", "XMP:Title": "T"}
        self.assertEqual(extract_embedded_metadata(record),
                         {"EXIF:Make": "Canon", "XMP:Title": "T"})

    def test_removes_non_embedded_groups(self):
        record = {"SourceFile": "/a", "System:FileSize": "1 kB", "File:FileType": "PNG",
                  "ExifTool:Error": "Unknown file type", "Composite:ImageSize": "1x1"}
        self.assertEqual(extract_embedded_metadata(record), {})

    def test_removes_source_file(self):
        self.assertEqual(extract_embedded_metadata({"SourceFile": "/a"}), {})

    def test_keeps_key_without_group(self):
        self.assertEqual(extract_embedded_metadata({"Foo": 1}), {"Foo": 1})

    def test_group_match_is_exact(self):
        self.assertEqual(extract_embedded_metadata({"FileX:Tag": 1}), {"FileX:Tag": 1})

    def test_does_not_mutate_input(self):
        record = {"SourceFile": "/a", "EXIF:Make": "x"}
        extract_embedded_metadata(record)
        self.assertEqual(record, {"SourceFile": "/a", "EXIF:Make": "x"})


if __name__ == "__main__":
    unittest.main()
