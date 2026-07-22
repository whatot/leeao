#!/usr/bin/env python3
"""Group dense short-entry books without splitting them into separate files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


BOOKS = [
    ("01.自传回忆类/李敖风流自传.md", 50),
    ("05.诗集语录类/李语录.md", 100),
    ("06.沉思日记类/大学札记.md", 50),
    ("06.沉思日记类/李敖札记.md", 50),
    ("06.沉思日记类/李敖随写录前集.md", 50),
    ("06.沉思日记类/李敖随写录后集.md", 50),
    ("03.惊世杂文类/千秋万岁乌鸦求是合集.md", 50),
    ("01.自传回忆类/李敖议坛哀思录.md", 50),
    ("17.百家论李敖合集/四十二年，我的“恶邻”李敖大师.md", 50),
    ("05.诗集语录类/李敖的情诗.md", 50),
    ("12.人物研究类/大江大海骗了你.md", 50),
    ("03.惊世杂文类/世论新语.md", 50),
    ("03.惊世杂文类/求是新语.md", 50),
]

GROUP_MARKER = "<!-- leeao-entry-group -->"
ENTRY = re.compile(r"^#{2,3} (.+)$")


def group(path: Path, size: int) -> tuple[str, int]:
    source = path.read_text().splitlines()
    cleaned: list[str] = []
    skip_heading = False
    skip_blank = False
    for line in source:
        if line == GROUP_MARKER:
            skip_heading = True
            continue
        if skip_heading and line.startswith("## "):
            skip_heading = False
            skip_blank = True
            continue
        if skip_blank and not line:
            skip_blank = False
            continue
        skip_blank = False
        cleaned.append(line)

    entries = []
    for index, line in enumerate(cleaned):
        match = ENTRY.match(line)
        if match and "目录" not in match.group(1):
            entries.append(index)

    entry_set = set(entries)
    output: list[str] = []
    ordinal = 0
    for index, line in enumerate(cleaned):
        if index in entry_set:
            if ordinal % size == 0:
                start = ordinal + 1
                end = min(len(entries), ordinal + size)
                output.extend([GROUP_MARKER, f"## 第 {start:03d}–{end:03d} 项", ""])
            output.append(re.sub(r"^#{2,3} ", "### ", line))
            ordinal += 1
        else:
            output.append(line)
    return "\n".join(output).rstrip() + "\n", len(entries)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    changed = 0
    for relative, size in BOOKS:
        path = args.root / relative
        rendered, entries = group(path, size)
        is_changed = rendered != path.read_text()
        changed += is_changed
        print(f"{path.stem}: entries={entries} group_size={size} {'change' if is_changed else 'unchanged'}")
        if args.apply and is_changed:
            path.write_text(rendered)
    print(f"books={len(BOOKS)} changed={changed}")


if __name__ == "__main__":
    main()
