import os
import shutil
import tempfile
from pathlib import Path

import pytest

_temp_root = Path(__file__).resolve().parent / ".pytest-tmp"
_temp_root.mkdir(parents=True, exist_ok=True)
os.environ["TMP"] = str(_temp_root)
os.environ["TEMP"] = str(_temp_root)
os.environ["TMPDIR"] = str(_temp_root)
tempfile.tempdir = str(_temp_root)


@pytest.fixture
def tmp_path():
    path = Path(tempfile.mkdtemp(dir=_temp_root))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
