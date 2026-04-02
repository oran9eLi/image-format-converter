# Image Format Converter

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
python -m pytest
```

If `python` resolves to the Windows Store shim on this machine, use `py -3.14`
for the same steps instead:

```powershell
py -3.14 -m venv .venv
.venv\Scripts\activate
py -3.14 -m pip install -e .[dev]
py -3.14 -m pytest
```
