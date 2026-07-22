#!/usr/bin/env python3
"""Audit whether every meaningful 6.0 source line exists in its Markdown book."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from merge_leeao_6 import chunks, decode_source, is_source_boilerplate


def meaningful_source_counts(path: Path) -> Counter[str]:
    return Counter(
        block_key
        for block_key, block in chunks(decode_source(path), source=True)
        if not is_source_boilerplate(block[0])
    )


def current_counts(path: Path) -> Counter[str]:
    return Counter(block_key for block_key, _ in chunks(path.read_text().splitlines()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    manifest = args.root / "sources/leeao-6.0.csv"
    results: list[dict[str, str | int]] = []
    with manifest.open() as handle:
        for row in csv.DictReader(handle):
            source = meaningful_source_counts(args.source_dir / row["source_file"])
            current = current_counts(args.root / row["target"])
            missing = source - current
            results.append(
                {
                    "number": row["number"],
                    "title": row["title"],
                    "source_lines": sum(source.values()),
                    "missing_lines": sum(missing.values()),
                }
            )

    if args.output:
        output = args.output if args.output.is_absolute() else args.root / args.output
        with output.open("w", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=results[0].keys(), lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(results)

    incomplete = [row for row in results if row["missing_lines"]]
    for row in incomplete:
        print(f"{row['number']} {row['title']}: missing={row['missing_lines']}/{row['source_lines']}")
    print(f"complete={len(results) - len(incomplete)}/{len(results)} incomplete={len(incomplete)}")


if __name__ == "__main__":
    main()
