# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning according to [SemVer](https://semver.org/).

## [1.3.0] - 2026-10-15

### Added
- Standalone binaries (PyInstaller) for Linux, macOS (arm64/x86_64) and Windows, built by GitHub Actions and attached to each `v*` release.

## [1.2.0] - 2026-10-15

### Changed
- All user-facing messages (errors, warnings, hints, `--help`), docs and code comments are now in English.

## [1.1.0] - 2026-10-11

### Added
- If `exiftool` is missing, the tool prints the matching install command for the operating system
  and available package manager (Homebrew, MacPorts, apt, dnf, yum, pacman, zypper, apk, Nix, winget, Chocolatey, Scoop).
- Help texts for missing read/write permissions, a missing target directory,
  a non-executable `exiftool` and an unwritable output file (exit code 2).

## [1.0.1] - 2026-10-11

### Fixed
- Files whose name cannot be encoded as UTF-8 (Linux) aborted the whole run with `UnicodeEncodeError`.
  They are now skipped and reported on stderr.

## [1.0.0] - 2026-10-11

### Added
- Recursive scan of a path (file or directory).
- Reads embedded metadata via `exiftool`; output as JSON with absolute file path.
- Files without embedded metadata are omitted.
- Option `-o/--output` to write to a file, `--version`.
- Exit codes: 0 OK, 2 invalid arguments, 3 `exiftool` missing/broken.
