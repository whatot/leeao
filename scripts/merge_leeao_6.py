#!/usr/bin/env python3
"""Conservatively merge uniquely anchored 6.0 paragraphs into existing books."""

from __future__ import annotations

import argparse
import csv
import difflib
import re
from collections import Counter
from pathlib import Path


SPACE = re.compile(r"[\s\u3000]+")
HEADING = re.compile(r"^\s*#{1,6}\s*")
SOURCE_BOILERPLATE = (
    "李敖影音E书QQ群",
    "李敖影音E书②群",
    "李敖影音书籍群不自由的自由",
    "李敖影音书籍QQ群敖友",
    "李敖影音书籍QQ群：",
    "李敖数字博物馆",
    "李敖研究网（需梯子）",
    "李敖资源下载站",
    "油管/抖音/西瓜/小红书/哔哩哔哩/今日头条",
)
DECORATIVE_SEPARATOR = re.compile(r"^(?:\*\s*){3,}$")


def decode_source(path: Path) -> list[str]:
    lines = []
    for raw in path.read_bytes().splitlines():
        try:
            lines.append(raw.decode("utf-8"))
        except UnicodeDecodeError:
            lines.append(raw.decode("gb18030"))
    return lines


def key(line: str) -> str:
    return SPACE.sub("", HEADING.sub("", line)).replace(r"\<", "<")


def is_source_boilerplate(line: str) -> bool:
    return DECORATIVE_SEPARATOR.fullmatch(line) is not None or any(
        marker in line for marker in SOURCE_BOILERPLATE
    )


def chunks(lines: list[str], source: bool = False) -> list[tuple[str, list[str]]]:
    result: list[tuple[str, list[str]]] = []
    for line in lines:
        normalized = line.strip(" \t\u3000") if source else line
        normalized_key = key(normalized)
        if normalized_key:
            result.append((normalized_key, [normalized]))
        elif result:
            result[-1][1].append("")
    return result


def merge(current: list[str], source: list[str]) -> tuple[list[str], int, int]:
    old = chunks(current)
    new = chunks(source, source=True)
    old_counts = Counter(item[0] for item in old)
    new_counts = Counter(item[0] for item in new)
    added_counts: Counter[str] = Counter()
    matcher = difflib.SequenceMatcher(None, [x[0] for x in old], [x[0] for x in new], autojunk=False)
    output: list[str] = []
    inserted = conflicts = 0
    opcodes = matcher.get_opcodes()
    for index, (tag, i1, i2, j1, j2) in enumerate(opcodes):
        if tag == "equal":
            for _, block in old[i1:i2]:
                output.extend(block)
        elif tag == "insert" and index > 0 and index + 1 < len(opcodes):
            for block_key, block in new[j1:j2]:
                if is_source_boilerplate(block[0]):
                    continue
                if old_counts[block_key] + added_counts[block_key] >= new_counts[block_key]:
                    continue
                output.extend(block)
                added_counts[block_key] += 1
                inserted += 1
        else:
            for _, block in old[i1:i2]:
                output.extend(block)
            conflicts += max(i2 - i1, j2 - j1)
    return output, inserted, conflicts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("numbers", nargs="+", type=int)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rows = {int(row["number"]): row for row in csv.DictReader((args.root / "sources/leeao-6.0.csv").open())}
    for number in args.numbers:
        row = rows[number]
        target = args.root / row["target"]
        source = args.source_dir / row["source_file"]
        merged, inserted, conflicts = merge(target.read_text().splitlines(), decode_source(source))
        print(f"{number:03d} {row['title']}: insert={inserted}, conflict={conflicts}")
        if args.apply and inserted:
            target.write_text("\n".join(merged).rstrip() + "\n")


if __name__ == "__main__":
    main()
