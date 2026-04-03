from pathlib import Path

from PIL import Image

from image_format_converter.models import ConversionBatchResult, ConversionItemResult


SUPPORTED_INPUT_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif"}
FORMAT_SUFFIX = {
    "PNG": ".png",
    "JPG": ".jpg",
    "BMP": ".bmp",
    "WEBP": ".webp",
    "ICO": ".ico",
}


class ConversionService:
    def convert_files(
        self, sources: list[Path], output_dir: Path, target_format: str
    ) -> ConversionBatchResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        results = [
            self._convert_one(path, output_dir, target_format) for path in sources
        ]
        return ConversionBatchResult.from_file_results(results)

    def _convert_one(
        self, source: Path, output_dir: Path, target_format: str
    ) -> ConversionItemResult:
        if source.suffix.lower() not in SUPPORTED_INPUT_SUFFIXES:
            return ConversionItemResult(
                source=source,
                output=None,
                success=False,
                message="Not a supported image format.",
            )

        target_format = target_format.upper()
        suffix = FORMAT_SUFFIX.get(target_format)
        if suffix is None:
            return ConversionItemResult(
                source=source,
                output=None,
                success=False,
                message=f"Unsupported target format: {target_format}",
            )

        output_path = self._next_available_output_path(
            output_dir / f"{source.stem}{suffix}"
        )

        with Image.open(source) as image:
            prepared = self._prepare_image_for_target(image, target_format)
            save_kwargs = {}
            if target_format == "JPG":
                save_kwargs["format"] = "JPEG"
            else:
                save_kwargs["format"] = target_format
            prepared.save(output_path, **save_kwargs)

        return ConversionItemResult(
            source=source,
            output=output_path,
            success=True,
            message="",
        )

    def _next_available_output_path(self, output_path: Path) -> Path:
        if not output_path.exists():
            return output_path

        counter = 1
        while True:
            candidate = output_path.with_name(
                f"{output_path.stem} ({counter}){output_path.suffix}"
            )
            if not candidate.exists():
                return candidate
            counter += 1

    def _prepare_image_for_target(
        self, image: Image.Image, target_format: str
    ) -> Image.Image:
        if target_format == "JPG" and image.mode in {"RGBA", "LA"}:
            background = Image.new("RGB", image.size, "white")
            background.paste(image, mask=image.getchannel("A"))
            return background
        if image.mode not in {"RGB", "RGBA"}:
            return image.convert("RGBA" if target_format == "PNG" else "RGB")
        return image
