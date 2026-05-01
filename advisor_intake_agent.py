"""
Advisor Intake Agent
--------------------
Paste a plain-text client description at the prompt.
Claude structures the data, then uses Zapier MCP to:
  1. Append a row to Google Sheets  (tool: log_client_to_sheets)
  2. Send an email summary via Gmail (tool: send_client_summary_email)

Required environment variables:
  ANTHROPIC_API_KEY  – Anthropic API key
  ZAPIER_MCP_URL     – MCP endpoint from actions.zapier.com/mcp
  ADVISOR_EMAIL      – Destination address for the summary email
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
ADVISOR_EMAIL     = os.environ.get("ADVISOR_EMAIL", "")

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = textwrap.dedent(f"""
    You are an advisor intake assistant. Your job is to:

    1. Parse the raw client description the user provides.
    2. Extract and structure the following fields (use "unknown" when missing):
       - full_name
       - email
       - phone
       - company
       - industry
       - pain_points       (short bullet list, pipe-separated)
       - goals             (short bullet list, pipe-separated)
       - budget_range
       - timeline
       - source            (how they found us, if mentioned)
       - notes             (anything else relevant)

    3. Call the tool `log_client_to_sheets` to record the structured data.
       Pass every field above as individual named arguments.

    4. Call the tool `send_client_summary_email` to email the advisor.
       Use:
         - to:      {ADVISOR_EMAIL}
         - subject: "New Client Intake: <full_name> – <company>"
         - body:    A clean, human-readable summary of all fields.

    Do not ask follow-up questions. Work with whatever information is provided.
    After both tools succeed, reply with a short confirmation message.
""").strip()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_env() -> None:
    missing = [v for v in ("ANTHROPIC_API_KEY", "ZAPIER_MCP_URL", "ADVISOR_EMAIL")
               if not os.environ.get(v)]
    if missing:
        print("ERROR: Missing required environment variables:")
        for v in missing:
            print(f"  {v}")
        print("\nSet them before running, e.g.:")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        print("  export ZAPIER_MCP_URL=https://mcp.zapier.com/...")
        print("  export ADVISOR_EMAIL=you@example.com")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

def run_intake(client_description: str) -> None:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    print("\nProcessing intake...\n")

    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": client_description}
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

    # Print the final text response from the model
    for block in response.content:
        if hasattr(block, "text"):
            print(block.text)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    validate_env()

    print("Advisor Intake Agent")
    print("=" * 40)
    print("Paste the client description below.")
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

    client_description = "\n".join(lines).strip()

    if not client_description:
        print("No description provided. Exiting.")
        sys.exit(0)

    run_intake(client_description)


if __name__ == "__main__":
    main()
