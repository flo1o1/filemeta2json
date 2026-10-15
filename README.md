# filemeta2json

Durchsucht eine Datei oder ein Verzeichnis (rekursiv), liest eingebettete Metadaten
(EXIF, XMP, IPTC, ID3, PDF, …) und gibt sie mit absolutem Pfad als JSON aus.

Voraussetzung: Python ≥ 3.9 und [`exiftool`](https://exiftool.org) (`brew install exiftool`). Keine Python-Abhängigkeiten.

```sh
python3 -m filemeta2json ~/Bilder                 # JSON nach stdout
python3 -m filemeta2json ~/Bilder -o meta.json    # JSON in Datei
```

Ausgabe:

```json
[
  { "path": "/Users/me/Bilder/a.jpg", "metadata": { "EXIF:Make": "Canon", "XMP:Title": "…" } }
]
```

- Schlüssel haben die Form `Gruppe:Tag`. Dateisystem-, Tool- und abgeleitete Werte
  (Gruppen `System`, `File`, `ExifTool`, `Composite`) werden nicht ausgegeben.
- Dateien ohne eingebettete Metadaten fehlen in der Ausgabe.
- Dateinamen mit Zeilenumbruch werden nicht unterstützt.
- Exit-Codes: `0` OK, `2` ungültige Argumente, `3` `exiftool` fehlt oder liefert nichts.

## Tests

```sh
python3 -m unittest discover -s tests -t .
```

`tests/unit`: isolierte Tests mit Fakes. `tests/regression`: End-to-End gegen echtes `exiftool` (werden ohne `exiftool` übersprungen).

## Versionierung

SemVer. Einzige Versionsquelle: `filemeta2json/__init__.py`. Jede Änderung wird in `CHANGELOG.md` eingetragen.
- MAJOR: inkompatible Änderung des JSON-Formats oder der CLI.
- MINOR: neue, abwärtskompatible Funktion.
- PATCH: Fehlerkorrektur.

## Lizenz

[MIT](LICENSE)
