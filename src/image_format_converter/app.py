from PySide6.QtWidgets import QApplication


def build_app(argv: list[str]) -> QApplication:
    app = QApplication.instance()
    return app or QApplication(argv)
