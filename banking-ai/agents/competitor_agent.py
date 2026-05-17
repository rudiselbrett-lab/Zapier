"""
Competitor Agent — tracks AI moves at JPMorgan, Capital One, Goldman Sachs,
Bank of America, and Wells Fargo.
Returns a list of ResearchItem dicts (category: "competitor").
"""
from __future__ import annotations

import logging
from datetime import date

from sdk import query, extract_json

logger = logging.getLogger(__name__)

INSTITUTIONS = {
    "JPMorgan": {
        "priority": "high",
        "sources": "tech blog, earnings calls, press releases, job postings",
    },
    "Capital One": {
        "priority": "high",
        "sources": "tech blog, GitHub activity, press releases",
    },
    "Goldman Sachs": {
        "priority": "medium",
        "sources": "press releases, earnings calls, investor materials",
    },
    "Bank of America": {
        "priority": "medium",
        "sources": "press releases, earnings calls, job postings",
    },
    "Wells Fargo": {
        "priority": "medium",
        "sources": "press releases, earnings calls, job postings",
    },
}

SYSTEM = """You are a competitive intelligence analyst tracking AI adoption at major banks.
Your job is to find specific, concrete announcements, product launches, hiring signals,
and technical investments from these institutions.
Be factual — only report things that actually happened. Return valid JSON only."""


def _research_institution(name: str, meta: dict, topic: str, today: str) -> list[dict]:
    prompt = f"""Research recent AI developments at {name} (priority: {meta['priority']}).
Primary sources to check: {meta['sources']}
Topic focus: {topic}
Today: {today}

Find 2-4 specific, recent items: product launches, AI tool announcements, executive statements
about AI strategy, notable job postings (e.g. AI/ML leadership), GitHub releases, or earnings
call AI mentions.

Return a JSON array. Each item:
{{
  "title": "specific headline or finding",
  "url": "source URL (real and verifiable)",
  "source": "specific source name",
  "summary": "2-3 sentences describing exactly what {name} did or announced",
  "why_it_matters": "1-2 sentences on competitive significance",
  "category": "competitor",
  "institution": "{name}",
  "relevance_score": null
}}

Return JSON array only. If nothing notable found recently, return empty array []."""

    raw = query(prompt, system=SYSTEM, allowed_tools=["web_search"])
    try:
        items = extract_json(raw)
        if not isinstance(items, list):
            items = []
        for item in items:
            item["category"] = "competitor"
            item["institution"] = name
        return items
    except (ValueError, KeyError) as e:
        logger.error("Competitor agent parse error for %s: %s", name, e)
        return []


def run(topic: str) -> list[dict]:
    """
    Research AI moves across all covered institutions.
    Note: called from asyncio context — internal calls are sequential per institution
    since each is its own query() call.
    """
    today = date.today().isoformat()
    all_items: list[dict] = []

    for name, meta in INSTITUTIONS.items():
        items = _research_institution(name, meta, topic, today)
        all_items.extend(items)
        logger.info("Competitor agent: %s → %d items", name, len(items))

    return all_items
