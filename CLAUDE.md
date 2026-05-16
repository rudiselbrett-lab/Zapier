# Zapier Advisor Intake Agent

## What this project does

CLI tool that takes a plain-text client description, uses Claude (via the Anthropic API) to structure it into named fields, then fires two Zapier MCP tools:
1. **`log_client_to_sheets`** — appends a row to Google Sheets
2. **`send_client_summary_email`** — emails a formatted summary to the advisor

## Required environment variables

| Variable | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com/settings/api-keys |
| `ZAPIER_MCP_URL` | https://actions.zapier.com/mcp → copy your MCP endpoint |
| `ADVISOR_EMAIL` | The email address that receives intake summaries |

Copy `.env.example` → `.env`, fill in the values, then `source .env`.

## Running the agent

```bash
source .env
python advisor_intake_agent.py
```

Paste the client description at the prompt, then press **Enter twice** (blank line) to submit.  
Piped input is also supported: `cat intake.txt | python advisor_intake_agent.py`

## Architecture

```
advisor_intake_agent.py
  └── anthropic.Anthropic.beta.messages.create()
        ├── model: claude-sonnet-4-6
        ├── mcp_servers: [{ type: "url", url: ZAPIER_MCP_URL }]
        └── betas: ["mcp-client-2025-04-04"]
```

The agent runs a single agentic turn. Claude parses the description, calls both Zapier tools in sequence, and returns a short confirmation. No multi-turn loop is needed.

## Key fields extracted

`full_name`, `email`, `phone`, `company`, `industry`, `pain_points`, `goals`, `budget_range`, `timeline`, `source`, `notes`

Missing fields default to `"unknown"`.

## Recommendations (see email for detail)

- Add `requirements.txt` (`anthropic>=0.50`)
- Add `.gitignore` to exclude `.env`
- Add basic error handling around the MCP call
- Consider a retry wrapper for transient API failures
