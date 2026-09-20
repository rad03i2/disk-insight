import json
import os
import time
from pathlib import Path

import pytest

from disk_insight.core import export_json, fingerprint, human_size, scan


def test_scan_totals_and_extensions(tmp_path: Path):
    (tmp_path / "a.txt").write_bytes(b"abc")
    (tmp_path / "b.bin").write_bytes(b"12345")
    result = scan(tmp_path)
    assert result.total_bytes == 8
    assert len(result.files) == 2
    assert result.by_extension()[".bin"] == 5


def test_hidden_files_are_excluded_by_default(tmp_path: Path):
    (tmp_path / ".secret").write_text("x")
    (tmp_path / "visible").write_text("xx")
    assert len(scan(tmp_path).files) == 1
    assert len(scan(tmp_path, include_hidden=True).files) == 2


def test_old_files(tmp_path: Path):
    target = tmp_path / "old.log"
    target.write_text("old")
    old = time.time() - 40 * 86400
    os.utime(target, (old, old))
    assert scan(tmp_path).old_files(30)[0].path.endswith("old.log")


def test_json_export(tmp_path: Path):
    (tmp_path / "x.txt").write_text("hello")
    result = scan(tmp_path)
    out = tmp_path / "report.json"
    export_json(result, out)
    data = json.loads(out.read_text())
    assert data["file_count"] == 1
    assert data["total_bytes"] == 5


def test_human_size():
    assert human_size(1024) == "1.0 KiB"


def test_fingerprint_is_stable(tmp_path: Path):
    (tmp_path / "x").write_text("a")
    records = scan(tmp_path).files
    assert fingerprint(records) == fingerprint(reversed(records))


def test_invalid_root(tmp_path: Path):
    with pytest.raises(ValueError):
        scan(tmp_path / "missing")
