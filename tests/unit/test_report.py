import json
import unittest

from filemeta2json.report import FileMetadata, to_json


class ToJsonTest(unittest.TestCase):
    def test_empty_input_yields_empty_array(self):
        self.assertEqual(json.loads(to_json([])), [])

    def test_entry_has_path_and_metadata(self):
        entries = [FileMetadata("/a.jpg", {"EXIF:Make": "Canon"})]
        self.assertEqual(json.loads(to_json(entries)),
                         [{"path": "/a.jpg", "metadata": {"EXIF:Make": "Canon"}}])

    def test_umlauts_are_not_escaped(self):
        self.assertIn("Müller", to_json([FileMetadata("/a", {"XMP:Creator": "Müller"})]))

    def test_output_ends_with_newline(self):
        self.assertTrue(to_json([]).endswith("\n"))

    def test_preserves_input_order(self):
        entries = [FileMetadata("/b", {"k": 1}), FileMetadata("/a", {"k": 2})]
        self.assertEqual([e["path"] for e in json.loads(to_json(entries))], ["/b", "/a"])


if __name__ == "__main__":
    unittest.main()
