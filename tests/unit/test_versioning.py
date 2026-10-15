import re
import unittest
from pathlib import Path

from filemeta2json import __version__

SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$")
CHANGELOG = Path(__file__).resolve().parents[2] / "CHANGELOG.md"


class VersioningTest(unittest.TestCase):
    def test_version_follows_semver(self):
        self.assertRegex(__version__, SEMVER)

    def test_changelog_documents_current_version(self):
        self.assertIn(f"## [{__version__}]", CHANGELOG.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
