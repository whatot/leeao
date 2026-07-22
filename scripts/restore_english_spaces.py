#!/usr/bin/env python3
"""Restore spaces inside ASCII text from the original GB18030 TXT books."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path


RENAMES = {
    "上山上山爱": "上山·上山·爱",
    "我梦碎所以我梦醒": "我梦碎，所以我梦醒",
    "李敖有话说1-735全集": "李敖有话说",
    "李敖访谈录1996-2014": "李敖访谈录1990-2018",
    "蒋介石研究一集": "蒋介石研究",
}

HEADING = re.compile(r"^(\s*#{1,6}\s*)(.*)$")
BOOK_NUMBER = re.compile(r"^\d{3}\.?", re.ASCII)
SPACE = re.compile(r"[ \t\u3000]")


def content(line: str) -> tuple[str, str]:
    match = HEADING.match(line)
    return (match.group(1), match.group(2)) if match else ("", line)


def key(line: str) -> str:
    return SPACE.sub("", content(line)[1]).strip()


def source_gaps(line: str) -> dict[int, str]:
    """Return spaces before non-space character indexes in source text."""
    gaps: dict[int, str] = {}
    chars_seen = 0
    pending = ""
    previous = ""
    for char in line:
        if char in " \t\u3000":
            pending += char
            continue
        if pending and previous and previous.isascii() and char.isascii():
            gaps[chars_seen] = " "
        pending = ""
        previous = char
        chars_seen += 1
    return gaps


def restore_line(line: str, source: str) -> tuple[str, int]:
    prefix, body = content(line)
    gaps = source_gaps(source)
    if not gaps:
        return line, 0

    result: list[str] = []
    chars_seen = 0
    whitespace_since_character = False
    restored = 0
    for char in body:
        if char in " \t\u3000":
            whitespace_since_character = True
            result.append(char)
            continue
        if chars_seen in gaps and not whitespace_since_character:
            result.append(gaps[chars_seen])
            restored += 1
        result.append(char)
        chars_seen += 1
        whitespace_since_character = False
    return prefix + "".join(result), restored


def source_books(source_dir: Path) -> dict[str, Path]:
    return {
        BOOK_NUMBER.sub("", path.stem): path
        for path in source_dir.glob("*.txt")
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    books = source_books(args.source_dir)
    files_changed = lines_changed = spaces_restored = 0
    books_missing: list[str] = []

    for markdown in sorted(args.root.glob("[0-9][0-9].*/*.md")):
        if markdown.name == "README.md":
            continue
        source_name = RENAMES.get(markdown.stem, markdown.stem)
        source_path = books.get(source_name)
        if source_path is None:
            books_missing.append(markdown.stem)
            continue

        candidates: dict[str, list[str]] = defaultdict(list)
        for line in source_path.read_text(encoding="gb18030").splitlines():
            if normalized := key(line):
                candidates[normalized].append(line)

        original = markdown.read_text()
        output: list[str] = []
        file_lines_changed = file_spaces_restored = 0
        for line in original.splitlines(keepends=True):
            ending = "\n" if line.endswith("\n") else ""
            body = line[:-1] if ending else line
            matches = candidates.get(key(body), [])
            if len(matches) == 1:
                restored_line, count = restore_line(body, matches[0])
                if count:
                    body = restored_line
                    file_lines_changed += 1
                    file_spaces_restored += count
            output.append(body + ending)

        updated = "".join(output)
        if updated != original:
            markdown.write_text(updated)
            files_changed += 1
            lines_changed += file_lines_changed
            spaces_restored += file_spaces_restored

    print(f"files changed: {files_changed}")
    print(f"lines changed: {lines_changed}")
    print(f"spaces restored: {spaces_restored}")
    if books_missing:
        print("books without a matching TXT: " + ", ".join(books_missing))


if __name__ == "__main__":
    main()
