"""
core/question_gen.py — Interview Question Generator
"""
from __future__ import annotations

import json
import logging
import re

from core.schemas import Question
from core.llm import chat

logger = logging.getLogger(__name__)

CATEGORIES = ["Technical", "Behavioral", "System Design", "Problem Solving", "Domain Knowledge"]


def generate_questions(
    role: str,
    difficulty: str = "medium",
    count: int = 5,
    categories: list[str] = None,
    resume_context: str = "",
) -> list[Question]:
    """
    Generate interview questions using LLM. Falls back to static questions if LLM unavailable.
    Returns list of Question objects.
    """
    cats = categories or CATEGORIES[:3]
    prompt = f"""Generate {count} interview questions for a {role} role at {difficulty} difficulty.
Categories to cover: {', '.join(cats)}.
{"Resume context: " + resume_context[:500] if resume_context else ""}
Return ONLY a JSON array of objects with keys: category, topic, difficulty, question_text, key_points (list of 3-5 strings).
No markdown, no explanation, just the JSON array."""

    result = chat(prompt)
    if result is None:
        return _fallback_questions(role, difficulty, count, cats)

    try:
        # Strip markdown code fences if present
        clean = re.sub(r"```(?:json)?", "", result).strip().rstrip("```").strip()
        data = json.loads(clean)
        questions = []
        for i, q in enumerate(data[:count], 1):
            questions.append(Question(
                number=i,
                category=q.get("category", "Technical"),
                topic=q.get("topic", "General"),
                difficulty=q.get("difficulty", difficulty),
                question_text=q.get("question_text", ""),
                key_points=q.get("key_points", []),
            ))
        return questions
    except Exception as e:
        logger.warning("Question parse failed: %s", e)
        return _fallback_questions(role, difficulty, count, cats)


def _fallback_questions(role: str, difficulty: str, count: int, categories: list[str]) -> list[Question]:
    base = [
        Question(
            number=1,
            category="Technical",
            topic="Core Concepts",
            difficulty=difficulty,
            question_text=f"Explain the most important technical concepts for a {role}.",
            key_points=["Show depth of understanding", "Use examples", "Mention trade-offs"],
        ),
        Question(
            number=2,
            category="Behavioral",
            topic="Problem Solving",
            difficulty=difficulty,
            question_text="Describe a challenging problem you solved and your approach.",
            key_points=["Use STAR method", "Show impact", "Mention what you learned"],
        ),
        Question(
            number=3,
            category="System Design",
            topic="Architecture",
            difficulty=difficulty,
            question_text=f"Design a simple system relevant to {role} work.",
            key_points=["Consider scalability", "Discuss trade-offs", "Mention data flow"],
        ),
        Question(
            number=4,
            category="Technical",
            topic="Best Practices",
            difficulty=difficulty,
            question_text="What coding or engineering best practices do you follow?",
            key_points=["Code quality", "Testing", "Documentation", "Version control"],
        ),
        Question(
            number=5,
            category="Domain Knowledge",
            topic="Industry Awareness",
            difficulty=difficulty,
            question_text=f"What recent trends in {role} space interest you most?",
            key_points=["Show curiosity", "Mention specific technologies", "Connect to work"],
        ),
    ]
    return base[:count]
