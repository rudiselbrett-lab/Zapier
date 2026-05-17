"""
Content Agent — finds articles and YouTube videos on banking AI topics.
Returns a list of ResearchItem dicts (category: "content").
"""
from __future__ import annotations

import json
import logging
from datetime import date

from sdk import query, extract_json

logger = logging.getLogger(__name__)

SYSTEM = """You are a banking AI research analyst. Your job is to find high-quality,
recent articles and YouTube videos about AI adoption in banking and financial services.
Focus on product/strategy articles and technical/educational videos.
Always return valid JSON only — no prose, no markdown fences."""


def run(topic: str, date_range: str = "last 30 days") -> list[dict]:
    """
    Search for content on `topic` within `date_range`.
    Returns list of ResearchItem-compatible dicts.
    """
    today = date.today().isoformat()

    prompt = f"""Research the latest content on: "{topic}" in banking and financial services.
Date range: {date_range} (today is {today}).

Search for:
1. Articles from trade press (American Banker, Finextra, The Financial Brand, Forbes Finance, etc.)
2. YouTube videos from practitioners, bank tech teams, or industry conferences
3. Newsletter highlights from sources like a16z, Andreessen Horowitz Fintech, or industry analysts

Return a JSON array of 10-15 items. Each item must have exactly these fields:
{{
  "title": "exact title",
  "url": "full URL (must be real and verifiable)",
  "source": "publication or channel name",
  "summary": "2-3 sentence summary of the content",
  "why_it_matters": "1-2 sentences on why this is relevant to banking AI practitioners",
  "category": "content",
  "institution": null,
  "relevance_score": null
}}

Filter out anything older than {date_range}. Return JSON array only."""

    raw = query(prompt, system=SYSTEM, allowed_tools=["web_search"])

    try:
        items = extract_json(raw)
        if not isinstance(items, list):
            items = [items]
        # Enforce category
        for item in items:
            item["category"] = "content"
        logger.info("Content agent returned %d items", len(items))
        return items
    except (ValueError, KeyError) as e:
        logger.error("Content agent parse error: %s\nRaw: %s", e, raw[:300])
        return []
