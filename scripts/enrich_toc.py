#!/usr/bin/env python3
"""Promote repeated 6.0 catalog entries to headings and enable page TOCs."""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


ENTRY = re.compile(r"^(\d{3})\.(.+)$")
HEADING = re.compile(r"^##\s+")
TOC = "<!-- toc -->"
GROUP_MARKER = "<!-- leeao-entry-group -->"
CATALOG_HEADING = re.compile(r"^#《.+》目录$")


def enrich(path: Path) -> tuple[str, int]:
    source = path.read_text()
    lines = source.splitlines()
    if GROUP_MARKER in lines:
        heading_count = sum(HEADING.match(line) is not None for line in lines)
        return source, heading_count

    lines = [
        f"## {line[1:]}"
        if CATALOG_HEADING.match(line)
        else re.sub(r"^(#{2,6})(?=\S)", r"\1 ", line)
        for line in lines
    ]
    occurrences: dict[str, list[int]] = defaultdict(list)
    entries: list[tuple[int, str, str]] = []

    for index, line in enumerate(lines):
        match = ENTRY.match(line)
        if match:
            entries.append((index, line, match.group(2).strip()))
        occurrences[line].append(index)

    promoted: set[int] = set()
    seen: set[str] = set()
    for index, full, title in entries:
        if full in seen:
            promoted.add(index)
            continue
        seen.add(full)
        later_full = [item for item in occurrences[full] if item > index]
        if later_full:
            promoted.update(later_full)
            continue
        later_title = [item for item in occurrences[title] if item > index]
        promoted.update(later_title)

    output = [f"## {line}" if index in promoted else line for index, line in enumerate(lines)]
    heading_count = sum(HEADING.match(line) is not None for line in output)

    output = [line for line in output if line != TOC]
    while len(output) > 1 and not output[1]:
        output.pop(1)
    if heading_count >= 2:
        output[1:1] = ["", TOC, ""]

    return "\n".join(output).rstrip() + "\n", heading_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    with (args.root / "sources/leeao-6.0.csv").open() as handle:
        rows = list(csv.DictReader(handle))

    covered = promoted = 0
    for row in rows:
        path = args.root / row["target"]
        rendered, headings = enrich(path)
        changed = rendered != path.read_text()
        if headings >= 2:
            covered += 1
        if changed:
            promoted += 1
            if args.apply:
                path.write_text(rendered)
        print(f"{int(row['number']):03d} {row['title']}: headings={headings} {'change' if changed else 'unchanged'}")
    print(f"toc_covered={covered}/{len(rows)} changed={promoted}")


if __name__ == "__main__":
    main()
