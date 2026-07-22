#!/usr/bin/env python3
"""Generate readable pages for the remaining oversized 6.0 books."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path


BOOKS = [
    ("03.惊世杂文类/求是报.md", "month", 50),
    ("10.李敖节目演讲合集/李敖政论综艺集.md", "year", 50),
    ("10.李敖节目演讲合集/挑战李敖.md", "year", 50),
    ("10.李敖节目演讲合集/李敖大哥大.md", "balanced", 50),
    ("10.李敖节目演讲合集/李敖秘密书房.md", "balanced", 50),
    ("10.李敖节目演讲合集/李敖笑傲江湖.md", "balanced", 50),
    ("10.李敖节目演讲合集/李敖语妙天下.md", "balanced", 50),
    ("10.李敖节目演讲合集/李敖演讲集.md", "weighted", 3000),
    ("18.李敖出版社/汪政权的开场与收场.md", "weighted", 3000),
    ("18.李敖出版社/李宗仁回忆录.md", "weighted", 3000),
    ("18.李敖出版社/《血色黄昏》1987版.md", "weighted", 3000),
    ("18.李敖出版社/《血色黄昏》1997版.md", "weighted", 3000),
    ("06.沉思日记类/一个预备军官的日记.md", "weighted", 3000),
    ("05.诗集语录类/虽千万人，李敖往矣.md", "weighted", 3000),
    ("07.采访序跋类/李敖访谈录1990-2018.md", "weighted", 3000),
    ("04.小说剧本类/虚拟的十七岁.md", "weighted", 3000),
    ("10.李敖节目演讲合集/李敖Talk秀.md", "weighted", 3000),
    ("17.百家论李敖合集/百家论李敖.md", "weighted", 3000),
    ("05.诗集语录类/李敖语萃.md", "weighted", 3000),
    ("04.小说剧本类/上山·上山·爱.md", "weighted", 3000),
    ("04.小说剧本类/阳痿美国.md", "weighted", 3000),
    ("03.惊世杂文类/千秋万岁编外集.md", "weighted", 3000),
    ("18.李敖出版社/蒋经国传.md", "weighted", 3000),
    ("18.李敖出版社/卫士长谈毛泽东.md", "weighted", 3000),
    ("18.李敖出版社/调查局黑牢345天.md", "weighted", 3000),
    ("01.自传回忆类/李敖相关.md", "weighted", 3000),
    ("18.李敖出版社/长征——前所未闻的故事.md", "weighted", 3000),
    ("05.诗集语录类/李敖语录.md", "weighted", 3000),
    ("01.自传回忆类/李敖自传与回忆.md", "weighted", 3000),
    ("02.精品散文类/李敖全集.md", "weighted", 3000),
    ("03.惊世杂文类/你笨蛋，你笨蛋.md", "weighted", 3000),
    ("04.小说剧本类/第73烈士.md", "weighted", 3000),
    ("05.诗集语录类/爱情的秘密.md", "weighted", 3000),
    ("06.沉思日记类/早年日记.md", "weighted", 3000),
    ("06.沉思日记类/大学日记后期甲集.md", "weighted", 3000),
    ("06.沉思日记类/大学日记后期乙集.md", "weighted", 3000),
    ("06.沉思日记类/李敖五五日记.md", "weighted", 3000),
    ("08.书信函件类/李敖情书集.md", "weighted", 3000),
    ("08.书信函件类/坐牢家爸爸给女儿的八十封信.md", "weighted", 3000),
    ("10.李敖节目演讲合集/笑敖年代.md", "weighted", 3000),
    ("11.李敖电子报合集/李敖通电集.md", "weighted", 3000),
    ("12.人物研究类/胡适评传.md", "weighted", 3000),
    ("12.人物研究类/闽变研究与文星讼案.md", "weighted", 3000),
    ("12.人物研究类/蒋介石评传.md", "weighted", 3000),
    ("14.台湾史政类/你不知道的二二八.md", "weighted", 3000),
    ("17.百家论李敖合集/敖友论李敖.md", "weighted", 3000),
    ("17.百家论李敖合集/李戡专访与脸书合集.md", "weighted", 3000),
    ("18.李敖出版社/蒋介石张学良秘闻.md", "weighted", 3000),
    ("18.李敖出版社/拆穿蒋介石.md", "weighted", 3000),
    ("18.李敖出版社/蒋介石与蒋经国——毁灭的种子.md", "weighted", 3000),
    ("18.李敖出版社/军统内幕.md", "weighted", 3000),
    ("18.李敖出版社/政海秘辛.md", "weighted", 3000),
    ("18.李敖出版社/汪精卫传.md", "weighted", 3000),
    ("18.李敖出版社/《忆往谈旧录》2016版.md", "weighted", 3000),
    ("18.李敖出版社/中国近代社会研究.md", "weighted", 3000),
]

HEADING = re.compile(r"^## (.+)$")
DATE = re.compile(r"(?:《求是报》)?(\d{4})(\d{2})?(\d{2})?")


def balanced(items: list[dict], target: int) -> list[list[dict]]:
    count = max(1, round(len(items) / target))
    size, extra = divmod(len(items), count)
    result, offset = [], 0
    for index in range(count):
        length = size + (1 if index < extra else 0)
        result.append(items[offset : offset + length])
        offset += length
    return result


def bounded(items: list[dict], max_count: int = 50, max_lines: int = 3500) -> list[list[dict]]:
    result: list[list[dict]] = []
    current: list[dict] = []
    weight = 0
    for item in items:
        item_weight = item["end"] - item["index"]
        if current and (len(current) >= max_count or weight + item_weight > max_lines):
            result.append(current)
            current, weight = [], 0
        current.append(item)
        weight += item_weight
    if current:
        result.append(current)
    return result


def weighted(items: list[dict], target: int) -> list[list[dict]]:
    result: list[list[dict]] = []
    current: list[dict] = []
    weight = 0
    for item in items:
        item_weight = item["end"] - item["index"]
        if current and weight + item_weight > target:
            result.append(current)
            current, weight = [], 0
        current.append(item)
        weight += item_weight
    if current:
        result.append(current)
    return result


def safe_name(text: str) -> str:
    text = re.sub(r"[\\/:*?\"<>|]", "-", text)
    return re.sub(r"\s+", "-", text).strip("-.、—")[:48]


def write_book(root: Path, relative: str, mode: str, target: int) -> tuple[dict[Path, str], list[str]]:
    source = root / relative
    lines = source.read_text().splitlines()
    title = lines[0].removeprefix("# ").strip()
    output_dir = source.with_suffix("")
    items = []
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if match and "目录" not in match.group(1):
            date = DATE.match(match.group(1))
            items.append(
                {
                    "index": index,
                    "title": match.group(1),
                    "year": date.group(1) if date else None,
                    "month": f"{date.group(1)}-{date.group(2)}" if date and date.group(2) else None,
                }
            )
    for index, item in enumerate(items):
        item["end"] = items[index + 1]["index"] if index + 1 < len(items) else len(lines)

    sections: list[tuple[str | None, list[list[dict]]]] = []
    if mode in {"month", "year"}:
        grouped: dict[str, list[dict]] = defaultdict(list)
        for item in items:
            key = item["month"] if mode == "month" else item["year"]
            grouped[key or "其他"].append(item)
        for key in sorted(grouped):
            sections.append((key, bounded(grouped[key], max_count=target)))
    elif mode == "balanced":
        sections.append((None, bounded(items, max_count=target)))
    else:
        sections.append((None, weighted(items, target)))

    generated: dict[Path, str] = {}
    overview = [f"# {title}", "", f"原完整 6.0 文本保留在上级目录；此处按内容结构拆分为便于阅读的页面。", "", "## 分页目录", ""]
    summary = [f"  - [{title}]({output_dir.relative_to(root).as_posix()}/README.md)"]
    page_number = 0
    for section, groups in sections:
        section_lines = [f"# {title}：{section}", ""] if section else None
        if section:
            section_dir = output_dir / section
            overview.append(f"- [{section}]({section}/README.md)：{sum(len(group) for group in groups)} 项，{len(groups)} 页")
            summary.append(f"    - [{section}]({section_dir.relative_to(root).as_posix()}/README.md)")
        else:
            section_dir = output_dir
        for group in groups:
            page_number += 1
            first, last = group[0], group[-1]
            filename = f"{page_number:02d}-{safe_name(first['title'])}.md"
            label = f"{first['title']}—{last['title']}" if len(group) > 1 else first["title"]
            link = f"[{label}]({filename})（{len(group)} 项）"
            if section_lines is not None:
                section_lines.append(f"- {link}")
                summary.append(f"      - [{label}]({(section_dir / filename).relative_to(root).as_posix()})")
            else:
                overview.append(f"- {link}")
                summary.append(f"    - [{label}]({(section_dir / filename).relative_to(root).as_posix()})")
            body = [f"# {title}：{label}", "", "<!-- toc -->", ""]
            for item in group:
                body.extend(lines[item["index"] : item["end"]])
            generated[section_dir / filename] = "\n".join(body).rstrip() + "\n"
        if section_lines is not None:
            generated[section_dir / "README.md"] = "\n".join(section_lines).rstrip() + "\n"
    generated[output_dir / "README.md"] = "\n".join(overview).rstrip() + "\n"
    return generated, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    generated: dict[Path, str] = {}
    summary_path = args.root / "SUMMARY.md"
    summary_text = summary_path.read_text()
    for relative, mode, target in BOOKS:
        files, summary = write_book(args.root, relative, mode, target)
        generated.update(files)
        source = Path(relative)
        indent = "  "
        original = f"{indent}- [{source.stem}]({source.as_posix()})"
        replacement = "\n".join(summary)
        if original in summary_text:
            summary_text = summary_text.replace(original, replacement)
        elif replacement not in summary_text:
            raise SystemExit(f"SUMMARY entry not found: {source.stem}")

    changed = sum(not path.exists() or path.read_text() != content for path, content in generated.items())
    current_summary = summary_path.read_text()
    if summary_text != current_summary:
        changed += 1
    print(f"books={len(BOOKS)} files={len(generated)} changed={changed}")
    if args.apply:
        for path, content in generated.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        summary_path.write_text(summary_text)


if __name__ == "__main__":
    main()
