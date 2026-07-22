#!/usr/bin/env python3
"""Generate year-aware, roughly 50-episode pages for 李敖有话说."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path


EPISODE = re.compile(r"^## (\d{3})\.(\d{4})-(\d{2})-(\d{2})[：:](.+)$")
SUMMARY_LINK = "  - [李敖有话说](10.李敖节目演讲合集/李敖有话说.md)"


def balanced(items: list[tuple], target: int = 50) -> list[list[tuple]]:
    count = max(1, round(len(items) / target))
    size, extra = divmod(len(items), count)
    result = []
    offset = 0
    for index in range(count):
        length = size + (1 if index < extra else 0)
        result.append(items[offset : offset + length])
        offset += length
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    source = args.root / "10.李敖节目演讲合集/李敖有话说.md"
    output_dir = source.with_suffix("")
    lines = source.read_text().splitlines()
    episodes = []
    for index, line in enumerate(lines):
        match = EPISODE.match(line)
        if match:
            episodes.append(
                {
                    "index": index,
                    "number": int(match.group(1)),
                    "year": match.group(2),
                    "date": f"{match.group(2)}-{match.group(3)}-{match.group(4)}",
                    "title": match.group(5),
                }
            )
    for index, episode in enumerate(episodes):
        episode["end"] = episodes[index + 1]["index"] if index + 1 < len(episodes) else len(lines)

    years: dict[str, list[dict]] = defaultdict(list)
    for episode in episodes:
        years[episode["year"]].append(episode)

    generated: dict[Path, str] = {}
    summary = ["  - [李敖有话说](10.李敖节目演讲合集/李敖有话说/README.md)"]
    overview = [
        "# 李敖有话说",
        "",
        "原书共收录 729 期节目文字，按自然年组织，并在每年内均衡拆分为约 50 期一页。",
        "",
        "完整、未经拆分的 6.0 对照文本仍保留在上级目录，用于来源审计。",
        "",
        "## 年度目录",
        "",
    ]

    page_count = 0
    for year in sorted(years):
        groups = balanced(years[year])
        year_index = [f"# 李敖有话说：{year} 年", ""]
        summary.append(f"    - [{year} 年](10.李敖节目演讲合集/李敖有话说/{year}/README.md)")
        overview.append(f"- [{year} 年]({year}/README.md)：{len(years[year])} 期，{len(groups)} 页")
        for group in groups:
            first, last = group[0], group[-1]
            filename = f"{first['number']:03d}-{last['number']:03d}.md"
            label = f"第 {first['number']:03d}–{last['number']:03d} 期"
            year_index.append(f"- [{label}]({filename})（{first['date']} 至 {last['date']}）")
            summary.append(
                f"      - [{label}](10.李敖节目演讲合集/李敖有话说/{year}/{filename})"
            )
            body = [f"# 李敖有话说：{year} 年 {label}", "", "<!-- toc -->", ""]
            for episode in group:
                body.extend(lines[episode["index"] : episode["end"]])
            generated[output_dir / year / filename] = "\n".join(body).rstrip() + "\n"
            page_count += 1
        generated[output_dir / year / "README.md"] = "\n".join(year_index).rstrip() + "\n"
    generated[output_dir / "README.md"] = "\n".join(overview).rstrip() + "\n"

    summary_path = args.root / "SUMMARY.md"
    summary_text = summary_path.read_text()
    replacement = "\n".join(summary)
    if SUMMARY_LINK not in summary_text and replacement not in summary_text:
        raise SystemExit("李敖有话说 SUMMARY entry not found")
    rendered_summary = summary_text.replace(SUMMARY_LINK, replacement)

    changed = sum(not path.exists() or path.read_text() != content for path, content in generated.items())
    if rendered_summary != summary_text:
        changed += 1
    print(f"episodes={len(episodes)} years={len(years)} pages={page_count} changed={changed}")
    for year in sorted(years):
        sizes = [len(group) for group in balanced(years[year])]
        print(f"{year}: episodes={len(years[year])} pages={len(sizes)} sizes={sizes}")

    if args.apply:
        for path, content in generated.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        summary_path.write_text(rendered_summary)


if __name__ == "__main__":
    main()
