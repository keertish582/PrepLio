"""
core/reflection.py — Deep Resume Review via LLM
"""
from __future__ import annotations

import logging

from core.llm import chat
from core.schemas import ResumeReviewResult

logger = logging.getLogger(__name__)


def deep_review(result: ResumeReviewResult) -> str:
    """
    Run an additional deep-review pass using the LLM.
    Returns a narrative string, or empty string on failure.
    """
    if not result.summary:
        return ""

    prompt = f"""You are a senior recruiter reviewing a resume for the role of {result.target_role}.
Resume summary: {result.summary}
Rule score: {result.rule_bundle.rule_score}/{result.rule_bundle.max_rule_score}
Sections reviewed: {len(result.section_feedback)}

Provide a 3-paragraph deep analysis:
1. Overall assessment and positioning
2. Top 3 specific improvements with concrete examples
3. Competitive positioning advice for {result.target_role} roles

Be specific, constructive, and actionable. No generic advice."""

    text = chat(prompt)
    return text or ""
