import os
import shutil
import tempfile
from pathlib import Path

import pytest

_temp_root = Path(__file__).resolve().parents[2] / ".pytest-tmp"
_temp_root.mkdir(parents=True, exist_ok=True)
os.environ["TMP"] = str(_temp_root)
os.environ["TEMP"] = str(_temp_root)
os.environ["TMPDIR"] = str(_temp_root)
tempfile.tempdir = str(_temp_root)

from image_format_converter.main_window import MainWindow


@pytest.fixture
def tmp_path():
    path = Path(tempfile.mkdtemp(dir=_temp_root))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_window_shows_output_path_and_target_formats(qtbot, tmp_path: Path):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    assert str(tmp_path) in window.output_path_label.text()
    assert window.format_combo.count() == 5


def test_add_files_populates_queue(qtbot, tmp_path: Path):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    window.add_files([tmp_path / "a.jpg", tmp_path / "b.png"])

    assert window.file_table.rowCount() == 2


def test_change_output_path_updates_label(qtbot, tmp_path: Path):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    newer = tmp_path / "exports"
    window.set_output_directory(newer)

    assert str(newer) in window.output_path_label.text()
