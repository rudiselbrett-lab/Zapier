"""
Gmail Inbox Agent
-----------------
A conversational agent that manages your Gmail inbox using natural language.

Capabilities (via Zapier MCP Gmail actions):
  - Search and summarize emails
  - Read full email threads
  - Draft and send replies
  - Label, archive, or trash emails
  - Give you a prioritized inbox summary

Required environment variables:
  ANTHROPIC_API_KEY  – Anthropic API key
  ZAPIER_MCP_URL     – MCP endpoint from actions.zapier.com/mcp

Usage:
  python gmail_inbox_agent.py

Example commands:
  "Summarize my unread emails"
  "Show emails from john@example.com this week"
  "Draft a reply to the latest email from Sarah"
  "Archive all emails labeled newsletter"
"""

import os
import sys
import textwrap

import anthropic

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ANTHROPIC_API_KEY   = os.environ.get("ANTHROPIC_API_KEY", "")
ZAPIER_MCP_URL      = os.environ.get("ZAPIER_MCP_URL", "")
ENRICHMENT_MCP_URL  = os.environ.get("ENRICHMENT_MCP_URL", "")  # optional: second Zapier MCP with LinkedIn/search actions

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = textwrap.dedent("""
    You are a helpful Gmail inbox assistant. You help the user manage their
    email inbox efficiently using the available Gmail and web search tools.

    Your capabilities include:
    - Searching and reading emails by sender, subject, date, or label
    - Summarizing email threads and highlighting action items
    - Drafting replies or new emails on the user's behalf
    - Labeling, archiving, or organizing emails
    - Giving a prioritized summary of what needs attention
    - Enriching sender info with LinkedIn profile, job title, company, and background

    ## Sender Enrichment (always do this for real people)
    Whenever you present an email from a real person (not automated/noreply senders),
    attempt to look them up using available web search or LinkedIn tools.
    Extract and display:
      - Current job title and company
      - LinkedIn profile URL (if found)
      - A one-line bio or notable background detail
      - Mutual context clues from their email domain (e.g. company size, industry)

    Format enriched sender info like this:
      👤 Trevor Nocchi — Talent Acquisition, AssetMark
         linkedin.com/in/trevornocchi | Financial services, ~$100B AUM

    Skip enrichment for automated senders (noreply@, auto-confirm@, alerts, newsletters).
    If enrichment fails or no info is found, just note "No LinkedIn found" and move on.

    ## Guidelines
    - Always confirm before sending any email — show the draft and ask for approval
    - When summarizing multiple emails, highlight action items and deadlines
    - Be concise: one sentence per email in list views, full detail when asked
    - If a search returns too many results, ask the user to narrow it down
    - Never delete emails without explicit confirmation

    When the user asks for an inbox summary, search for unread emails,
    group them by urgency/sender, enrich real senders, and present a
    clean prioritized list.
""").strip()


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
    if not ENRICHMENT_MCP_URL:
        print("TIP: Set ENRICHMENT_MCP_URL to a Zapier MCP with LinkedIn Search or")
        print("     Web Search actions for richer sender profiles.\n")


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

def run_agent(conversation: list[dict]) -> str:
    """Send the current conversation to Claude and return its text response."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=conversation,
        mcp_servers=[
            s for s in [
                {"type": "url", "url": ZAPIER_MCP_URL, "name": "zapier"},
                {"type": "url", "url": ENRICHMENT_MCP_URL, "name": "enrichment"} if ENRICHMENT_MCP_URL else None,
            ] if s is not None
        ],
        betas=["mcp-client-2025-04-04"],
    )

    # Extract the final text reply
    reply = ""
    for block in response.content:
        if hasattr(block, "text"):
            reply += block.text

    return reply.strip()


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
            conversation.pop()  # remove the failed user message
            continue

        conversation.append({"role": "assistant", "content": reply})
        print(f"Agent: {reply}\n")


if __name__ == "__main__":
    main()
