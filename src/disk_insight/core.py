from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class FileRecord:
    path: str
    size: int
    modified: float
    extension: str


@dataclass
class ScanResult:
    root: str
    files: list[FileRecord]
    skipped: list[str]

    @property
    def total_bytes(self) -> int:
        return sum(f.size for f in self.files)

    def largest(self, limit: int = 20) -> list[FileRecord]:
        return sorted(self.files, key=lambda f: f.size, reverse=True)[:limit]

    def by_extension(self) -> dict[str, int]:
        totals: dict[str, int] = {}
        for item in self.files:
            key = item.extension or "[no extension]"
            totals[key] = totals.get(key, 0) + item.size
        return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))

    def old_files(self, days: int, now: float | None = None) -> list[FileRecord]:
        current = now if now is not None else datetime.now(timezone.utc).timestamp()
        cutoff = current - days * 86400
        return sorted((f for f in self.files if f.modified < cutoff), key=lambda f: f.modified)

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "total_bytes": self.total_bytes,
            "file_count": len(self.files),
            "skipped": self.skipped,
            "files": [asdict(f) for f in self.files],
            "by_extension": self.by_extension(),
        }


def scan(root: Path, *, follow_symlinks: bool = False, include_hidden: bool = False) -> ScanResult:
    root = root.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    records: list[FileRecord] = []
    skipped: list[str] = []
    for base, dirs, names in os.walk(root, followlinks=follow_symlinks):
        base_path = Path(base)
        if not include_hidden:
            dirs[:] = [d for d in dirs if not d.startswith(".")]
        if not follow_symlinks:
            dirs[:] = [d for d in dirs if not (base_path / d).is_symlink()]
        for name in names:
            if not include_hidden and name.startswith("."):
                continue
            path = base_path / name
            try:
                if path.is_symlink() and not follow_symlinks:
                    continue
                stat = path.stat(follow_symlinks=follow_symlinks)
                if not path.is_file():
                    continue
                records.append(FileRecord(str(path), stat.st_size, stat.st_mtime, path.suffix.lower()))
            except (OSError, PermissionError) as exc:
                skipped.append(f"{path}: {exc}")
    return ScanResult(str(root), records, skipped)


def human_size(value: int) -> str:
    size = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB"):
        if size < 1024 or unit == "PiB":
            return f"{size:.1f} {unit}"
        size /= 1024
    raise AssertionError("unreachable")


def export_json(result: ScanResult, destination: Path) -> None:
    destination.write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


def fingerprint(records: Iterable[FileRecord]) -> str:
    digest = hashlib.sha256()
    for item in sorted(records, key=lambda x: x.path):
        digest.update(f"{item.path}\0{item.size}\0{item.modified}\n".encode())
    return digest.hexdigest()
