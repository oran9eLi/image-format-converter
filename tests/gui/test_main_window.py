from pathlib import Path
from shutil import rmtree
from uuid import uuid4

from PIL import Image

from image_format_converter.config import AppConfigStore
from image_format_converter.main_window import MainWindow


def test_window_shows_output_path_and_target_formats(qtbot, tmp_path: Path):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    assert str(tmp_path) in window.output_path_label.text()
    assert window.format_combo.count() == 5


def test_add_files_populates_queue(qtbot, tmp_path: Path):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    files = [tmp_path / "a.jpg", tmp_path / "b.png"]
    window.add_files(files)

    assert window._queued_files == files
    assert window.file_table.rowCount() == 2
    assert window.file_table.item(0, 0).text() == str(files[0])
    assert window.file_table.item(0, 1).text() == "待处理"
    assert window.file_table.item(0, 2).text() == "PNG"
    assert window.file_table.item(1, 0).text() == str(files[1])
    assert window.file_table.item(1, 1).text() == "待处理"
    assert window.file_table.item(1, 2).text() == "PNG"


def test_change_output_path_updates_label(qtbot, tmp_path: Path):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    newer = tmp_path / "exports"
    window.set_output_directory(newer)

    assert str(newer) in window.output_path_label.text()


def test_convert_button_runs_batch_and_updates_status(qtbot):
    root_path = Path.cwd() / f".gui-convert-{uuid4().hex}"
    root_path.mkdir(parents=True, exist_ok=False)
    try:
        source = root_path / "sample.png"
        with source.open("wb") as fp:
            Image.new("RGB", (12, 12), "green").save(fp, format="PNG")

        store = AppConfigStore(root_path / "config.json")
        store.save_default_output_dir(root_path / "out")
        window = MainWindow(default_output_dir=store.load().default_output_dir)
        qtbot.addWidget(window)
        window.add_files([source])

        assert hasattr(window, "convert_current_batch")
        window.convert_current_batch()

        assert "成功 1 张" in window.status_label.text()
        assert (root_path / "out" / "sample.png").exists()
    finally:
        rmtree(root_path, ignore_errors=True)
