#!/usr/bin/env python3
"""Rewrite book bodies from the canonical 6.0 text while preserving Markdown headings."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from merge_leeao_6 import chunks, decode_source, is_source_boilerplate, key


def canonical_markdown(target: Path, source: Path, title: str) -> str:
    current = target.read_text().splitlines()
    headings = {
        key(line): line
        for line in current
        if line.startswith("#") and key(line) != key(title)
    }

    body: list[str] = []
    for line in decode_source(source):
        stripped = line.strip(" \t\u3000")
        if stripped and is_source_boilerplate(stripped):
            continue
        stripped = stripped.replace("<XX>", r"\<XX>")
        body.append(headings.get(key(stripped), stripped) if stripped else "")

    while body and not body[0]:
        body.pop(0)
    while body and not body[-1]:
        body.pop()
    return f"# {title}\n\n" + "\n".join(body) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("numbers", nargs="*", type=int)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    with (args.root / "sources/leeao-6.0.csv").open() as handle:
        rows = {int(row["number"]): row for row in csv.DictReader(handle)}
    numbers = args.numbers or sorted(rows)

    for number in numbers:
        row = rows[number]
        target = args.root / row["target"]
        source = args.source_dir / row["source_file"]
        rendered = canonical_markdown(target, source, row["title"])
        changed = rendered != target.read_text()
        print(f"{number:03d} {row['title']}: {'change' if changed else 'unchanged'}")
        if args.apply and changed:
            target.write_text(rendered)


if __name__ == "__main__":
    main()
