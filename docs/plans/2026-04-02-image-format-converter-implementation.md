# Image Format Converter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows desktop app that batch-converts common image formats with drag-and-drop, visible output path management, and `exe` packaging.

**Architecture:** Use a small `src`-layout Python application. Keep conversion logic, config persistence, and Qt UI in separate modules so unit tests can cover non-UI behavior and GUI tests can validate drag/drop and button flows without coupling business logic to widgets.

**Tech Stack:** Python, PySide6, Pillow, pytest, pytest-qt, PyInstaller

---

## File Structure

### Planned files

- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/image_format_converter/__init__.py`
- Create: `src/image_format_converter/app.py`
- Create: `src/image_format_converter/config.py`
- Create: `src/image_format_converter/converter.py`
- Create: `src/image_format_converter/models.py`
- Create: `src/image_format_converter/main_window.py`
- Create: `src/image_format_converter/widgets/__init__.py`
- Create: `src/image_format_converter/widgets/drop_zone.py`
- Create: `tests/conftest.py`
- Create: `tests/unit/test_config.py`
- Create: `tests/unit/test_converter.py`
- Create: `tests/gui/test_main_window.py`
- Create: `scripts/build.ps1`

### Responsibility map

- `pyproject.toml`: project metadata, runtime dependencies, dev dependencies, pytest config
- `src/image_format_converter/config.py`: load and save the default output path in a small JSON config file
- `src/image_format_converter/models.py`: supported format metadata and per-file queue item data structure
- `src/image_format_converter/converter.py`: validate input files, resolve output paths, flatten transparency for JPG, write converted files
- `src/image_format_converter/widgets/drop_zone.py`: focused drag-and-drop widget emitting accepted file paths
- `src/image_format_converter/main_window.py`: main UI composition, queue management, path change flow, status reporting
- `src/image_format_converter/app.py`: Qt application entrypoint
- `tests/unit/*`: non-UI TDD coverage for config and conversion rules
- `tests/gui/test_main_window.py`: GUI flow tests with `pytest-qt`
- `scripts/build.ps1`: repeatable local build command for the `exe`

## Task 1: Bootstrap Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/image_format_converter/__init__.py`
- Create: `src/image_format_converter/app.py`
- Create: `tests/conftest.py`
- Create: `tests/unit/test_bootstrap_smoke.py`

- [ ] **Step 1: Write the failing smoke test**

```python
from image_format_converter.app import build_app


def test_build_app_returns_qapplication(qapp):
    app = build_app([])
    assert app is qapp
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/test_bootstrap_smoke.py -v`
Expected: FAIL with `ModuleNotFoundError` for `image_format_converter`

- [ ] **Step 3: Add project metadata and minimal package**

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "image-format-converter"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["PySide6>=6.8", "Pillow>=11.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-qt>=4.4"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

```python
from PySide6.QtWidgets import QApplication


def build_app(argv: list[str]) -> QApplication:
    app = QApplication.instance()
    return app or QApplication(argv)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/test_bootstrap_smoke.py -v`
Expected: PASS

- [ ] **Step 5: Add a short README with local setup**

```md
# Image Format Converter

## Local setup

python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
python -m pytest
```

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml README.md src/image_format_converter/__init__.py src/image_format_converter/app.py tests/conftest.py tests/unit/test_bootstrap_smoke.py
git commit -m "chore: bootstrap Python desktop app"
```

## Task 2: Persist the Default Output Path

**Files:**
- Create: `src/image_format_converter/config.py`
- Create: `tests/unit/test_config.py`

- [ ] **Step 1: Write the failing config tests**

```python
from pathlib import Path

from image_format_converter.config import AppConfigStore


def test_load_returns_none_when_file_missing(tmp_path: Path):
    store = AppConfigStore(tmp_path / "config.json")
    assert store.load().default_output_dir is None


def test_save_and_reload_default_output_dir(tmp_path: Path):
    config_path = tmp_path / "config.json"
    store = AppConfigStore(config_path)
    store.save_default_output_dir(Path("D:/PNG_Output"))
    assert store.load().default_output_dir == Path("D:/PNG_Output")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/unit/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError` for `image_format_converter.config`

- [ ] **Step 3: Write the minimal config implementation**

```python
from dataclasses import dataclass
from pathlib import Path
import json


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
        self._config_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/unit/test_config.py -v`
Expected: PASS

- [ ] **Step 5: Refactor for app data location helper**

```python
def default_config_path() -> Path:
    return Path.home() / "AppData" / "Local" / "ImageFormatConverter" / "config.json"
```

- [ ] **Step 6: Commit**

```bash
git add src/image_format_converter/config.py tests/unit/test_config.py
git commit -m "feat: persist default output path"
```

## Task 3: Implement Conversion Rules and Output Naming

**Files:**
- Create: `src/image_format_converter/models.py`
- Create: `src/image_format_converter/converter.py`
- Create: `tests/unit/test_converter.py`

- [ ] **Step 1: Write the failing converter tests**

```python
from pathlib import Path

from PIL import Image

from image_format_converter.converter import ConversionService


def test_png_to_jpg_flattens_transparency(tmp_path: Path):
    source = tmp_path / "transparent.png"
    Image.new("RGBA", (8, 8), (255, 0, 0, 0)).save(source)

    service = ConversionService()
    result = service.convert_files([source], tmp_path / "out", "JPG")

    assert result.succeeded == 1
    assert (tmp_path / "out" / "transparent.jpg").exists()


def test_existing_output_name_gets_incremented(tmp_path: Path):
    source = tmp_path / "photo.png"
    Image.new("RGB", (8, 8), "blue").save(source)
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    Image.new("RGB", (8, 8), "red").save(output_dir / "photo.png")

    service = ConversionService()
    service.convert_files([source], output_dir, "PNG")

    assert (output_dir / "photo (1).png").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/unit/test_converter.py -v`
Expected: FAIL with `ModuleNotFoundError` for `image_format_converter.converter`

- [ ] **Step 3: Write minimal conversion models and service**

```python
SUPPORTED_INPUT_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif"}
FORMAT_SUFFIX = {"PNG": ".png", "JPG": ".jpg", "BMP": ".bmp", "WEBP": ".webp", "ICO": ".ico"}


class ConversionService:
    def convert_files(self, sources: list[Path], output_dir: Path, target_format: str) -> ConversionBatchResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        results = [self._convert_one(path, output_dir, target_format) for path in sources]
        return ConversionBatchResult.from_file_results(results)
```

```python
def _prepare_image_for_target(image: Image.Image, target_format: str) -> Image.Image:
    if target_format == "JPG" and image.mode in {"RGBA", "LA"}:
        background = Image.new("RGB", image.size, "white")
        background.paste(image, mask=image.getchannel("A"))
        return background
    if image.mode not in {"RGB", "RGBA"}:
        return image.convert("RGBA" if target_format == "PNG" else "RGB")
    return image
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/unit/test_converter.py -v`
Expected: PASS

- [ ] **Step 5: Add failure-path tests and minimal support**

```python
def test_unsupported_file_is_reported_without_stopping_batch(tmp_path: Path):
    source = tmp_path / "notes.txt"
    source.write_text("not an image", encoding="utf-8")

    service = ConversionService()
    result = service.convert_files([source], tmp_path / "out", "PNG")

    assert result.failed == 1
    assert "not a supported image format" in result.items[0].message.lower()
```

- [ ] **Step 6: Run the full converter suite**

Run: `python -m pytest tests/unit/test_converter.py -v`
Expected: PASS for transparency, duplicate naming, unsupported-file handling, and any added GIF/ICO cases

- [ ] **Step 7: Commit**

```bash
git add src/image_format_converter/models.py src/image_format_converter/converter.py tests/unit/test_converter.py
git commit -m "feat: add batch conversion service"
```

## Task 4: Build the Drag-and-Drop UI Shell

**Files:**
- Create: `src/image_format_converter/widgets/__init__.py`
- Create: `src/image_format_converter/widgets/drop_zone.py`
- Create: `src/image_format_converter/main_window.py`
- Create: `tests/gui/test_main_window.py`

- [ ] **Step 1: Write the failing GUI tests**

```python
from pathlib import Path

from image_format_converter.main_window import MainWindow


def test_window_shows_output_path_and_target_formats(qtbot, tmp_path: Path):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    assert str(tmp_path) in window.output_path_label.text()
    assert window.format_combo.count() == 5


def test_add_files_populates_queue(qtbot, tmp_path: Path):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    window.add_files([tmp_path / "a.jpg", tmp_path / "b.png"])

    assert window.file_table.rowCount() == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/gui/test_main_window.py -v`
Expected: FAIL with `ModuleNotFoundError` for `image_format_converter.main_window`

- [ ] **Step 3: Write the minimal widgets and main window**

```python
class DropZone(QFrame):
    files_dropped = Signal(list)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [Path(url.toLocalFile()) for url in event.mimeData().urls()]
        self.files_dropped.emit(files)
```

```python
class MainWindow(QWidget):
    def __init__(self, default_output_dir: Path | None):
        super().__init__()
        self.output_path_label = QLabel(str(default_output_dir or "未设置"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPG", "BMP", "WEBP", "ICO"])
        self.file_table = QTableWidget(0, 3)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/gui/test_main_window.py -v`
Expected: PASS

- [ ] **Step 5: Add GUI coverage for path-change flow**

```python
def test_change_output_path_updates_label(qtbot, tmp_path: Path):
    window = MainWindow(default_output_dir=tmp_path)
    qtbot.addWidget(window)

    newer = tmp_path / "exports"
    window.set_output_directory(newer)

    assert str(newer) in window.output_path_label.text()
```

- [ ] **Step 6: Re-run GUI suite**

Run: `python -m pytest tests/gui/test_main_window.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/image_format_converter/widgets/__init__.py src/image_format_converter/widgets/drop_zone.py src/image_format_converter/main_window.py tests/gui/test_main_window.py
git commit -m "feat: add main window shell"
```

## Task 5: Connect UI Actions to Config and Conversion Service

**Files:**
- Modify: `src/image_format_converter/app.py`
- Modify: `src/image_format_converter/config.py`
- Modify: `src/image_format_converter/converter.py`
- Modify: `src/image_format_converter/main_window.py`
- Modify: `tests/unit/test_config.py`
- Modify: `tests/unit/test_converter.py`
- Modify: `tests/gui/test_main_window.py`

- [ ] **Step 1: Write the failing integration-style GUI tests**

```python
from pathlib import Path

from PIL import Image

from image_format_converter.config import AppConfigStore
from image_format_converter.main_window import MainWindow


def test_convert_button_runs_batch_and_updates_status(qtbot, tmp_path: Path):
    source = tmp_path / "sample.png"
    Image.new("RGB", (12, 12), "green").save(source)

    store = AppConfigStore(tmp_path / "config.json")
    window = MainWindow(default_output_dir=tmp_path / "out", config_store=store)
    qtbot.addWidget(window)
    window.add_files([source])

    window.convert_current_batch()

    assert "成功 1 张" in window.status_label.text()
    assert (tmp_path / "out" / "sample.png").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/gui/test_main_window.py -v`
Expected: FAIL because conversion wiring and status updates are not implemented yet

- [ ] **Step 3: Write the minimal integration code**

```python
def convert_current_batch(self) -> None:
    result = self._conversion_service.convert_files(
        self.current_files,
        self.current_output_dir,
        self.format_combo.currentText(),
    )
    self.status_label.setText(f"成功 {result.succeeded} 张，失败 {result.failed} 张")
```

```python
def main() -> int:
    app = build_app(sys.argv)
    store = AppConfigStore(default_config_path())
    window = MainWindow(default_output_dir=store.load().default_output_dir, config_store=store)
    window.show()
    return app.exec()
```

- [ ] **Step 4: Run the focused GUI tests to verify they pass**

Run: `python -m pytest tests/gui/test_main_window.py -v`
Expected: PASS

- [ ] **Step 5: Add regression tests for saved default path and mixed batch failures**

```python
def test_changing_output_path_persists_new_default(tmp_path: Path):
    store = AppConfigStore(tmp_path / "config.json")
    store.save_default_output_dir(tmp_path / "initial")
    store.save_default_output_dir(tmp_path / "next")
    assert store.load().default_output_dir == tmp_path / "next"
```

```python
def test_invalid_file_does_not_block_valid_file(tmp_path: Path):
    valid = tmp_path / "ok.png"
    invalid = tmp_path / "bad.txt"
    Image.new("RGB", (10, 10), "black").save(valid)
    invalid.write_text("bad", encoding="utf-8")
    result = ConversionService().convert_files([invalid, valid], tmp_path / "out", "PNG")
    assert result.succeeded == 1
    assert result.failed == 1
```

- [ ] **Step 6: Run the unit and GUI suites together**

Run: `python -m pytest tests/unit tests/gui -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/image_format_converter/app.py src/image_format_converter/config.py src/image_format_converter/converter.py src/image_format_converter/main_window.py tests/unit/test_config.py tests/unit/test_converter.py tests/gui/test_main_window.py
git commit -m "feat: wire conversion workflow into UI"
```

## Task 6: Package the Application for Windows

**Files:**
- Create: `scripts/build.ps1`
- Modify: `README.md`
- Modify: `pyproject.toml`

- [ ] **Step 1: Write the failing packaging smoke step**

Run: `powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1`
Expected: FAIL because the script does not exist yet

- [ ] **Step 2: Add minimal build script and packaging dependency**

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-qt>=4.4", "pyinstaller>=6.0"]
```

```powershell
python -m PyInstaller `
  --noconsole `
  --onefile `
  --name ImageFormatConverter `
  --paths src `
  src/image_format_converter/app.py
```

- [ ] **Step 3: Run the build script to verify it produces an executable**

Run: `powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1`
Expected: PASS and create `dist\ImageFormatConverter.exe`

- [ ] **Step 4: Document run/build commands**

```md
python -m pip install -e .[dev]
python -m image_format_converter.app
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

- [ ] **Step 5: Run the full verification suite**

Run: `python -m pytest -v`
Expected: PASS

Run: `git status --short`
Expected: only intended README/build metadata changes remain before commit

- [ ] **Step 6: Commit**

```bash
git add scripts/build.ps1 README.md pyproject.toml
git commit -m "build: package desktop converter as exe"
```

## Task 7: Final Verification and Handoff

**Files:**
- Modify: `README.md` (only if verification uncovers missing instructions)

- [ ] **Step 1: Install dependencies in a fresh virtual environment**

Run: `python -m venv .venv`
Expected: PASS

Run: `.venv\Scripts\python -m pip install -e .[dev]`
Expected: PASS

- [ ] **Step 2: Run the full automated suite from the virtual environment**

Run: `.venv\Scripts\python -m pytest -v`
Expected: PASS

- [ ] **Step 3: Run the packaged application manually**

Run: `dist\ImageFormatConverter.exe`
Expected: app window opens, output path is visible, drag-and-drop area is present, format combo is populated

- [ ] **Step 4: Verify one real conversion manually**

Manual check:
- drag one transparent PNG
- switch target to `JPG`
- confirm output file is written with white background
- verify output directory opens correctly

- [ ] **Step 5: Commit any final docs-only fixes**

```bash
git add README.md
git commit -m "docs: finalize usage instructions"
```

## Notes for Execution

- Keep UI copy in Chinese because the target user requested a Chinese-language desktop tool.
- Do not add extra settings pages in v1. Keep everything in one window.
- Prefer dependency injection in `MainWindow` for `AppConfigStore` and `ConversionService`; it keeps GUI tests simple and avoids test-only hacks.
- If drag-and-drop proves flaky in automated tests, keep unit tests around file acceptance logic and use `pytest-qt` for a lighter integration path instead of brittle synthetic OS drag events.
