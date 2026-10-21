"""Offline tests: never invoke Nuitka, Inno Setup, signing or release tools."""

import os
import platform
import sys
from unittest import TestCase
from unittest.mock import patch

from installer_builder2 import InstallerBuilder, _format_nuitka_datafiles, format_data_file, run_nuitka

class TestDataFileFormatter(TestCase):
    def test_format_data_file(self):
        # Test single file
        self.assertEqual(
            format_data_file("file.txt"),
            f"{os.path.abspath('file.txt')}=file.txt"
        )

        # Test directory
        self.assertEqual(
            format_data_file("testdir/"),
            f"{os.path.abspath('testdir')}=testdir/"
        )

        # Test pattern
        self.assertEqual(
            format_data_file("dir/*.txt"),
            f"{os.path.abspath('dir')}/*.txt=dir/"
        )

        # Test pre-formatted string
        self.assertEqual(
            format_data_file("source=target"),
            "source=target"
        )

    def test_deployment_flag(self):
        # Create builder with deployment enabled
        builder = InstallerBuilder("TestApp", enable_deployment=True)
        self.assertTrue(builder.enable_deployment)

        # Create builder with deployment disabled (default)
        builder = InstallerBuilder("TestApp")
        self.assertFalse(builder.enable_deployment)

    def test_installer_builder_config(self):

        builder = InstallerBuilder(
            "TestApp",
            version="1.2.3",
            company_name="Test Company",
            console=True
        )

        self.assertEqual(builder.app_name, "TestApp")
        self.assertEqual(builder.version, "1.2.3")
        self.assertEqual(builder.company_name, "Test Company")
        self.assertTrue(builder.console)

    def test_data_file_handling(self):

        builder = InstallerBuilder("TestApp")
        builder.data_files = ["test.txt", "data/*.dat"]
        builder.data_directories = ["assets/"]

        # Test that data files are properly formatted
        formatted_files = _format_nuitka_datafiles(builder.data_files)
        self.assertTrue(any("test.txt" in f for f in formatted_files))
        self.assertTrue(any("*.dat" in f for f in formatted_files))

    def test_platform_specific(self):

        builder = InstallerBuilder("TestApp")

        if platform.system() == "Windows":
            # Test Windows-specific paths
            self.assertTrue(str(builder.dist_path).endswith('dist'))
        elif platform.system() == "Darwin":
            # Test macOS-specific paths
            self.assertTrue(str(builder.dist_path).endswith('dist'))

    def test_compile_distribution_passes_data_and_deployment_to_nuitka(self):
        builder = InstallerBuilder(
            "TestApp",
            main_module="main.py",
            console=True,
            enable_deployment=True,
            data_files=["test.txt", "data/*.dat", "source=target"],
            data_directories=["assets/"],
        )
        with patch("installer_builder2.subprocess.check_call") as execute:
            builder.compile_distribution()

        execute.assert_called_once_with([
            sys.executable, "-m", "nuitka", "--standalone",
            "--include-data-files=" + os.path.abspath("test.txt") + "=test.txt",
            "--include-data-files=" + os.path.abspath("data") + "/*.dat=data/",
            "--include-data-files=source=target",
            "--include-data-dir=" + os.path.abspath("assets") + "=assets/",
            "--assume-yes-for-downloads", "--output-dir=dist", "--deployment",
            '--windows-product-name="TestApp"', "--macos-app-name=TestApp",
            "--windows-product-version=0.0.0.0", "--macos-app-version=0.0",
            "main.py",
        ])

    def test_default_run_keeps_deployment_disabled(self):
        with patch("installer_builder2.subprocess.check_call") as execute:
            run_nuitka("main.py", console=True)

        execute.assert_called_once_with([
            sys.executable, "-m", "nuitka", "--standalone",
            "--assume-yes-for-downloads", "--output-dir=dist", "main.py",
        ])
