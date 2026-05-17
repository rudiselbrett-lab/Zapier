"""
Output formatter — writes report.md and artifact.html from the final report JSON.
"""
from __future__ import annotations

import json
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

    # Also write the interactive HTML artifact
    html_out = str(Path(out).parent / "artifact.html")
    write_artifact(report, intent, html_out)

    return out


def write_artifact(report: dict, intent: str, output_path: str | None = None) -> str:
    today = date.today().isoformat()
    report_json = json.dumps(report, ensure_ascii=False)

    # Read the JSX source to embed inline
    jsx_path = Path(__file__).parent / "artifact.jsx"
    jsx_source = jsx_path.read_text(encoding="utf-8") if jsx_path.exists() else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Banking AI Intelligence — {today}</title>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #f9fafb; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel" data-type="module">
    const reportData = {report_json};
    const intentStr = {json.dumps(intent)};
    const dateStr = {json.dumps(today)};

    {jsx_source}

    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(
      <App report={{reportData}} intent={{intentStr}} date={{dateStr}} />
    );
  </script>
</body>
</html>"""

    out = output_path or os.path.join(os.path.dirname(__file__), "artifact.html")
    Path(out).write_text(html, encoding="utf-8")
    return out
