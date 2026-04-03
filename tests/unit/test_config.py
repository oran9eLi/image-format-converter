from pathlib import Path

from image_format_converter.config import AppConfigStore, default_config_path


def test_load_returns_none_when_file_missing(tmp_path: Path):
    store = AppConfigStore(tmp_path / "config.json")
    assert store.load().default_output_dir is None


def test_save_and_reload_default_output_dir(tmp_path: Path):
    config_path = tmp_path / "config.json"
    store = AppConfigStore(config_path)
    store.save_default_output_dir(Path("D:/PNG_Output"))
    assert store.load().default_output_dir == Path("D:/PNG_Output")


def test_default_config_path_points_to_image_format_converter_appdata_location():
    assert default_config_path() == (
        Path.home() / "AppData" / "Local" / "ImageFormatConverter" / "config.json"
    )
