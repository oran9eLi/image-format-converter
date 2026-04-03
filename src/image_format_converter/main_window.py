from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from image_format_converter.config import AppConfigStore
from image_format_converter.converter import ConversionService
from image_format_converter.widgets import DropZone

STATUS_COLUMN_WIDTH = 96
FORMAT_COLUMN_WIDTH = 88
ACTION_COLUMN_WIDTH = 44


class MainWindow(QWidget):
    def __init__(
        self,
        default_output_dir: Path | None,
        config_store: AppConfigStore | None = None,
        conversion_service: ConversionService | None = None,
    ):
        super().__init__()
        self._output_dir = default_output_dir
        self._config_store = config_store
        self._conversion_service = conversion_service or ConversionService()
        self._queued_files: list[Path] = []

        self.output_path_label = QLabel(self._format_output_dir())
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPG", "BMP", "WEBP", "ICO"])
        self.add_files_button = QPushButton("添加图片")
        self.add_files_button.clicked.connect(self.choose_input_files)
        self.output_path_button = QPushButton("更改路径")
        self.output_path_button.clicked.connect(self.choose_output_directory)
        self.convert_button = QPushButton("开始转换")
        self.convert_button.clicked.connect(self.convert_current_batch)
        self.status_label = QLabel("就绪")
        self.file_table = QTableWidget(0, 4)
        self.file_table.setHorizontalHeaderLabels(["文件", "状态", "格式", ""])
        self.file_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.SelectedClicked
        )
        header = self.file_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.file_table.setColumnWidth(1, STATUS_COLUMN_WIDTH)
        self.file_table.setColumnWidth(2, FORMAT_COLUMN_WIDTH)
        self.file_table.setColumnWidth(3, ACTION_COLUMN_WIDTH)

        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self.add_files)

        self._build_layout()

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        header.addWidget(self.output_path_label)
        header.addWidget(self.output_path_button)
        header.addWidget(self.add_files_button)
        header.addStretch(1)
        header.addWidget(QLabel("目标格式："))
        header.addWidget(self.format_combo)
        header.addWidget(self.convert_button)
        layout.addLayout(header)
        layout.addWidget(self.drop_zone)
        layout.addWidget(self.file_table)
        layout.addWidget(self.status_label)

    def _format_output_dir(self) -> str:
        return f"输出目录：{self._output_dir}" if self._output_dir else "输出目录：未设置"

    def set_output_directory(self, output_dir: Path | None) -> None:
        self._output_dir = output_dir
        self.output_path_label.setText(self._format_output_dir())
        if output_dir is not None and self._config_store is not None:
            self._config_store.save_default_output_dir(output_dir)

    def choose_output_directory(self) -> None:
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            str(self._output_dir) if self._output_dir is not None else "",
        )
        if selected_dir:
            self.set_output_directory(Path(selected_dir))

    def choose_input_files(self) -> None:
        selected_files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.webp *.gif)",
        )
        if selected_files:
            self.add_files([Path(file_path) for file_path in selected_files])

    def add_files(self, files: list[Path]) -> None:
        for file_path in files:
            self._queued_files.append(file_path)
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)
            self.file_table.setItem(row, 0, QTableWidgetItem(file_path.stem))
            self.file_table.setItem(row, 1, self._make_readonly_centered_item("待处理"))
            self.file_table.setItem(
                row,
                2,
                self._make_readonly_centered_item(file_path.suffix.lstrip(".").upper()),
            )
            self.file_table.setCellWidget(row, 3, self._make_delete_button())

    def convert_current_batch(self) -> None:
        if self._output_dir is None:
            self.status_label.setText("请先设置输出目录")
            return

        current_format = self.format_combo.currentText()
        output_stems = [
            self.file_table.item(row, 0).text() if self.file_table.item(row, 0) else path.stem
            for row, path in enumerate(self._queued_files)
        ]
        result = self._conversion_service.convert_files(
            self._queued_files,
            self._output_dir,
            current_format,
            output_stems=output_stems,
        )

        rows_to_remove: list[int] = []
        failed_files: list[Path] = []
        for row, (path, item) in enumerate(zip(self._queued_files, result.items)):
            if item.success:
                rows_to_remove.append(row)
                continue

            failed_files.append(path)
            self.file_table.setItem(
                row,
                1,
                self._make_readonly_centered_item(item.message or "失败"),
            )

        for row in reversed(rows_to_remove):
            self.file_table.removeRow(row)

        self._queued_files = failed_files
        self.status_label.setText(f"成功 {result.succeeded} 张，失败 {result.failed} 张")

    def _make_readonly_centered_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item

    def _make_delete_button(self) -> QPushButton:
        button = QPushButton()
        button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))
        button.setFlat(True)
        button.setToolTip("移除")
        button.clicked.connect(lambda: self._remove_row_for_button(button))
        return button

    def _remove_row_for_button(self, button: QPushButton) -> None:
        for row in range(self.file_table.rowCount()):
            if self.file_table.cellWidget(row, 3) is button:
                self.file_table.removeRow(row)
                del self._queued_files[row]
                break
