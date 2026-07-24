from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile

from utils.normalizer import file_stem, normalize_path, without_extension


@dataclass(frozen=True)
class FileEntry:
    display_path: str
    normalized_path: str
    is_dir: bool = False

    @property
    def basename(self) -> str:
        return PurePosixPath(self.normalized_path).name

    @property
    def stem(self) -> str:
        return file_stem(self.normalized_path)

    @property
    def no_extension(self) -> str:
        return without_extension(self.normalized_path)


@dataclass
class FileInventory:
    entries: list[FileEntry] = field(default_factory=list)
    by_exact: dict[str, list[FileEntry]] = field(default_factory=dict)
    by_no_extension: dict[str, list[FileEntry]] = field(default_factory=dict)
    by_basename: dict[str, list[FileEntry]] = field(default_factory=dict)
    by_stem: dict[str, list[FileEntry]] = field(default_factory=dict)

    def add(self, entry: FileEntry) -> None:
        if not entry.normalized_path:
            return
        self.entries.append(entry)
        self.by_exact.setdefault(entry.normalized_path, []).append(entry)
        self.by_no_extension.setdefault(entry.no_extension, []).append(entry)
        self.by_basename.setdefault(entry.basename, []).append(entry)
        self.by_stem.setdefault(entry.stem, []).append(entry)


class FileScanner:
    def __init__(self, roots: list[str | Path], max_nested_zip_mb: int = 512):
        self.roots = [Path(root) for root in roots]
        self.max_nested_zip_bytes = max_nested_zip_mb * 1024 * 1024
        self.inventory = FileInventory()

    def scan(self) -> FileInventory:
        for root in self.roots:
            if root.is_dir():
                self._scan_directory(root)
            elif root.is_file():
                self._add_file(root, root.name)
                if root.suffix.casefold() == ".zip":
                    self._scan_zip_path(root, root.name)
        return self.inventory

    def _scan_directory(self, root: Path) -> None:
        for path in root.rglob("*"):
            try:
                relative = path.relative_to(root).as_posix()
            except ValueError:
                relative = path.as_posix()

            if path.is_dir():
                self._add_display(relative, is_dir=True)
                continue

            self._add_file(path, relative)
            if path.suffix.casefold() == ".zip":
                self._scan_zip_path(path, relative)

    def _add_file(self, path: Path, display_path: str) -> None:
        self._add_display(display_path, is_dir=False)

    def _add_display(self, display_path: str, is_dir: bool) -> None:
        normalized = normalize_path(display_path)
        self.inventory.add(FileEntry(display_path=display_path, normalized_path=normalized, is_dir=is_dir))

    def _scan_zip_path(self, zip_path: Path, display_prefix: str) -> None:
        try:
            with ZipFile(zip_path) as zf:
                self._scan_zip_file(zf, display_prefix)
        except (BadZipFile, OSError):
            return

    def _scan_zip_file(self, zf: ZipFile, display_prefix: str) -> None:
        for info in zf.infolist():
            name = info.filename.replace("\\", "/").strip("/")
            if not name:
                continue

            display = f"{display_prefix}!{name}"
            self._add_display(display, is_dir=info.is_dir())

            if info.is_dir() or not name.casefold().endswith(".zip"):
                continue
            if info.file_size > self.max_nested_zip_bytes:
                continue

            try:
                data = zf.read(info)
                with ZipFile(BytesIO(data)) as nested:
                    self._scan_zip_file(nested, display)
            except (BadZipFile, OSError, RuntimeError):
                continue
