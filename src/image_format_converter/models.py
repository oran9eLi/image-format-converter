from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ConversionItemResult:
    source: Path
    output: Path | None
    success: bool
    message: str = ""


@dataclass(slots=True)
class ConversionBatchResult:
    items: list[ConversionItemResult] = field(default_factory=list)

    @property
    def succeeded(self) -> int:
        return sum(1 for item in self.items if item.success)

    @property
    def failed(self) -> int:
        return sum(1 for item in self.items if not item.success)

    @classmethod
    def from_file_results(
        cls, items: list[ConversionItemResult]
    ) -> "ConversionBatchResult":
        return cls(items=items)
