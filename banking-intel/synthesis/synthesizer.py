"""
Synthesis Agent — deduplicates, scores relevance, and structures the final report.
No tools used — reasoning only.
"""
from __future__ import annotations

import json
import logging

from sdk import query, extract_json
from state import OrchestratorState, ResearchItem

logger = logging.getLogger(__name__)

SYSTEM = """You are a senior banking AI analyst producing an executive intelligence brief.
Your job is to synthesize research from three lanes into a structured, high-signal report.
Deduplicate aggressively — if two items cover the same story, keep the better one.
Score relevance honestly: 9-10 = must-read, 7-8 = valuable, 5-6 = background, 1-4 = noise.
Return valid JSON only."""


def _items_to_list(items: list[ResearchItem]) -> list[dict]:
    return [
        {
            "title": i.title,
            "url": i.url,
            "source": i.source,
            "summary": i.summary,
            "why_it_matters": i.why_it_matters,
            "category": i.category,
            "institution": i.institution,
        }
        for i in items
    ]


def run(state: OrchestratorState) -> dict:
    all_items = {
        "content": _items_to_list(state.content_output),
        "competitor": _items_to_list(state.competitor_output),
        "technical": _items_to_list(state.technical_output),
    }

    prompt = f"""You are synthesizing a banking AI intelligence report.

Research intent: {state.intent}

Here is the raw research from three agents:

CONTENT ITEMS (articles and videos):
{json.dumps(all_items['content'], indent=2)}

COMPETITOR ITEMS (bank moves):
{json.dumps(all_items['competitor'], indent=2)}

TECHNICAL ITEMS (models, frameworks, papers):
{json.dumps(all_items['technical'], indent=2)}

Produce a structured final report as JSON with this exact schema:
{{
  "top_picks": [
    {{
      "title": "...",
      "url": "...",
      "source": "...",
      "summary": "...",
      "why_it_matters": "...",
      "category": "content|competitor|technical",
      "institution": null,
      "relevance_score": 9
    }}
  ],
  "competitor_moves": {{
    "JPMorgan": [...],
    "Capital One": [...],
    "Goldman Sachs": [...],
    "Bank of America": [...],
    "Wells Fargo": [...]
  }},
  "content_worth_your_time": {{
    "articles": [...],
    "videos": [...]
  }},
  "technical_radar": {{
    "models_and_capabilities": [...],
    "frameworks_and_tooling": [...],
    "research_papers": [...]
  }},
  "all_sources": [...]
}}

Rules:
- top_picks: 3-5 highest-signal items across all lanes, each with relevance_score 8+
- competitor_moves: per-institution arrays; use empty [] if nothing found
- content_worth_your_time.articles: product/strategy angle items
- content_worth_your_time.videos: technical/educational videos (source contains "YouTube" or "video")
- technical_radar: split by sub-category
- all_sources: flat list of ALL items with url and title (for export)
- Set relevance_score (1-10) on every item in top_picks
- Deduplicate: if same story appears in multiple lanes, put it in the most relevant lane only
- Remove any item with a clearly fabricated or broken URL

Return JSON only."""

    raw = query(prompt, system=SYSTEM, allowed_tools=None)

    try:
        report = extract_json(raw)
        logger.info("Synthesis complete. Top picks: %d", len(report.get("top_picks", [])))
        return report
    except (ValueError, KeyError) as e:
        logger.error("Synthesizer parse error: %s\nRaw: %s", e, raw[:500])
        # Return minimal structure so formatter doesn't crash
        return {
            "top_picks": [],
            "competitor_moves": {k: [] for k in ["JPMorgan", "Capital One", "Goldman Sachs", "Bank of America", "Wells Fargo"]},
            "content_worth_your_time": {"articles": [], "videos": []},
            "technical_radar": {"models_and_capabilities": [], "frameworks_and_tooling": [], "research_papers": []},
            "all_sources": [],
            "_error": str(e),
            "_raw": raw[:1000],
        }
