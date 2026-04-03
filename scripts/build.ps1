$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $repoRoot

py -3.14 -m PyInstaller `
  --noconsole `
  --onefile `
  --name ImageFormatConverter `
  --paths src `
  src/image_format_converter/app.py
