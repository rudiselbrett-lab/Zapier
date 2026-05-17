"""
Gmail Inbox Agent
-----------------
A conversational agent that manages your Gmail inbox using natural language.
Automatically enriches real senders with LinkedIn profile, job title, and bio.

Capabilities (via Zapier MCP + built-in web search):
  - Search and summarize emails
  - Read full email threads
  - Draft and send replies
  - Label, archive, or trash emails
  - Prioritized inbox summary with LinkedIn context for every real sender

Required environment variables:
  ANTHROPIC_API_KEY  – Anthropic API key
  ZAPIER_MCP_URL     – MCP endpoint from actions.zapier.com/mcp

Usage:
  python gmail_inbox_agent.py

Example commands:
  "Summarize my unread emails"
  "Show emails from john@example.com this week"
  "Draft a reply to the latest email from Sarah"
  "Archive all newsletter emails"
"""

import json
import os
import sys
import textwrap

import anthropic
from duckduckgo_search import DDGS

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ZAPIER_MCP_URL    = os.environ.get("ZAPIER_MCP_URL", "")

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = textwrap.dedent("""
    You are a helpful Gmail inbox assistant. You help the user manage their
    email inbox efficiently using Gmail tools and web search.

    Your capabilities include:
    - Searching and reading emails by sender, subject, date, or label
    - Summarizing email threads and highlighting action items
    - Drafting replies or new emails on the user's behalf
    - Labeling, archiving, or organizing emails
    - Giving a prioritized summary of what needs attention

    ## Sender Enrichment (always do this for real people)
    Whenever you present an email from a real person, call search_web to look
    them up on LinkedIn before displaying their email. Use the query format:
      "<First Last> <Company> LinkedIn"

    Display enriched info like this:
      👤 Trevor Nocchi — Talent Acquisition Partner, AssetMark
         linkedin.com/in/trevor-nocchi | ~8 yrs recruiting, Phoenix AZ

    Skip enrichment for automated senders: noreply@, auto-confirm@,
    no-reply@, alerts, newsletters, and bulk mailers.
    If no LinkedIn is found, just omit the enrichment line.

    ## Guidelines
    - Always confirm before sending any email — show the draft and ask for approval
    - When summarizing multiple emails, highlight action items and deadlines
    - Be concise: one sentence per email in list views, full detail when asked
    - Never delete emails without explicit confirmation

    When the user asks for an inbox summary, search for unread emails,
    enrich every real sender, then present a clean prioritized list.
""").strip()

TOOLS = [
    {
        "name": "search_web",
        "description": (
            "Search the web for information about a person or company. "
            "Use this to find LinkedIn profiles, job titles, and professional "
            "background for email senders. Query format: '<Name> <Company> LinkedIn'"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query, e.g. 'Trevor Nocchi AssetMark LinkedIn'"
                }
            },
            "required": ["query"]
        }
    }
]


# ---------------------------------------------------------------------------
# Tool implementation
# ---------------------------------------------------------------------------

def search_web(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))
        if not results:
            return "No results found."
        return json.dumps([
            {"title": r["title"], "url": r["href"], "snippet": r["body"]}
            for r in results
        ], indent=2)
    except Exception as e:
        return f"Search failed: {e}"


def handle_tool_call(name: str, inputs: dict) -> str:
    if name == "search_web":
        return search_web(inputs["query"])
    return f"Unknown tool: {name}"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_env() -> None:
    missing = [v for v in ("ANTHROPIC_API_KEY", "ZAPIER_MCP_URL")
               if not os.environ.get(v)]
    if missing:
        print("ERROR: Missing required environment variables:")
        for v in missing:
            print(f"  {v}")
        print("\nSet them before running, e.g.:")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        print("  export ZAPIER_MCP_URL=https://mcp.zapier.com/...")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

def run_agent(conversation: list[dict]) -> str:
    """Run the agent loop, handling search_web tool calls client-side."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    messages = list(conversation)

    while True:
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=TOOLS,
            mcp_servers=[
                {"type": "url", "url": ZAPIER_MCP_URL, "name": "zapier"}
            ],
            betas=["mcp-client-2025-04-04"],
        )

        # Collect any client-side tool calls (search_web)
        tool_uses = [b for b in response.content if getattr(b, "type", None) == "tool_use"]

        if not tool_uses:
            # No more tool calls — extract final text and return
            return "".join(
                b.text for b in response.content if hasattr(b, "text")
            ).strip()

        # Execute each tool call and build results
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for tool_use in tool_uses:
            result = handle_tool_call(tool_use.name, tool_use.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result,
            })
        messages.append({"role": "user", "content": tool_results})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    validate_env()

    print("Gmail Inbox Agent")
    print("=" * 40)
    print("Ask me anything about your inbox.")
    print('Type "exit" or press Ctrl+C to quit.\n')
    print("Examples:")
    print('  "Summarize my unread emails"')
    print('  "Show emails from john@example.com"')
    print('  "Draft a reply to the latest email from Sarah"')
    print('  "Archive all newsletter emails"\n')

    conversation: list[dict] = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "bye"):
            print("Goodbye!")
            break

        conversation.append({"role": "user", "content": user_input})
        print("\nThinking...\n")

        try:
            reply = run_agent(conversation)
        except anthropic.APIError as e:
            print(f"API error: {e}\n")
            conversation.pop()
            continue

        conversation.append({"role": "assistant", "content": reply})
        print(f"Agent: {reply}\n")


if __name__ == "__main__":
    main()
