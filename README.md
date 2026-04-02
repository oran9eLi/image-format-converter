# Image Format Converter

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
python -m pytest
```

If `python` resolves to the Windows Store shim on this machine, use the virtual
environment's interpreter directly for install and test commands:

```powershell
py -m venv .venv
.venv\Scripts\activate
.\.venv\Scripts\python.exe -m pip install -e .[dev]
.\.venv\Scripts\python.exe -m pytest
```
