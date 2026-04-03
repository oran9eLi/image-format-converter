import os
import tempfile
from pathlib import Path
from uuid import uuid4

import _pytest.pathlib as pytest_pathlib
import _pytest.tmpdir as pytest_tmpdir


_REPO_ROOT = Path(__file__).resolve().parents[1]
_LOCAL_TMP = _REPO_ROOT / ".pytest_tmp_local"
_LOCAL_TMP.mkdir(parents=True, exist_ok=True)

for name in ("TMP", "TEMP", "TMPDIR"):
    os.environ[name] = str(_LOCAL_TMP)

tempfile.tempdir = str(_LOCAL_TMP)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


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
pytest_pathlib.cleanup_dead_symlinks = lambda *args, **kwargs: None
pytest_tmpdir.cleanup_dead_symlinks = lambda *args, **kwargs: None
