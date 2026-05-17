"""
Thin wrappers that match the PRD's sdk patterns:
  query()           - stateless single-turn agent call (with optional tool loop)
  ClaudeSDKClient   - stateful multi-turn Orchestrator session
"""
from __future__ import annotations

import json
import os
import re
import time
from typing import Optional

import anthropic

MODEL = "claude-opus-4-7"

_WEB_TOOLS = [
    {
        "type": "web_search_20250305",
        "name": "web_search",
    },
]

_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def _run_tool_loop(
    messages: list[dict],
    tools: list[dict],
    system: str,
    max_iterations: int = 10,
) -> str:
    """Execute a tool-use loop, returning the final text response."""
    for _ in range(max_iterations):
        kwargs: dict = {"model": MODEL, "max_tokens": 4096, "messages": messages}
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["betas"] = ["web-search-2025-03-05"]
            kwargs["tools"] = tools

        response = _client.beta.messages.create(**kwargs)

        # Collect any text blocks
        text_blocks = [b.text for b in response.content if hasattr(b, "text")]

        if response.stop_reason == "end_turn":
            return "\n".join(text_blocks)

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    # Web search results are returned by the API automatically;
                    # we just need to pass them back as tool_result blocks.
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": getattr(block, "content", ""),
                        }
                    )
            messages = messages + [
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": tool_results},
            ]
            continue

        # Unexpected stop
        return "\n".join(text_blocks)

    return ""


def query(
    prompt: str,
    system: str = "",
    allowed_tools: Optional[list[str]] = None,
) -> str:
    """
    Stateless single-turn agent call.

    allowed_tools: list of tool names to enable, e.g. ["web_search"].
    Pass None or [] for reasoning-only agents (Synthesis).
    """
    tools: list[dict] = []
    if allowed_tools:
        for name in allowed_tools:
            if name in ("web_search", "WebSearch"):
                tools.append(_WEB_TOOLS[0])

    messages = [{"role": "user", "content": prompt}]
    return _run_tool_loop(messages, tools, system)


class ClaudeSDKClient:
    """Stateful multi-turn client for the Orchestrator."""

    def __init__(self, system: str = ""):
        self.system = system
        self.history: list[dict] = []

    def send(self, message: str) -> str:
        self.history.append({"role": "user", "content": message})
        result = _run_tool_loop(self.history, tools=[], system=self.system)
        self.history.append({"role": "assistant", "content": result})
        return result


def extract_json(text: str) -> dict | list:
    """Parse JSON from agent output, stripping markdown fences if present."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strip ```json ... ``` fences
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Last resort: find the first { or [ and parse from there
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        idx = text.find(start_char)
        if idx != -1:
            # Find matching close
            depth = 0
            for i, ch in enumerate(text[idx:], idx):
                if ch == start_char:
                    depth += 1
                elif ch == end_char:
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[idx:i+1])
                        except json.JSONDecodeError:
                            break

    raise ValueError(f"No valid JSON found in agent output:\n{text[:500]}")
