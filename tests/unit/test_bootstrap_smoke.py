from pathlib import Path

from image_format_converter.app import build_app
from image_format_converter.config import AppConfigStore
from image_format_converter import app as app_module


def test_build_app_returns_qapplication(qapp):
    app = build_app([])
    assert app is qapp


def test_main_bootstraps_window_with_saved_default_output_dir(monkeypatch, tmp_path: Path):
    config_path = tmp_path / "config.json"
    expected_output_dir = tmp_path / "saved-out"
    AppConfigStore(config_path).save_default_output_dir(expected_output_dir)

    captured: dict[str, object] = {}

    class DummyApp:
        def exec(self) -> int:
            return 0

    class DummyWindow:
        def __init__(self, default_output_dir, config_store=None):
            captured["default_output_dir"] = default_output_dir
            captured["config_store"] = config_store

        def show(self) -> None:
            captured["shown"] = True

    monkeypatch.setattr(app_module, "build_app", lambda argv: DummyApp())
    monkeypatch.setattr(app_module, "default_config_path", lambda: config_path)
    monkeypatch.setattr(app_module, "MainWindow", DummyWindow)

    assert app_module.main() == 0
    assert captured["default_output_dir"] == expected_output_dir
    assert captured["shown"] is True
