from pathlib import Path

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from image_format_converter.widgets import DropZone


class MainWindow(QWidget):
    def __init__(self, default_output_dir: Path | None):
        super().__init__()
        self._output_dir = default_output_dir
        self._queued_files: list[Path] = []

        self.output_path_label = QLabel(self._format_output_dir())
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPG", "BMP", "WEBP", "ICO"])
        self.file_table = QTableWidget(0, 3)
        self.file_table.setHorizontalHeaderLabels(["文件", "状态", "格式"])

        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self.add_files)

        self._build_layout()

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        header.addWidget(QLabel("输出目录："))
        header.addWidget(self.output_path_label)
        header.addStretch(1)
        header.addWidget(QLabel("目标格式："))
        header.addWidget(self.format_combo)
        layout.addLayout(header)
        layout.addWidget(self.drop_zone)
        layout.addWidget(self.file_table)

    def _format_output_dir(self) -> str:
        return f"输出目录：{self._output_dir}" if self._output_dir else "输出目录：未设置"

    def set_output_directory(self, output_dir: Path | None) -> None:
        self._output_dir = output_dir
        self.output_path_label.setText(self._format_output_dir())

    def add_files(self, files: list[Path]) -> None:
        for file_path in files:
            self._queued_files.append(file_path)
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)
            self.file_table.setItem(row, 0, QTableWidgetItem(str(file_path)))
            self.file_table.setItem(row, 1, QTableWidgetItem("待处理"))
            self.file_table.setItem(row, 2, QTableWidgetItem(self.format_combo.currentText()))
