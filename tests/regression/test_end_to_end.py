"""Regression tests against the real `exiftool`; guard the overall behavior."""

import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
EXIFTOOL_AVAILABLE = shutil.which("exiftool") is not None


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))


def minimal_png() -> bytes:
    """Smallest valid 1x1 PNG without metadata."""
    header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    pixel = zlib.compress(b"\x00\xff\xff\xff")
    return (b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", header)
            + _png_chunk(b"IDAT", pixel) + _png_chunk(b"IEND", b""))


def write_png_with_title(path: Path, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(minimal_png())
    # Arguments go via stdin: Windows command lines cannot carry Unicode to exiftool.
    arguments = f"-XMP:Title={title}\n{path}\n"
    result = subprocess.run(["exiftool", "-overwrite_original", "-charset", "filename=utf8",
                             "-charset", "utf8", "-@", "-"],
                            input=arguments.encode("utf-8"), capture_output=True)
    if b"1 image files updated" not in result.stdout:
        raise RuntimeError(result.stdout + result.stderr)


def run_cli(*arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "filemeta2json", *arguments],
                          cwd=REPOSITORY_ROOT, capture_output=True, text=True, encoding="utf-8")


@unittest.skipUnless(EXIFTOOL_AVAILABLE, "exiftool not installed")
class EndToEndRegressionTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()

    def _entries(self, *arguments):
        result = run_cli(str(self.root), *arguments)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_file_with_metadata_is_reported_with_absolute_path(self):
        image = self.root / "bild.png"
        write_png_with_title(image, "Sonnenuntergang")
        entries = self._entries()
        self.assertEqual([e["path"] for e in entries], [str(image)])
        self.assertEqual(entries[0]["metadata"]["XMP:Title"], "Sonnenuntergang")

    def test_only_embedded_metadata_groups_are_reported(self):
        write_png_with_title(self.root / "bild.png", "T")
        groups = {key.split(":")[0] for key in self._entries()[0]["metadata"]}
        self.assertTrue(groups.isdisjoint({"System", "ExifTool", "File", "Composite"}))

    def test_file_without_metadata_is_omitted(self):
        (self.root / "notes.txt").write_text("hallo")
        self.assertEqual(self._entries(), [])

    def test_technical_header_properties_count_as_metadata(self):
        (self.root / "plain.png").write_bytes(minimal_png())
        metadata = self._entries()[0]["metadata"]
        self.assertEqual((metadata["PNG:ImageWidth"], metadata["PNG:ImageHeight"]), (1, 1))

    def test_unknown_file_type_does_not_abort_run(self):
        (self.root / "data.unknownformat").write_bytes(b"\x00\x01\x02")
        write_png_with_title(self.root / "bild.png", "T")
        self.assertEqual(len(self._entries()), 1)

    def test_nested_directories_are_searched_and_sorted(self):
        write_png_with_title(self.root / "z" / "deep" / "z.png", "z")
        write_png_with_title(self.root / "a.png", "a")
        paths = [e["path"] for e in self._entries()]
        self.assertEqual(paths, [str(self.root / "a.png"), str(self.root / "z" / "deep" / "z.png")])

    def test_unicode_and_spaces_in_path_and_value(self):
        image = self.root / "Übergröße Bild ß.png"
        write_png_with_title(image, "Grüße – 日本")
        entry = self._entries()[0]
        self.assertEqual(entry["path"], str(image))
        self.assertEqual(entry["metadata"]["XMP:Title"], "Grüße – 日本")

    def test_single_file_as_input(self):
        image = self.root / "bild.png"
        write_png_with_title(image, "T")
        result = run_cli(str(image))
        self.assertEqual(json.loads(result.stdout)[0]["path"], str(image))

    def test_output_file_matches_stdout(self):
        write_png_with_title(self.root / "bild.png", "T")
        target = Path(tempfile.mkdtemp()) / "out.json"
        self.addCleanup(shutil.rmtree, target.parent)
        stdout_run = run_cli(str(self.root))
        file_run = run_cli(str(self.root), "-o", str(target))
        self.assertEqual(file_run.returncode, 0, file_run.stderr)
        self.assertEqual(file_run.stdout, "")
        self.assertEqual(target.read_text(encoding="utf-8"), stdout_run.stdout)

    @unittest.skipIf(os.name == "nt", "Windows file names are always valid Unicode")
    def test_non_utf8_filename_is_skipped_with_warning_and_others_still_reported(self):
        try:
            with open(os.path.join(os.fsencode(self.root), b"caf\xe9.txt"), "wb") as handle:
                handle.write(b"x")
        except OSError:
            self.skipTest("Dateisystem erlaubt keine Nicht-UTF-8-Dateinamen (z. B. macOS)")
        write_png_with_title(self.root / "bild.png", "T")
        result = run_cli(str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([e["path"] for e in json.loads(result.stdout)], [str(self.root / "bild.png")])
        self.assertIn("Warning", result.stderr)

    def test_empty_directory_yields_empty_json_array(self):
        self.assertEqual(self._entries(), [])

    def test_missing_input_path_fails_with_exit_code_2(self):
        result = run_cli("/does/not/exist")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")



class MissingExifToolRegressionTest(unittest.TestCase):
    def test_missing_exiftool_gives_install_instructions_and_exit_code_3(self):
        with tempfile.TemporaryDirectory() as empty_path_dir, tempfile.TemporaryDirectory() as data:
            (Path(data) / "a.txt").write_text("x")
            environment = {"PATH": empty_path_dir}
            result = subprocess.run(
                [sys.executable, "-m", "filemeta2json", data], cwd=REPOSITORY_ROOT,
                capture_output=True, text=True, env={**environment, "PYTHONPATH": str(REPOSITORY_ROOT)})
        self.assertEqual(result.returncode, 3)
        self.assertIn("not found", result.stderr)
        self.assertIn("exiftool -ver", result.stderr)
        self.assertTrue("exiftool.org" in result.stderr or "install exiftool" in result.stderr
                        or "install libimage-exiftool-perl" in result.stderr, result.stderr)


if __name__ == "__main__":
    unittest.main()
