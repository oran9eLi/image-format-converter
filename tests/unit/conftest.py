import os
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest


_UNIT_RUNTIME_ROOT = Path(__file__).resolve().parent / ".pytest_runtime_tmp"
_UNIT_RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)

for name in ("TMP", "TEMP", "TMPDIR"):
    os.environ[name] = str(_UNIT_RUNTIME_ROOT)

tempfile.tempdir = str(_UNIT_RUNTIME_ROOT)


@pytest.fixture
def tmp_path() -> Path:
    path = _UNIT_RUNTIME_ROOT / f"tmp-{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    return path
