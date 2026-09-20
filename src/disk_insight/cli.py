from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from .core import export_json, human_size, scan


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="disk-insight", description="Analyze local disk usage safely.")
    p.add_argument("path", nargs="?", default=".", type=Path)
    p.add_argument("--top", type=int, default=20, help="Number of largest files to show")
    p.add_argument("--older-than", type=int, metavar="DAYS", help="Show files older than DAYS")
    p.add_argument("--min-size", type=int, default=0, metavar="BYTES")
    p.add_argument("--include-hidden", action="store_true")
    p.add_argument("--follow-symlinks", action="store_true")
    p.add_argument("--json", type=Path, metavar="FILE", help="Export full scan as JSON")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.top < 0 or args.min_size < 0 or (args.older_than is not None and args.older_than < 0):
        print("error: numeric options must be non-negative", file=sys.stderr)
        return 2
    try:
        result = scan(args.path, follow_symlinks=args.follow_symlinks, include_hidden=args.include_hidden)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    files = [f for f in result.files if f.size >= args.min_size]
    print(f"Root: {result.root}")
    print(f"Files: {len(result.files)} | Total: {human_size(result.total_bytes)} | Skipped: {len(result.skipped)}")
    print("\nLargest files:")
    for item in sorted(files, key=lambda f: f.size, reverse=True)[: args.top]:
        print(f"{human_size(item.size):>10}  {item.path}")

    print("\nUsage by extension:")
    for ext, size in list(result.by_extension().items())[:15]:
        print(f"{human_size(size):>10}  {ext}")

    if args.older_than is not None:
        print(f"\nFiles older than {args.older_than} days:")
        for item in result.old_files(args.older_than):
            if item.size >= args.min_size:
                date = datetime.fromtimestamp(item.modified).date().isoformat()
                print(f"{date}  {human_size(item.size):>10}  {item.path}")

    if args.json:
        export_json(result, args.json)
        print(f"\nJSON report: {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
