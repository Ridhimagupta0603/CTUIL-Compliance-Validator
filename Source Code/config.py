from __future__ import annotations

from pathlib import Path


DEFAULT_MAX_HEADER_SCAN_ROWS = 80
DEFAULT_NESTED_ZIP_LIMIT_MB = 512


def default_output_path(workbook_path: str | Path) -> Path:
    path = Path(workbook_path)
    return path.with_name(f"{path.stem}_validated{path.suffix}")
