import os
import tempfile
from pathlib import Path
from uuid import uuid4

import _pytest.tmpdir as pytest_tmpdir


_LOCAL_TMP = Path.home() / ".codex" / "memories" / "image-format-converter" / "pytest-temp"
_LOCAL_TMP.mkdir(parents=True, exist_ok=True)
_CACHE_DIR = Path.home() / ".codex" / "memories" / "image-format-converter" / "pytest-cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

for name in ("TMP", "TEMP", "TMPDIR"):
    os.environ[name] = str(_LOCAL_TMP)

tempfile.tempdir = str(_LOCAL_TMP)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


# Use a stable writable temp root instead of pytest's default numbered root on this machine.
def _getbasetemp(self):
    if self._basetemp is None:
        self._basetemp = _LOCAL_TMP
    return self._basetemp


def _mktemp(self, basename, numbered=True):
    basename = self._ensure_relative_to_basetemp(basename)
    path = self.getbasetemp() / f"{basename}-{uuid4().hex}"
    path.mkdir()
    return path


pytest_tmpdir.TempPathFactory.getbasetemp = _getbasetemp
pytest_tmpdir.TempPathFactory.mktemp = _mktemp
