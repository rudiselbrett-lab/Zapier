"""
Output formatter — writes the final markdown report to output/report.md.
"""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path


def _item_md(item: dict) -> str:
    score = item.get("relevance_score")
    score_str = f" ⬥ relevance {score}/10" if score else ""
    return (
        f"**[{item['title']}]({item['url']})**{score_str}  \n"
        f"*{item['source']}*  \n"
        f"{item.get('summary', '')}  \n"
        f"> {item.get('why_it_matters', '')}\n"
    )


def write_markdown(report: dict, intent: str, output_path: str | None = None) -> str:
    today = date.today().isoformat()
    lines: list[str] = []

    lines.append(f"# Banking AI Intelligence Report")
    lines.append(f"*Generated {today} | Intent: {intent}*\n")
    lines.append("---\n")

    # WHAT CAUGHT MY ATTENTION
    lines.append("## What Caught My Attention\n")
    top = report.get("top_picks", [])
    if top:
        for item in top:
            lines.append(_item_md(item))
            lines.append("")
    else:
        lines.append("*No top picks surfaced.*\n")

    lines.append("---\n")

    # COMPETITOR MOVES
    lines.append("## Competitor Moves\n")
    moves = report.get("competitor_moves", {})
    institutions = ["JPMorgan", "Capital One", "Goldman Sachs", "Bank of America", "Wells Fargo"]
    for inst in institutions:
        items = moves.get(inst, [])
        lines.append(f"### {inst}")
        if items:
            for item in items:
                lines.append(_item_md(item))
                lines.append("")
        else:
            lines.append("*No notable moves found in this cycle.*\n")

    lines.append("---\n")

    # CONTENT WORTH YOUR TIME
    lines.append("## Content Worth Your Time\n")
    cwyt = report.get("content_worth_your_time", {})

    articles = cwyt.get("articles", [])
    lines.append("### Articles\n")
    if articles:
        for item in articles:
            lines.append(_item_md(item))
            lines.append("")
    else:
        lines.append("*No articles surfaced.*\n")

    videos = cwyt.get("videos", [])
    lines.append("### Videos\n")
    if videos:
        for item in videos:
            lines.append(_item_md(item))
            lines.append("")
    else:
        lines.append("*No videos surfaced.*\n")

    lines.append("---\n")

    # TECHNICAL RADAR
    lines.append("## Technical Radar\n")
    radar = report.get("technical_radar", {})

    for sub, label in [
        ("models_and_capabilities", "New Models & Capabilities"),
        ("frameworks_and_tooling", "Frameworks & Tooling"),
        ("research_papers", "Research Worth Reading"),
    ]:
        items = radar.get(sub, [])
        lines.append(f"### {label}\n")
        if items:
            for item in items:
                lines.append(_item_md(item))
                lines.append("")
        else:
            lines.append(f"*Nothing surfaced.*\n")

    lines.append("---\n")

    # RAW SOURCES
    lines.append("## Raw Sources\n")
    sources = report.get("all_sources", [])
    if sources:
        for s in sources:
            lines.append(f"- [{s.get('title', s.get('url', ''))}]({s.get('url', '')})")
    else:
        lines.append("*No sources listed.*")

    md = "\n".join(lines)

    out = output_path or os.path.join(os.path.dirname(__file__), "report.md")
    Path(out).write_text(md, encoding="utf-8")
    return out
