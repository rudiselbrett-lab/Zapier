from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ResearchItem:
    title: str
    url: str
    source: str
    summary: str
    why_it_matters: str
    category: str  # content | competitor | technical
    institution: Optional[str] = None
    relevance_score: Optional[int] = None  # 1-10


@dataclass
class OrchestratorState:
    intent: str
    research_plan: dict = field(default_factory=dict)
    content_output: list[ResearchItem] = field(default_factory=list)
    competitor_output: list[ResearchItem] = field(default_factory=list)
    technical_output: list[ResearchItem] = field(default_factory=list)
    final_output: Optional[dict] = None
    errors: list[str] = field(default_factory=list)
