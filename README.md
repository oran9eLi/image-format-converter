# Image Format Converter

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
python -m pytest
```

If `python` resolves to the Windows Store shim on this machine, create the
virtual environment with any installed Python 3.11+ launcher, then keep the
install and test commands inside `.venv`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[dev]
.\.venv\Scripts\python.exe -m pytest
```
