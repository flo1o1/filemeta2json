import os
import unittest
from pathlib import Path

from filemeta2json.filename_check import is_utf8_encodable

INVALID_UTF8_NAME = Path(os.fsdecode(b"/tmp/caf\xe9.jpg"))


class IsUtf8EncodableTest(unittest.TestCase):
    def test_plain_and_unicode_names_are_encodable(self):
        self.assertTrue(is_utf8_encodable(Path("/tmp/Übergröße 日本.jpg")))

    def test_invalid_utf8_bytes_are_not_encodable(self):
        self.assertFalse(is_utf8_encodable(INVALID_UTF8_NAME))


if __name__ == "__main__":
    unittest.main()
