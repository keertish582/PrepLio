"""
core/interview.py — Interview Answer Evaluator and Session Summarizer
"""
from __future__ import annotations

import json
import logging
import re

from core.schemas import Question, InterviewAnswer, InterviewSession
from core.llm import chat

logger = logging.getLogger(__name__)


def evaluate_answer(question: Question, answer_text: str) -> InterviewAnswer:
    """
    Evaluate a single interview answer using LLM.
    Returns InterviewAnswer. Never raises.
    """
    prompt = f"""Evaluate this interview answer. Be constructive and fair.
Question: {question.question_text}
Expected key points: {', '.join(question.key_points)}
Candidate answer: {answer_text[:800]}

Return ONLY JSON with keys:
correctness (0-10), clarity (0-10), depth (0-10),
covered_points (list of strings from key_points that were addressed),
missed_points (list of key_points not addressed),
feedback (2-3 sentences of constructive feedback)"""

    result = chat(prompt)
    if result is None:
        return _fallback_evaluation(question, answer_text)

    try:
        clean = re.sub(r"```(?:json)?", "", result).strip().rstrip("```").strip()
        data = json.loads(clean)
        correctness = float(data.get("correctness", 5))
        clarity = float(data.get("clarity", 5))
        depth = float(data.get("depth", 5))
        overall = round((correctness * 0.5 + clarity * 0.25 + depth * 0.25), 1)
        return InterviewAnswer(
            question_number=question.number,
            question_text=question.question_text,
            answer_text=answer_text,
            correctness=correctness,
            clarity=clarity,
            depth=depth,
            overall_score=overall,
            covered_points=data.get("covered_points", []),
            missed_points=data.get("missed_points", []),
            feedback=data.get("feedback", ""),
        )
    except Exception as e:
        logger.warning("Answer eval parse failed: %s", e)
        return _fallback_evaluation(question, answer_text)


def _fallback_evaluation(question: Question, answer_text: str) -> InterviewAnswer:
    has_content = len(answer_text.strip()) > 50
    score = 6.0 if has_content else 2.0
    return InterviewAnswer(
        question_number=question.number,
        question_text=question.question_text,
        answer_text=answer_text,
        correctness=score,
        clarity=score,
        depth=score - 1,
        overall_score=score,
        covered_points=[],
        missed_points=question.key_points,
        feedback="AI evaluation unavailable. Answer recorded for your review.",
    )


def build_interview_summary(session: InterviewSession) -> dict:
    """Build final summary dict from completed session."""
    if not session.answers:
        return {}

    avg = sum(a.overall_score for a in session.answers) / len(session.answers)

    cat_scores: dict[str, list] = {}
    for a, q in zip(session.answers, session.questions):
        cat_scores.setdefault(q.category, []).append(a.overall_score)
    cat_avgs = {cat: sum(scores) / len(scores) for cat, scores in cat_scores.items()}

    weak_topics = [
        q.topic for a, q in zip(session.answers, session.questions) if a.overall_score < 6
    ]

    return {
        "avg_score": round(avg, 1),
        "category_scores": cat_avgs,
        "weak_topics": weak_topics,
        "mode": session.mode,
        "strengths": [
            q.topic for a, q in zip(session.answers, session.questions) if a.overall_score >= 8
        ],
        "practice_plan": [f"Review {t}" for t in weak_topics[:5]],
    }
