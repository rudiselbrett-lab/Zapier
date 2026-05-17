"""
Dry-run stubs — replace real agent calls with canned data.
Exercises the full orchestration → synthesis → formatting pipeline
without touching the Anthropic API.
"""
from __future__ import annotations

from state import OrchestratorState, ResearchItem


def content_items() -> list[ResearchItem]:
    return [
        ResearchItem(
            title="How JPMorgan Is Using LLMs to Summarise Earnings Calls",
            url="https://www.americanbanker.com/jpmorgan-llm-earnings-calls",
            source="American Banker",
            summary="JPMorgan's AI team deployed an internal LLM pipeline that condenses quarterly earnings transcripts into one-page briefs for analysts. The system runs on proprietary data and is not customer-facing.",
            why_it_matters="Shows how top-tier banks are applying LLMs to internal knowledge work — a pattern any mid-size bank can replicate.",
            category="content",
            relevance_score=9,
        ),
        ResearchItem(
            title="AI in Fraud Detection: What's Working in 2026",
            url="https://thefinancialbrand.com/ai-fraud-detection-2026",
            source="The Financial Brand",
            summary="A survey of 120 retail banks found that real-time ML fraud scoring reduced false-positive rates by 34% compared to rule-based systems. Graph neural networks were the top emerging technique.",
            why_it_matters="Concrete performance data gives product teams ammunition for AI investment cases.",
            category="content",
            relevance_score=8,
        ),
        ResearchItem(
            title="Building Production RAG for Compliance Teams (YouTube)",
            url="https://www.youtube.com/watch?v=rag-compliance-demo",
            source="YouTube — FinTech Builders",
            summary="45-minute walkthrough of a RAG system built for a compliance team, covering chunking strategy, metadata filtering, and hallucination guardrails in a regulated context.",
            why_it_matters="Practical build guidance specifically for the constraints banking compliance teams face.",
            category="content",
            relevance_score=8,
        ),
        ResearchItem(
            title="The Case Against AI Chatbots in Branch Banking",
            url="https://finextra.com/blogposting/ai-chatbots-branch",
            source="Finextra",
            summary="Opinion piece arguing that AI chatbots in branch settings create friction for older demographics and erode relationship-banking differentiation.",
            why_it_matters="Counter-narrative worth knowing — useful for product teams scoping chatbot deployments.",
            category="content",
            relevance_score=6,
        ),
    ]


def competitor_items() -> list[ResearchItem]:
    return [
        ResearchItem(
            title="JPMorgan Launches IndexGPT 2.0 for Wealth Clients",
            url="https://www.jpmorgan.com/insights/technology/indexgpt-2",
            source="JPMorgan Tech Blog",
            summary="JPMorgan expanded IndexGPT from an internal tool to a client-facing portfolio analysis assistant available to Chase Private Client customers. The model is fine-tuned on proprietary market data.",
            why_it_matters="First major US bank to put a branded LLM product directly in client hands at scale.",
            category="competitor",
            institution="JPMorgan",
            relevance_score=9,
        ),
        ResearchItem(
            title="Capital One Open-Sources Slingshot ML Platform",
            url="https://github.com/capitalone/slingshot",
            source="Capital One GitHub",
            summary="Capital One released Slingshot, their internal ML feature-store and model-serving platform, under Apache 2.0. The repo includes tooling for model drift detection and A/B testing.",
            why_it_matters="Rare instance of a bank open-sourcing core ML infrastructure — signals confidence in their technical lead.",
            category="competitor",
            institution="Capital One",
            relevance_score=8,
        ),
        ResearchItem(
            title="Goldman Sachs Partners with Anthropic for Internal AI Tooling",
            url="https://www.goldmansachs.com/intelligence/pages/anthropic-partnership.html",
            source="Goldman Sachs",
            summary="Goldman announced an enterprise agreement with Anthropic to deploy Claude across investment banking and legal teams for document review and deal memo drafting.",
            why_it_matters="Confirms Anthropic's traction in bulge-bracket IB — watch for similar moves at other tier-1 banks.",
            category="competitor",
            institution="Goldman Sachs",
            relevance_score=8,
        ),
        ResearchItem(
            title="Bank of America Erica Crosses 2 Billion Interactions",
            url="https://newsroom.bankofamerica.com/erica-2-billion",
            source="Bank of America Newsroom",
            summary="BofA reported that its AI assistant Erica surpassed 2 billion client interactions, with 42% of interactions now involving proactive financial guidance rather than reactive support.",
            why_it_matters="Erica's scale makes it the best public benchmark for conversational AI ROI in retail banking.",
            category="competitor",
            institution="Bank of America",
            relevance_score=7,
        ),
        ResearchItem(
            title="Wells Fargo Pilots AI Underwriting Co-Pilot for Mortgage Teams",
            url="https://newsroom.wellsfargo.com/ai-mortgage-underwriting",
            source="Wells Fargo Newsroom",
            summary="Wells Fargo is testing an AI co-pilot that surfaces relevant guidelines and flags documentation gaps during the mortgage underwriting review, reducing average review time by 22%.",
            why_it_matters="Early signal that underwriting AI is moving from back-office to underwriter-facing workflow tools.",
            category="competitor",
            institution="Wells Fargo",
            relevance_score=7,
        ),
    ]


def technical_items() -> list[ResearchItem]:
    return [
        ResearchItem(
            title="Claude Opus 4.7 — Extended Context and Tool Use Improvements",
            url="https://www.anthropic.com/news/claude-opus-4-7",
            source="Anthropic",
            summary="Anthropic released Claude Opus 4.7 with a 500K token context window and improved reliability on multi-step tool-use chains. Benchmarks show 18% gains on financial document Q&A tasks.",
            why_it_matters="Larger context directly unlocks long-form regulatory document analysis and end-to-end loan file review.",
            category="technical",
            relevance_score=9,
        ),
        ResearchItem(
            title="FinBERT v3: Domain-Adapted Embeddings for Financial Text",
            url="https://huggingface.co/ProsusAI/finbert-v3",
            source="Hugging Face",
            summary="Updated FinBERT model trained on 10-K filings, earnings transcripts, and regulatory documents. Outperforms general embeddings on financial sentiment and entity extraction tasks by 11%.",
            why_it_matters="Drop-in upgrade for any bank running RAG or classification pipelines on financial text.",
            category="technical",
            relevance_score=8,
        ),
        ResearchItem(
            title="LangGraph 0.4 — Stateful Agent Workflows with Checkpointing",
            url="https://github.com/langchain-ai/langgraph/releases/tag/0.4.0",
            source="GitHub — LangChain",
            summary="LangGraph 0.4 adds native checkpointing, human-in-the-loop pause points, and a visual debugger. Designed for long-running agentic workflows that need auditability.",
            why_it_matters="Checkpointing and audit trails are table-stakes for regulated use cases — this closes a gap in the open-source agent stack.",
            category="technical",
            relevance_score=8,
        ),
        ResearchItem(
            title="arXiv: Detecting Hallucinations in Financial LLM Outputs",
            url="https://arxiv.org/abs/2405.12345",
            source="arXiv",
            summary="Researchers propose a lightweight verifier model trained on financial fact pairs that flags unsupported claims in LLM-generated summaries with 91% precision at <50ms latency.",
            why_it_matters="Hallucination detection at inference time is the missing piece for deploying LLMs in compliance-sensitive banking workflows.",
            category="technical",
            relevance_score=9,
        ),
    ]


def build_mock_state(intent: str) -> OrchestratorState:
    state = OrchestratorState(
        intent=intent,
        research_plan={
            "topic": intent,
            "date_range": "last 30 days",
            "content_focus": "articles and videos on banking AI adoption",
            "competitor_focus": "AI product launches and technical investments",
            "technical_focus": "new models, frameworks, and research papers",
        },
    )
    state.content_output = content_items()
    state.competitor_output = competitor_items()
    state.technical_output = technical_items()
    return state


def build_mock_report(state: OrchestratorState) -> dict:
    """Synthesise mock state into the final report structure without calling the API."""

    def _d(item: ResearchItem) -> dict:
        return {
            "title": item.title,
            "url": item.url,
            "source": item.source,
            "summary": item.summary,
            "why_it_matters": item.why_it_matters,
            "category": item.category,
            "institution": item.institution,
            "relevance_score": item.relevance_score,
        }

    all_items = (
        state.content_output + state.competitor_output + state.technical_output
    )
    top_picks = sorted(
        [i for i in all_items if (i.relevance_score or 0) >= 9],
        key=lambda i: i.relevance_score or 0,
        reverse=True,
    )[:5]

    competitor_moves: dict[str, list] = {
        k: [] for k in ["JPMorgan", "Capital One", "Goldman Sachs", "Bank of America", "Wells Fargo"]
    }
    for item in state.competitor_output:
        if item.institution in competitor_moves:
            competitor_moves[item.institution].append(_d(item))

    articles = [_d(i) for i in state.content_output if "YouTube" not in i.source]
    videos = [_d(i) for i in state.content_output if "YouTube" in i.source]

    return {
        "top_picks": [_d(i) for i in top_picks],
        "competitor_moves": competitor_moves,
        "content_worth_your_time": {"articles": articles, "videos": videos},
        "technical_radar": {
            "models_and_capabilities": [_d(i) for i in state.technical_output if "Claude" in i.title or "FinBERT" in i.title],
            "frameworks_and_tooling": [_d(i) for i in state.technical_output if "LangGraph" in i.title],
            "research_papers": [_d(i) for i in state.technical_output if "arXiv" in i.source],
        },
        "all_sources": [{"title": i.title, "url": i.url} for i in all_items],
    }
