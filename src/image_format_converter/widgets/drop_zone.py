from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame


class DropZone(QFrame):
    files_dropped = Signal(list)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [Path(url.toLocalFile()) for url in event.mimeData().urls()]
        self.files_dropped.emit(files)
