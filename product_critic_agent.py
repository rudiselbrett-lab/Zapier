"""
Product Critic Agent
--------------------
Paste a product description, URL, or name at the prompt.
Claude delivers a structured critique, then uses Zapier MCP to:
  1. Append the critique to Google Sheets  (tool: log_critique_to_sheets)
  2. Send the critique via Gmail           (tool: send_critique_email)

Required environment variables:
  ANTHROPIC_API_KEY  – Anthropic API key
  ZAPIER_MCP_URL     – MCP endpoint from actions.zapier.com/mcp
  RECIPIENT_EMAIL    – Destination address for the critique email
"""

import os
import sys
import textwrap

import anthropic

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ZAPIER_MCP_URL    = os.environ.get("ZAPIER_MCP_URL", "")
RECIPIENT_EMAIL   = os.environ.get("RECIPIENT_EMAIL", "")

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = textwrap.dedent(f"""
    You are a sharp, honest product critic with expertise in UX, market strategy,
    and business viability. Your job is to:

    1. Analyze the product the user describes (name, URL, or free-text description).
    2. Produce a structured critique covering:
       - product_name       (best guess if not explicit)
       - category           (e.g. SaaS, mobile app, hardware, marketplace)
       - target_audience    (who it's for)
       - value_proposition  (what problem it solves)
       - strengths          (pipe-separated bullet list, max 5)
       - weaknesses         (pipe-separated bullet list, max 5)
       - opportunities      (pipe-separated bullet list, max 3)
       - threats            (pipe-separated bullet list, max 3)
       - ux_score           (1–10 with one-line rationale)
       - market_fit_score   (1–10 with one-line rationale)
       - overall_verdict    (one punchy paragraph: would you invest / use it?)

    3. Call the tool `log_critique_to_sheets` to record the structured data.
       Pass every field above as individual named arguments.

    4. Call the tool `send_critique_email` to email the critique.
       Use:
         - to:      {RECIPIENT_EMAIL}
         - subject: "Product Critique: <product_name>"
         - body:    A clean, human-readable version of the full critique.

    Be direct and opinionated. Avoid generic praise. If something is bad, say so.
    After both tools succeed, reply with a short confirmation message.
""").strip()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_env() -> None:
    missing = [v for v in ("ANTHROPIC_API_KEY", "ZAPIER_MCP_URL", "RECIPIENT_EMAIL")
               if not os.environ.get(v)]
    if missing:
        print("ERROR: Missing required environment variables:")
        for v in missing:
            print(f"  {v}")
        print("\nSet them before running, e.g.:")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        print("  export ZAPIER_MCP_URL=https://mcp.zapier.com/...")
        print("  export RECIPIENT_EMAIL=you@example.com")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

def run_critique(product_input: str) -> None:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    print("\nAnalyzing product...\n")

    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": product_input}
        ],
        mcp_servers=[
            {
                "type": "url",
                "url": ZAPIER_MCP_URL,
                "name": "zapier",
            }
        ],
        betas=["mcp-client-2025-04-04"],
    )

    for block in response.content:
        if hasattr(block, "text"):
            print(block.text)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    validate_env()

    print("Product Critic Agent")
    print("=" * 40)
    print("Describe the product to critique (name, URL, or free-text).")
    print("Press Enter twice (blank line) when done.\n")

    lines: list[str] = []
    try:
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
    except EOFError:
        pass  # support piped input

    product_input = "\n".join(lines).strip()

    if not product_input:
        print("No input provided. Exiting.")
        sys.exit(0)

    run_critique(product_input)


if __name__ == "__main__":
    main()
