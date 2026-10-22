"""evidence-packet: turn a messy folder of dispute evidence into a clean packet.

Walks a source folder of screenshots, receipts, emails and documents, copies
everything into a tidy packet directory, and generates an index with dates,
sizes and SHA-256 hashes so the packet can be handed to a company, a bank, a
regulator or a court with a straight face.

Pure standard library. Nothing leaves your machine.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules"}


@dataclass
class Entry:
    rel_path: str
    size_bytes: int
    modified: datetime
    sha256: str


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect(source: Path, out: Path) -> list[Entry]:
    entries: list[Entry] = []
    for path in sorted(source.rglob("*")):
        if path.is_dir():
            continue
        if any(part in SKIP_DIRS or part.startswith(".") for part in path.parts):
            continue
        if out in path.parents:
            continue
        rel = path.relative_to(source)
        entries.append(
            Entry(
                rel_path=str(rel),
                size_bytes=path.stat().st_size,
                modified=datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc),
                sha256=sha256_of(path),
            )
        )
    entries.sort(key=lambda e: (e.modified, e.rel_path))
    return entries


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n} {unit}"
        n //= 1024
    return f"{n} TB"


def build(source: Path, out: Path, title: str, claimant: str) -> list[Entry]:
    if not source.is_dir():
        raise SystemExit(f"source folder not found: {source}")
    out.mkdir(parents=True, exist_ok=True)
    files_dir = out / "files"
    entries = collect(source, out)

    for entry in entries:
        dest = files_dir / entry.rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / entry.rel_path, dest)

    generated = datetime.now(timezone.utc)
    with (out / "index.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "modified_utc", "size_bytes", "sha256"])
        for e in entries:
            w.writerow([e.rel_path, e.modified.isoformat(timespec="seconds"), e.size_bytes, e.sha256])

    lines = [
        f"# {title}",
        "",
        f"Evidence packet generated {generated.date().isoformat()} "
        f"({generated.isoformat(timespec='seconds')}).",
    ]
    if claimant:
        lines.append(f"Prepared for: {claimant}")
    lines += [
        "",
        f"**{len(entries)} files**, {human_size(sum(e.size_bytes for e in entries))} total. "
        "Files are copied unchanged into `files/`; SHA-256 hashes below let any "
        "recipient verify the copies match the originals.",
        "",
        "| # | File | Date (UTC) | Size | SHA-256 |",
        "|---|------|-----------|------|---------|",
    ]
    for i, e in enumerate(entries, 1):
        lines.append(
            f"| {i} | `{e.rel_path}` | {e.modified.date().isoformat()} "
            f"| {human_size(e.size_bytes)} | `{e.sha256[:16]}...` |"
        )
    lines += [
        "",
        "## Notes",
        "",
        "Add your timeline here: what happened, in date order, one line per event, "
        "with the file numbers that prove each step.",
        "",
    ]
    (out / "INDEX.md").write_text("\n".join(lines))
    return entries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="evidence-packet", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="build a packet from a source folder")
    b.add_argument("source", type=Path)
    b.add_argument("out", type=Path)
    b.add_argument("--title", default="Evidence Packet")
    b.add_argument("--claimant", default="")
    args = parser.parse_args(argv)

    if args.command == "build":
        entries = build(args.source, args.out, args.title, args.claimant)
        print(f"Packet built: {args.out}")
        print(f"  {len(entries)} files indexed in INDEX.md and index.csv")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
