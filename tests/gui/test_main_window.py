from pathlib import Path
from shutil import rmtree
from uuid import uuid4

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QHeaderView

from image_format_converter.config import AppConfigStore
from image_format_converter.main_window import MainWindow


def test_window_shows_output_path_and_target_formats(qtbot, tmp_path: Path):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    assert str(tmp_path) in window.output_path_label.text()
    assert window.format_combo.count() == 5
    assert window.add_files_button.text() == "添加图片"
    assert window.drop_zone.minimumHeight() >= 120
    header = window.file_table.horizontalHeader()
    assert header.sectionResizeMode(0) == QHeaderView.ResizeMode.Stretch
    assert header.sectionResizeMode(1) == QHeaderView.ResizeMode.Fixed
    assert header.sectionResizeMode(2) == QHeaderView.ResizeMode.Fixed
    assert header.sectionResizeMode(3) == QHeaderView.ResizeMode.Fixed
    assert window.file_table.columnWidth(1) >= 96
    assert window.file_table.columnWidth(2) >= 88
    assert window.file_table.columnWidth(3) >= 36


def test_add_files_populates_queue(qtbot, tmp_path: Path):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    files = [tmp_path / "a.jpg", tmp_path / "b.png"]
    window.add_files(files)

    assert window._queued_files == files
    assert window.file_table.rowCount() == 2
    assert window.file_table.item(0, 0).text() == "a"
    assert window.file_table.item(0, 1).text() == "待处理"
    assert window.file_table.item(0, 2).text() == "JPG"
    assert window.file_table.item(1, 0).text() == "b"
    assert window.file_table.item(1, 1).text() == "待处理"
    assert window.file_table.item(1, 2).text() == "PNG"
    assert bool(window.file_table.item(0, 0).flags() & Qt.ItemFlag.ItemIsEditable)
    assert not bool(window.file_table.item(0, 1).flags() & Qt.ItemFlag.ItemIsEditable)
    assert not bool(window.file_table.item(0, 2).flags() & Qt.ItemFlag.ItemIsEditable)
    assert window.file_table.item(0, 1).textAlignment() == int(Qt.AlignmentFlag.AlignCenter)
    assert window.file_table.item(0, 2).textAlignment() == int(Qt.AlignmentFlag.AlignCenter)
    assert window.file_table.cellWidget(0, 3) is not None


def test_change_output_path_updates_label(qtbot, tmp_path: Path):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    newer = tmp_path / "exports"
    window.set_output_directory(newer)

    assert str(newer) in window.output_path_label.text()


def test_choose_output_directory_updates_label_and_persists(qtbot, tmp_path: Path, monkeypatch):
    root_path = Path.cwd() / f".gui-output-dir-{uuid4().hex}"
    root_path.mkdir(parents=True, exist_ok=False)
    try:
        store = AppConfigStore(root_path / "config.json")
        window = MainWindow(default_output_dir=root_path, config_store=store)
        qtbot.addWidget(window)

        newer = root_path / "exports"
        monkeypatch.setattr(
            QFileDialog,
            "getExistingDirectory",
            lambda *args, **kwargs: str(newer),
        )

        window.choose_output_directory()

        assert str(newer) in window.output_path_label.text()
        assert store.load().default_output_dir == newer
    finally:
        rmtree(root_path, ignore_errors=True)


def test_choose_input_files_populates_queue(qtbot, tmp_path: Path, monkeypatch):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    files = [tmp_path / "one.jpg", tmp_path / "two.png"]
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileNames",
        lambda *args, **kwargs: ([str(path) for path in files], ""),
    )

    window.choose_input_files()

    assert window._queued_files == files
    assert window.file_table.rowCount() == 2


def test_delete_button_removes_row_from_queue(qtbot, tmp_path: Path):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    files = [tmp_path / "one.jpg", tmp_path / "two.png"]
    window.add_files(files)

    delete_button = window.file_table.cellWidget(0, 3)
    qtbot.mouseClick(delete_button, Qt.MouseButton.LeftButton)

    assert window._queued_files == [files[1]]
    assert window.file_table.rowCount() == 1
    assert window.file_table.item(0, 0).text() == "two"


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
        assert window.file_table.rowCount() == 0
    finally:
        rmtree(root_path, ignore_errors=True)


def test_convert_current_batch_removes_successful_rows_and_keeps_failures(qtbot):
    root_path = Path.cwd() / f".gui-convert-{uuid4().hex}"
    root_path.mkdir(parents=True, exist_ok=False)
    try:
        bad = root_path / "bad.png"
        good = root_path / "sample.png"
        with bad.open("wb") as fp:
            Image.new("RGB", (12, 12), "red").save(fp, format="PNG")
        with good.open("wb") as fp:
            Image.new("RGB", (12, 12), "green").save(fp, format="PNG")

        store = AppConfigStore(root_path / "config.json")
        store.save_default_output_dir(root_path / "out")
        window = MainWindow(default_output_dir=store.load().default_output_dir)
        qtbot.addWidget(window)
        window.add_files([bad, good])
        window.file_table.item(0, 0).setText("   ")
        window.file_table.item(1, 0).setText("封面图")
        window.format_combo.setCurrentText("JPG")

        window.convert_current_batch()

        assert window.status_label.text() == "成功 1 张，失败 1 张"
        assert window.file_table.rowCount() == 1
        assert window._queued_files == [bad]
        assert window.file_table.item(0, 1).text() == "文件名无效"
        assert window.file_table.item(0, 2).text() == "PNG"
        assert len(list((root_path / "out").glob("封面图*.jpg"))) == 1
    finally:
        rmtree(root_path, ignore_errors=True)
