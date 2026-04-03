import os
import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

_LOCAL_TMP = Path.home() / ".codex" / "memories" / "image-format-converter" / "tmp"
shutil.rmtree(_LOCAL_TMP, ignore_errors=True)
_LOCAL_TMP.mkdir(parents=True, exist_ok=True)

for name in ("TMP", "TEMP", "TMPDIR"):
    os.environ[name] = str(_LOCAL_TMP)

tempfile.tempdir = str(_LOCAL_TMP)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture
def tmp_path():
    path = _LOCAL_TMP / f"tmp-{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
