from pathlib import Path

from PIL import Image

from image_format_converter.converter import ConversionService


def test_png_to_jpg_flattens_transparency(tmp_path: Path):
    source = tmp_path / "transparent.png"
    Image.new("RGBA", (8, 8), (255, 0, 0, 0)).save(source)

    service = ConversionService()
    result = service.convert_files([source], tmp_path / "out", "JPG")

    assert result.succeeded == 1
    assert (tmp_path / "out" / "transparent.jpg").exists()


def test_transparent_gif_to_jpg_is_flattened_to_white(tmp_path: Path):
    source = tmp_path / "transparent.gif"
    image = Image.new("RGBA", (8, 8), (255, 0, 0, 0))
    image.save(source, format="GIF", transparency=0)

    service = ConversionService()
    result = service.convert_files([source], tmp_path / "out", "JPG")

    output = Image.open(tmp_path / "out" / "transparent.jpg")
    assert result.succeeded == 1
    assert output.getpixel((0, 0)) == (255, 255, 255)


def test_existing_output_name_gets_incremented(tmp_path: Path):
    source = tmp_path / "photo.png"
    Image.new("RGB", (8, 8), "blue").save(source)
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    Image.new("RGB", (8, 8), "red").save(output_dir / "photo.png")

    service = ConversionService()
    service.convert_files([source], output_dir, "PNG")

    assert (output_dir / "photo (1).png").exists()


def test_unsupported_file_is_reported_without_stopping_batch(tmp_path: Path):
    source = tmp_path / "notes.txt"
    source.write_text("not an image", encoding="utf-8")

    service = ConversionService()
    result = service.convert_files([source], tmp_path / "out", "PNG")

    assert result.failed == 1
    assert "not a supported image format" in result.items[0].message.lower()


def test_corrupt_supported_file_does_not_stop_batch(tmp_path: Path):
    broken = tmp_path / "broken.png"
    broken.write_bytes(b"not a valid image")
    good = tmp_path / "photo.png"
    Image.new("RGB", (8, 8), "blue").save(good)

    service = ConversionService()
    result = service.convert_files([broken, good], tmp_path / "out", "PNG")

    assert result.failed == 1
    assert result.succeeded == 1
    assert (tmp_path / "out" / "photo.png").exists()
    assert result.items[0].success is False
    assert result.items[1].success is True


def test_invalid_file_does_not_block_valid_file(tmp_path: Path):
    valid = tmp_path / "ok.png"
    invalid = tmp_path / "bad.txt"
    Image.new("RGB", (10, 10), "black").save(valid)
    invalid.write_text("bad", encoding="utf-8")

    result = ConversionService().convert_files([invalid, valid], tmp_path / "out", "PNG")

    assert result.succeeded == 1
    assert result.failed == 1
