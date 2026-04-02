from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    default_output_dir: Path | None


class AppConfigStore:
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path

    def load(self) -> AppConfig:
        if not self._config_path.exists():
            return AppConfig(default_output_dir=None)

        data = json.loads(self._config_path.read_text(encoding="utf-8"))
        raw_path = data.get("default_output_dir")
        return AppConfig(default_output_dir=Path(raw_path) if raw_path else None)

    def save_default_output_dir(self, output_dir: Path) -> None:
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"default_output_dir": str(output_dir)}
        self._config_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def default_config_path() -> Path:
    return (
        Path.home()
        / "AppData"
        / "Local"
        / "ImageFormatConverter"
        / "config.json"
    )
