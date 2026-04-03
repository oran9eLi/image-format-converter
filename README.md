# Image Format Converter

## Local setup

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\activate
py -3.14 -m pip install -e .[dev]
py -3.14 -m image_format_converter.app
```

If `py -3.14` is not available on this machine, create the virtual environment
with any installed Python 3.11+ launcher, then keep the install and run
commands inside `.venv`:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[dev]
.\.venv\Scripts\python.exe -m image_format_converter.app
```

## Build for Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```
