"""
Orchestrator — hub-and-spoke coordinator.
Builds the research plan, runs agents in parallel via asyncio.gather(),
assembles state, and routes to Synthesis.
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import asdict

from sdk import ClaudeSDKClient, extract_json
from state import OrchestratorState, ResearchItem

logger = logging.getLogger(__name__)

ORCHESTRATOR_SYSTEM = """You are a research orchestrator for a banking AI intelligence system.
Your job is to translate a user's intent into a structured research plan.
Return valid JSON only."""


def _build_research_plan(client: ClaudeSDKClient, intent: str) -> dict:
    prompt = f"""The user wants: "{intent}"

Build a research plan for three parallel research lanes. Return JSON:
{{
  "topic": "concise topic string for all agents",
  "date_range": "last 30 days",
  "content_focus": "what the Content Agent should prioritize",
  "competitor_focus": "what the Competitor Agent should focus on",
  "technical_focus": "what the Technical Agent should look for"
}}"""

    raw = client.send(prompt)
    try:
        return extract_json(raw)
    except ValueError:
        logger.warning("Research plan parse failed, using defaults")
        return {
            "topic": intent,
            "date_range": "last 30 days",
            "content_focus": intent,
            "competitor_focus": intent,
            "technical_focus": intent,
        }


def _to_research_items(raw_list: list[dict], category: str) -> list[ResearchItem]:
    items = []
    for d in raw_list:
        try:
            items.append(
                ResearchItem(
                    title=d.get("title", "Untitled"),
                    url=d.get("url", ""),
                    source=d.get("source", ""),
                    summary=d.get("summary", ""),
                    why_it_matters=d.get("why_it_matters", ""),
                    category=category,
                    institution=d.get("institution"),
                    relevance_score=d.get("relevance_score"),
                )
            )
        except Exception as e:
            logger.warning("Skipping malformed item: %s", e)
    return items


async def _run_content(plan: dict) -> list[dict]:
    from agents import content_agent
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, content_agent.run, plan["topic"], plan.get("date_range", "last 30 days")
    )


async def _run_competitor(plan: dict) -> list[dict]:
    from agents import competitor_agent
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, competitor_agent.run, plan["topic"])


async def _run_technical(plan: dict) -> list[dict]:
    from agents import technical_agent
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, technical_agent.run, plan["topic"])


async def run(intent: str) -> OrchestratorState:
    state = OrchestratorState(intent=intent)

    client = ClaudeSDKClient(system=ORCHESTRATOR_SYSTEM)

    logger.info("Building research plan for: %s", intent)
    plan = _build_research_plan(client, intent)
    state.research_plan = plan
    logger.info("Research plan: %s", json.dumps(plan, indent=2))

    logger.info("Launching three research agents in parallel...")
    content_raw, competitor_raw, technical_raw = await asyncio.gather(
        _run_content(plan),
        _run_competitor(plan),
        _run_technical(plan),
    )

    state.content_output = _to_research_items(content_raw, "content")
    state.competitor_output = _to_research_items(competitor_raw, "competitor")
    state.technical_output = _to_research_items(technical_raw, "technical")

    logger.info(
        "Collected: %d content, %d competitor, %d technical items",
        len(state.content_output),
        len(state.competitor_output),
        len(state.technical_output),
    )

    return state
