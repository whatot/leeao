#!/usr/bin/env python3
"""Import missing books from the GOLGO11 大李敖全集 6.0 TXT release."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


CATEGORIES = [
    (1, 8, "01.自传回忆类"), (9, 15, "02.精品散文类"),
    (16, 31, "03.惊世杂文类"), (32, 37, "04.小说剧本类"),
    (38, 43, "05.诗集语录类"), (44, 53, "06.沉思日记类"),
    (54, 58, "07.采访序跋类"), (59, 70, "08.书信函件类"),
    (71, 81, "09.历史文化类"), (82, 94, "10.李敖节目演讲合集"),
    (95, 99, "11.李敖电子报合集"), (100, 126, "12.人物研究类"),
    (127, 132, "13.国民党史政类"), (133, 141, "14.台湾史政类"),
    (142, 147, "15.雷霆法律类"), (148, 157, "16.李敖祸台十书"),
    (158, 165, "17.百家论李敖合集"), (166, 195, "18.李敖出版社"),
]
NUMBERED = re.compile(r"^(\d{3})\.?(.*)$")


def category_for(number: int) -> str:
    return next(category for start, end, category in CATEGORIES if start <= number <= end)


def source_books(source_dir: Path):
    for source in sorted(source_dir.glob("*.txt")):
        match = NUMBERED.match(source.stem)
        if match:
            yield int(match.group(1)), match.group(2), source


def update_summary(root: Path, rows: list[tuple]) -> None:
    summary = root / "SUMMARY.md"
    lines = summary.read_text().splitlines()
    for _, _, category in reversed(CATEGORIES):
        if not (root / category).exists():
            continue
        start = next(i for i, line in enumerate(lines) if line.startswith(f"- [") and f"({category}/README.md)" in line)
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("- [")), len(lines))
        books = [(number, title, target) for number, title, _, row_category, target, _ in rows if row_category == category]
        source_targets = {target for _, _, target in books}
        legacy = sorted(
            path for path in (root / category).glob("*.md")
            if path.name != "README.md" and str(path.relative_to(root)) not in source_targets
        )
        children = [f"  - [{title}]({target})" for _, title, target in sorted(books)]
        children += [f"  - [{path.stem}]({path.relative_to(root)})" for path in legacy]
        lines[start + 1:end] = children
    summary.write_text("\n".join(lines) + "\n")


def markdown_text(title: str, source: Path) -> str:
    lines = []
    for raw_line in source.read_bytes().splitlines():
        try:
            lines.append(raw_line.decode("utf-8"))
        except UnicodeDecodeError:
            lines.append(raw_line.decode("gb18030"))
    normalized = [line.strip(" \t\u3000") for line in lines]
    body = "\n".join(normalized).strip()
    return f"# {title}\n\n{body}\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--max-number", type=int, default=165)
    args = parser.parse_args()

    rows = []
    imported = 0
    for number, title, source in source_books(args.source_dir):
        category = category_for(number)
        target = args.root / category / f"{title}.md"
        status = "present" if target.exists() else "pending"
        if number <= args.max_number and not target.exists():
            target.parent.mkdir(exist_ok=True)
            target.write_text(markdown_text(title, source), encoding="utf-8")
            status = "present"
            imported += 1
        rows.append((number, title, source.name, category, str(target.relative_to(args.root)), status))

    manifest = args.root / "sources" / "leeao-6.0.csv"
    manifest.parent.mkdir(exist_ok=True)
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("number", "title", "source_file", "category", "target", "status"))
        writer.writerows(rows)
    update_summary(args.root, rows)
    print(f"imported books: {imported}")
    print(f"manifest entries: {len(rows)}")


if __name__ == "__main__":
    main()
