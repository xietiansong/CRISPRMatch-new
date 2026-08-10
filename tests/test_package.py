import importlib
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from crisprmatch.resources import ui_path


def test_bundled_ui_resources_exist():
    for filename in (
        "start.ui",
        "split_lanes.ui",
        "flash_merge.ui",
        "show_sampletable.ui",
        "show_fasta.ui",
        "show_result.ui",
    ):
        assert Path(ui_path(filename)).is_file()


def test_gui_modules_import_from_an_arbitrary_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    for module in (
        "crisprmatch.main",
        "crisprmatch.split_gui",
        "crisprmatch.merge_gui",
    ):
        importlib.import_module(module)


def test_cli_version_does_not_load_gui():
    completed = subprocess.run(
        [sys.executable, "-m", "crisprmatch.cli", "--version"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0
    assert completed.stdout.strip() == "crisprmatch 0.1.0"


@pytest.mark.integration
@pytest.mark.parametrize("executable", ["bwa", "samtools", "flash"])
def test_conda_environment_contains_external_tools(executable):
    assert shutil.which(executable), f"{executable} is missing from PATH"
