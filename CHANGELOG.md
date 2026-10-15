# Changelog

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach [SemVer](https://semver.org/lang/de/).

## [1.1.0] - 2026-10-11

### Added
- Fehlt `exiftool`, nennt das Tool den passenden Installationsbefehl für Betriebssystem
  und vorhandenen Paketmanager (Homebrew, MacPorts, apt, dnf, yum, pacman, zypper, apk, Nix, winget, Chocolatey, Scoop).
- Hilfetexte bei fehlenden Lese-/Schreibrechten, nicht vorhandenem Zielverzeichnis,
  nicht ausführbarem `exiftool` und nicht schreibbarer Ausgabedatei (Exit-Code 2).

## [1.0.1] - 2026-10-11

### Fixed
- Dateien, deren Name nicht als UTF-8 kodierbar ist (Linux), brachen den ganzen Lauf mit `UnicodeEncodeError` ab.
  Sie werden jetzt übersprungen und auf stderr gemeldet.

## [1.0.0] - 2026-10-11

### Added
- Rekursives Durchsuchen eines Pfades (Datei oder Verzeichnis).
- Auslesen eingebetteter Metadaten via `exiftool`; Ausgabe als JSON mit absolutem Dateipfad.
- Dateien ohne eingebettete Metadaten werden ausgelassen.
- Option `-o/--output` zum Schreiben in eine Datei, `--version`.
- Exit-Codes: 0 OK, 2 ungültige Argumente, 3 `exiftool` fehlt/defekt.
