from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from image_format_converter.config import AppConfigStore
from image_format_converter.converter import ConversionService
from image_format_converter.widgets import DropZone


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
        self._queued_row_indices: list[int] = []

        self.output_path_label = QLabel(self._format_output_dir())
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPG", "BMP", "WEBP", "ICO"])
        self.convert_button = QPushButton("开始转换")
        self.convert_button.clicked.connect(self.convert_current_batch)
        self.status_label = QLabel("就绪")
        self.file_table = QTableWidget(0, 3)
        self.file_table.setHorizontalHeaderLabels(["文件", "状态", "格式"])

        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self.add_files)

        self._build_layout()

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        header.addWidget(self.output_path_label)
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

    def add_files(self, files: list[Path]) -> None:
        for file_path in files:
            self._queued_files.append(file_path)
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)
            self._queued_row_indices.append(row)
            self.file_table.setItem(row, 0, QTableWidgetItem(str(file_path)))
            self.file_table.setItem(row, 1, QTableWidgetItem("待处理"))
            self.file_table.setItem(row, 2, QTableWidgetItem(self.format_combo.currentText()))

    def convert_current_batch(self) -> None:
        if self._output_dir is None:
            self.status_label.setText("请先设置输出目录")
            return

        current_format = self.format_combo.currentText()
        result = self._conversion_service.convert_files(
            self._queued_files,
            self._output_dir,
            current_format,
        )
        for row, item in zip(self._queued_row_indices, result.items):
            self.file_table.setItem(
                row,
                1,
                QTableWidgetItem("成功" if item.success else "失败"),
            )
            self.file_table.setItem(row, 2, QTableWidgetItem(current_format))
        self._queued_files.clear()
        self._queued_row_indices.clear()
        self.status_label.setText(f"成功 {result.succeeded} 张，失败 {result.failed} 张")
