"""
Technical Agent — tracks AI models, frameworks, and research papers relevant to banking.
Returns a list of ResearchItem dicts (category: "technical").
"""
from __future__ import annotations

import logging
from datetime import date

from sdk import query, extract_json

logger = logging.getLogger(__name__)

FOCUS_AREAS = [
    "new LLM model releases and capabilities relevant to financial services",
    "AI frameworks and tooling for enterprise/regulated industries",
    "research papers on AI in finance, credit, fraud, or compliance",
]

SYSTEM = """You are a technical AI research analyst focused on financial services.
Your job is to find concrete technical developments: model releases, framework updates,
and research papers that banking technologists should know about.
Be specific — include model names, version numbers, paper titles. Return valid JSON only."""


def run(topic: str) -> list[dict]:
    today = date.today().isoformat()

    focus_str = "\n".join(f"- {a}" for a in FOCUS_AREAS)

    prompt = f"""Research the latest technical AI developments relevant to banking and finance.
Topic context: {topic}
Today: {today}

Cover these areas:
{focus_str}

Find 8-12 items total across all areas. Return a JSON array. Each item:
{{
  "title": "specific model name, framework, or paper title",
  "url": "source URL — paper link, GitHub repo, official announcement (must be real)",
  "source": "source name (arXiv, Hugging Face, GitHub, company blog, etc.)",
  "summary": "2-3 sentences on what this is and what it does",
  "why_it_matters": "1-2 sentences on relevance to banking/financial services technologists",
  "category": "technical",
  "institution": null,
  "relevance_score": null
}}

Split across:
- "models_and_capabilities": new model releases or capability announcements
- "frameworks_and_tooling": open-source tools, SDKs, infrastructure updates
- "research_papers": peer-reviewed or preprint papers with banking/finance angle

Return JSON array only."""

    raw = query(prompt, system=SYSTEM, allowed_tools=["web_search"])

    try:
        items = extract_json(raw)
        if not isinstance(items, list):
            items = [items]
        for item in items:
            item["category"] = "technical"
        logger.info("Technical agent returned %d items", len(items))
        return items
    except (ValueError, KeyError) as e:
        logger.error("Technical agent parse error: %s\nRaw: %s", e, raw[:300])
        return []
