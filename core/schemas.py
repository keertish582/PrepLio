from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class RuleCheckResult(BaseModel):
    rule_name: str = ""
    passed: bool = False
    score: float = 0.0
    max_score: float = 0.0
    message: str = ""
    section: str = ""


class ParsedResume(BaseModel):
    raw_text: str = ""
    sections: dict[str, str] = Field(default_factory=dict)
    skills: list[str] = Field(default_factory=list)
    contact: dict[str, str] = Field(default_factory=dict)
    file_hash: str = ""
    file_name: str = ""
    file_size_bytes: int = 0


class RuleCheckBundle(BaseModel):
    checks: list[RuleCheckResult] = Field(default_factory=list)
    rule_score: float = 0.0
    max_rule_score: float = 85.0


class SectionFeedback(BaseModel):
    section_name: str = ""
    score: float = 0.0
    max_score: float = 10.0
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    original_bullets: list[str] = Field(default_factory=list)
    suggested_rewrites: list[str] = Field(default_factory=list)
    explanation: str = ""
    ai_generated: bool = True


class PriorityFix(BaseModel):
    severity: str = "medium"
    section: str = ""
    action: str = ""


class ResumeReviewResult(BaseModel):
    parsed: ParsedResume = Field(default_factory=ParsedResume)
    rule_bundle: RuleCheckBundle = Field(default_factory=RuleCheckBundle)
    section_feedback: list[SectionFeedback] = Field(default_factory=list)
    priority_fixes: list[PriorityFix] = Field(default_factory=list)
    ai_score: Optional[float] = None
    ai_assessment_complete: bool = False
    final_score: Optional[float] = None
    summary: str = ""
    target_role: str = ""
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)


class SkillMatch(BaseModel):
    skill: str = ""
    matched: bool = False
    evidence: str = ""
    snippet: str = ""


class GapReport(BaseModel):
    role: str = ""
    must_haves: list[SkillMatch] = Field(default_factory=list)
    good_to_haves: list[SkillMatch] = Field(default_factory=list)
    match_pct: float = 0.0
    roadmap: list[dict[str, Any]] = Field(default_factory=list)
    project_ideas: list[dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class Question(BaseModel):
    number: int = 0
    category: str = ""
    topic: str = ""
    difficulty: str = "medium"
    question_text: str = ""
    key_points: list[str] = Field(default_factory=list)


class InterviewAnswer(BaseModel):
    question_number: int = 0
    question_text: str = ""
    answer_text: str = ""
    correctness: float = 0.0
    clarity: float = 0.0
    depth: float = 0.0
    overall_score: float = 0.0
    covered_points: list[str] = Field(default_factory=list)
    missed_points: list[str] = Field(default_factory=list)
    feedback: str = ""


class InterviewSession(BaseModel):
    role: str = ""
    difficulty: str = "medium"
    mode: str = "coaching"
    questions: list[Question] = Field(default_factory=list)
    answers: list[InterviewAnswer] = Field(default_factory=list)
    avg_score: float = 0.0
    category_scores: dict[str, float] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    weak_topics: list[str] = Field(default_factory=list)
    practice_plan: list[str] = Field(default_factory=list)
    completed: bool = False
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
