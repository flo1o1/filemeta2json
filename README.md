# filemeta2json

Scans a file or directory (recursively), reads embedded metadata
(EXIF, XMP, IPTC, ID3, PDF, …) and prints it as JSON with the absolute path.

Requirements: Python ≥ 3.9 (not for the binary) and [`exiftool`](https://exiftool.org) (`brew install exiftool`). No Python dependencies.

### Standalone binary

Download the file for your system from the [latest release](https://github.com/flo1o1/filemeta2json/releases/latest)
(Linux x86_64, macOS arm64/x86_64, Windows x86_64). No Python needed, but `exiftool` must still be installed.

```sh
chmod +x filemeta2json-macos-arm64   # macOS/Linux only
./filemeta2json-macos-arm64 ~/Bilder
```

On macOS the unsigned binary may be blocked by Gatekeeper: `xattr -d com.apple.quarantine <file>`.

### From source

```sh
python3 -m filemeta2json ~/Bilder                 # JSON to stdout
python3 -m filemeta2json ~/Bilder -o meta.json    # JSON to file
```

Output:

```json
[
  { "path": "/Users/me/Bilder/a.jpg", "metadata": { "EXIF:Make": "Canon", "XMP:Title": "…" } }
]
```

- Keys have the form `Group:Tag`. File system, tool and derived values
  (groups `System`, `File`, `ExifTool`, `Composite`) are not printed.
- Files without embedded metadata are omitted from the output.
- File names containing a line break are not supported.
- Exit codes: `0` OK, `2` invalid arguments, `3` `exiftool` missing or produced no output.

## Tests

```sh
python3 -m unittest discover -s tests -t .
```

`tests/unit`: isolated tests with fakes. `tests/regression`: end-to-end against the real `exiftool` (skipped without `exiftool`).

## Versioning

SemVer. Single version source: `filemeta2json/__init__.py`. Every change is recorded in `CHANGELOG.md`.
- MAJOR: incompatible change to the JSON format or the CLI.
- MINOR: new, backward-compatible feature.
- PATCH: bug fix.

## License

[MIT](LICENSE)
