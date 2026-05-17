"""
Banking AI Intelligence System — entry point.

Usage:
    python main.py
    python main.py "AI in mortgage underwriting"
    python main.py --intent "AI in mortgage underwriting" --output /tmp/report.md
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys

# Ensure local modules resolve before any installed packages
sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")


def _check_env() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Error: ANTHROPIC_API_KEY environment variable is not set.")


async def _run(intent: str, output_path: str | None, dry_run: bool = False) -> None:
    from output import formatter

    if dry_run:
        import mock_agents
        logger.info("[DRY RUN] Building mock state — no API calls made")
        state = mock_agents.build_mock_state(intent)
        logger.info(
            "[DRY RUN] Mock data: %d content, %d competitor, %d technical items",
            len(state.content_output),
            len(state.competitor_output),
            len(state.technical_output),
        )
        logger.info("[DRY RUN] Running mock synthesis...")
        report = mock_agents.build_mock_report(state)
        state.final_output = report
    else:
        import orchestrator
        from synthesis import synthesizer

        # Phase 1-3: Orchestrator + parallel agents
        state = await orchestrator.run(intent)

        # Phase 4: Synthesis
        logger.info("Running synthesis agent...")
        report = synthesizer.run(state)
        state.final_output = report

    # Phase 5: Output
    logger.info("Writing markdown report...")
    out = formatter.write_markdown(report, intent, output_path)
    logger.info("Report written to: %s", out)

    # Print top picks to stdout for quick review
    top = report.get("top_picks", [])
    if top:
        print("\n" + "="*60)
        print("WHAT CAUGHT MY ATTENTION")
        print("="*60)
        for item in top:
            score = item.get("relevance_score", "?")
            print(f"\n[{score}/10] {item['title']}")
            print(f"  {item['url']}")
            print(f"  {item.get('why_it_matters', '')}")
    else:
        print("\nNo top picks surfaced. Check output/report.md for full results.")

    print(f"\nFull report: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Banking AI Intelligence System")
    parser.add_argument(
        "intent",
        nargs="?",
        default="AI adoption and innovation in banking",
        help="Research intent (default: 'AI adoption and innovation in banking')",
    )
    parser.add_argument("--intent", dest="intent_flag", help="Research intent (alternative flag)")
    parser.add_argument("--output", help="Output path for markdown report")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use mock data — no API key required, exercises full pipeline",
    )
    args = parser.parse_args()

    if not args.dry_run:
        _check_env()

    intent = args.intent_flag or args.intent

    logger.info("Starting Banking AI Intelligence run%s", " [DRY RUN]" if args.dry_run else "")
    logger.info("Intent: %s", intent)

    asyncio.run(_run(intent, args.output, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
