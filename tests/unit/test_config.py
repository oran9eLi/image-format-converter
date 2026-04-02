from pathlib import Path
from uuid import uuid4

from image_format_converter.config import AppConfigStore, default_config_path


def _create_temp_dir() -> Path:
    temp_dir = Path.cwd() / f"config-test-{uuid4().hex}"
    temp_dir.mkdir()
    return temp_dir


def test_load_returns_none_when_file_missing():
    temp_dir = _create_temp_dir()
    store = AppConfigStore(temp_dir / "config.json")
    assert store.load().default_output_dir is None


def test_save_and_reload_default_output_dir():
    temp_dir = _create_temp_dir()
    config_path = temp_dir / "config.json"
    store = AppConfigStore(config_path)
    store.save_default_output_dir(Path("D:/PNG_Output"))
    assert store.load().default_output_dir == Path("D:/PNG_Output")


def test_default_config_path_points_to_image_format_converter_appdata_location():
    assert default_config_path() == (
        Path.home() / "AppData" / "Local" / "ImageFormatConverter" / "config.json"
    )
