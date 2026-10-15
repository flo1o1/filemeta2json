import unittest

from filemeta2json.install_hints import DOWNLOAD_URL, HOMEBREW_URL, exiftool_install_hint


def available(*programs):
    return lambda program: "/bin/" + program if program in programs else None


class ExiftoolInstallHintTest(unittest.TestCase):
    def test_macos_with_homebrew(self):
        hint = exiftool_install_hint("darwin", available("brew"))
        self.assertIn("brew install exiftool", hint)
        self.assertNotIn("port install", hint)

    def test_macos_with_macports_only(self):
        self.assertIn("sudo port install p5-image-exiftool", exiftool_install_hint("darwin", available("port")))

    def test_macos_without_package_manager_points_to_download_and_homebrew(self):
        hint = exiftool_install_hint("darwin", available())
        self.assertIn(DOWNLOAD_URL, hint)
        self.assertIn(HOMEBREW_URL, hint)

    def test_linux_debian_family(self):
        self.assertIn("sudo apt-get install libimage-exiftool-perl",
                      exiftool_install_hint("linux", available("apt-get")))

    def test_linux_fedora_family(self):
        self.assertIn("sudo dnf install perl-Image-ExifTool", exiftool_install_hint("linux", available("dnf")))

    def test_linux_arch(self):
        self.assertIn("sudo pacman -S perl-image-exiftool", exiftool_install_hint("linux", available("pacman")))

    def test_linux_alpine(self):
        self.assertIn("sudo apk add exiftool", exiftool_install_hint("linux", available("apk")))

    def test_linux_lists_every_available_manager(self):
        hint = exiftool_install_hint("linux", available("apt-get", "brew"))
        self.assertIn("apt-get install", hint)
        self.assertIn("brew install exiftool", hint)

    def test_linux_without_package_manager_has_no_homebrew_advice(self):
        hint = exiftool_install_hint("linux", available())
        self.assertIn(DOWNLOAD_URL, hint)
        self.assertNotIn(HOMEBREW_URL, hint)

    def test_windows_winget(self):
        self.assertIn("winget install OliverBetz.ExifTool", exiftool_install_hint("win32", available("winget")))

    def test_windows_chocolatey_and_scoop(self):
        hint = exiftool_install_hint("win32", available("choco", "scoop"))
        self.assertIn("choco install exiftool", hint)
        self.assertIn("scoop install exiftool", hint)

    def test_unknown_platform_falls_back_to_download(self):
        self.assertIn(DOWNLOAD_URL, exiftool_install_hint("freebsd13", available("brew")))

    def test_hint_always_explains_how_to_verify(self):
        self.assertIn("exiftool -ver", exiftool_install_hint("linux", available()))


if __name__ == "__main__":
    unittest.main()
