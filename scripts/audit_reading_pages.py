#!/usr/bin/env python3
"""Audit split-page coverage and practical limits for every SUMMARY reading page."""

from __future__ import annotations

import collections
import re
from pathlib import Path

from group_short_entries import GROUP_MARKER
from split_large_books import BOOKS, HEADING


SUMMARY_LINK = re.compile(r"\]\(([^)]+\.md)\)")


def heading_titles(path: Path) -> list[str]:
    return [
        match.group(1)
        for line in path.read_text().splitlines()
        if (match := HEADING.match(line)) and "目录" not in match.group(1)
    ]


def main() -> None:
    root = Path.cwd()
    failures: list[str] = []

    for relative, _, _ in BOOKS:
        source = root / relative
        expected = collections.Counter(heading_titles(source))
        actual: collections.Counter[str] = collections.Counter()
        for page in source.with_suffix("").rglob("*.md"):
            if page.name != "README.md":
                actual.update(heading_titles(page))
        if expected != actual:
            failures.append(f"coverage mismatch: {relative}")

    youhuashuo = root / "10.李敖节目演讲合集/李敖有话说.md"
    expected = collections.Counter(heading_titles(youhuashuo))
    actual: collections.Counter[str] = collections.Counter()
    for page in youhuashuo.with_suffix("").rglob("*.md"):
        if page.name != "README.md":
            actual.update(heading_titles(page))
    if expected != actual:
        failures.append("coverage mismatch: 李敖有话说")

    summary = (root / "SUMMARY.md").read_text()
    pages = [root / match for match in SUMMARY_LINK.findall(summary)]
    for page in pages:
        if not page.exists():
            failures.append(f"missing SUMMARY page: {page.relative_to(root)}")
            continue
        text = page.read_text()
        lines = len(text.splitlines())
        headings = len(re.findall(r"^## ", text, re.MULTILINE))
        grouped = GROUP_MARKER in text
        single_chapter = page.name != "README.md" and headings <= 1
        if lines > 3500 and not (grouped or single_chapter):
            failures.append(f"oversized page: {page.relative_to(root)} ({lines} lines)")
        if headings > 120:
            failures.append(f"oversized toc: {page.relative_to(root)} ({headings} headings)")

    print(
        f"split_books={len(BOOKS) + 1} summary_pages={len(pages)} "
        f"failures={len(failures)}"
    )
    for failure in failures:
        print(failure)
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
