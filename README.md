# Image Format Converter

一个用于 Windows 的轻量图片格式转换工具，支持拖拽、批量转换、默认输出目录保存，以及直接修改输出文件名。

## 功能

- 支持 `JPG/JPEG`、`PNG`、`BMP`、`WEBP`、`GIF` 输入
- 支持输出为 `PNG`、`JPG`、`BMP`、`WEBP`、`ICO`
- 支持拖拽添加和按钮选择图片
- 支持批量转换
- 支持设置并保存默认输出目录
- 支持在列表中直接修改输出文件名
- 转换成功项自动从列表移除，失败项保留

## 下载

如果你只想直接使用程序，请到 GitHub Releases 页面下载 `ImageFormatConverter.exe`。

## 本地运行

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\activate
py -3.14 -m pip install -e .[dev]
py -3.14 -m image_format_converter.app
```

如果本机没有 `py -3.14`，可以改用任意已安装的 Python 3.11+：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[dev]
.\.venv\Scripts\python.exe -m image_format_converter.app
```

## 打包 exe

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

打包完成后，成品位于：

```text
dist\ImageFormatConverter.exe
```

## 测试

```powershell
py -3.14 -m pytest -v
```
