import sys

from PySide6.QtWidgets import QApplication

from image_format_converter.config import AppConfigStore, default_config_path
from image_format_converter.main_window import MainWindow


def build_app(argv: list[str]) -> QApplication:
    app = QApplication.instance()
    return app or QApplication(argv)


def main() -> int:
    app = build_app(sys.argv)
    store = AppConfigStore(default_config_path())
    window = MainWindow(
        default_output_dir=store.load().default_output_dir,
        config_store=store,
    )
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
