"""Adapters — normalize backend data for UI without touching teammate contracts."""
from __future__ import annotations
import logging, importlib, traceback
from typing import Optional, Any
from core.schemas import ResumeReviewResult, GapReport, Question, InterviewAnswer, InterviewSession

logger = logging.getLogger(__name__)

def _try_import(module_path: str):
    try:
        return importlib.import_module(module_path)
    except ImportError as e:
        logger.warning("Module %s not available: %s", module_path, e)
        return None

# ── Ollama status ─────────────────────────────────────────────────────────────
def get_ollama_status() -> dict:
    llm = _try_import("core.llm")
    if llm is None:
        return {"available": False, "model_ready": False, "message": "core.llm module not found"}
    try:
        return llm.check_ollama()
    except Exception as e:
        return {"available": False, "model_ready": False, "message": f"Check failed: {e}"}

# ── Document parsing ──────────────────────────────────────────────────────────
def parse_document(file_bytes: bytes, filename: str) -> tuple[Optional[Any], str]:
    """Returns (ParsedResume | None, error_msg)."""
    parser = _try_import("core.parser")
    if parser is None:
        return None, "core.parser module unavailable"
    try:
        text, err = parser.extract_text(file_bytes, filename)
        if err:
            return None, err
        if len(text.strip()) < 100:
            return None, f"Extracted text is too short ({len(text.strip())} chars). Check if document has selectable text."
        parsed = parser.extract_resume(text)
        parsed.file_name = filename
        parsed.file_size_bytes = len(file_bytes)
        return parsed, ""
    except Exception as e:
        logger.error("parse_document failed: %s", traceback.format_exc()[-500:])
        return None, f"Document parsing failed: {type(e).__name__}"

def run_rule_checks(parsed) -> Optional[Any]:
    """Returns RuleCheckBundle or None."""
    parser = _try_import("core.parser")
    if parser is None:
        return None
    try:
        checks = parser.rule_checks(parsed)
        from core.schemas import RuleCheckBundle
        score = parser.rule_score(checks)
        return RuleCheckBundle(checks=checks, rule_score=score)
    except Exception as e:
        logger.error("rule_checks failed: %s", e)
        return None

# ── Review pipeline ───────────────────────────────────────────────────────────
def review_resume_live(parsed, role: str, deep: bool = False) -> tuple[Optional[ResumeReviewResult], str]:
    """Returns (ResumeReviewResult | None, error_msg)."""
    # Rule checks always run
    rule_bundle = run_rule_checks(parsed)
    
    # Try AI review
    ai_sections = []
    ai_score = None
    ai_complete = False
    llm = _try_import("core.llm")
    
    if llm:
        try:
            status = llm.check_ollama()
            if status.get("model_ready"):
                from core.schemas import SectionFeedback, PriorityFix
                # Build section feedback via LLM
                for sec_name, sec_text in parsed.sections.items():
                    if not sec_text.strip():
                        continue
                    prompt = f"""Review this {sec_name} section from a resume targeting {role} role.
Text: {sec_text[:600]}
Return JSON with: score (0-10), strengths (list), weaknesses (list), explanation (string), suggested_rewrites (list)"""
                    result_text = llm.chat(prompt)
                    if result_text:
                        import json, re
                        try:
                            clean = re.sub(r"```(?:json)?","",result_text).strip().rstrip("```").strip()
                            data = json.loads(clean)
                            ai_sections.append(SectionFeedback(
                                section_name=sec_name,
                                score=float(data.get("score",5)),
                                strengths=data.get("strengths",[]),
                                weaknesses=data.get("weaknesses",[]),
                                explanation=data.get("explanation",""),
                                suggested_rewrites=data.get("suggested_rewrites",[]),
                                ai_generated=True
                            ))
                        except Exception:
                            pass
                
                if ai_sections:
                    ai_score = sum(s.score for s in ai_sections) / len(ai_sections) * 1.5  # scale to 15
                    ai_complete = True
        except Exception as e:
            logger.warning("AI review failed: %s", e)

    from core.schemas import ResumeReviewResult, PriorityFix, RuleCheckBundle
    rb = rule_bundle or RuleCheckBundle()
    
    # Build priority fixes from failed checks
    fixes = []
    for chk in rb.checks:
        if not chk.passed and len(fixes) < 6:
            severity = "high" if chk.max_score >= 10 else "medium"
            fixes.append(PriorityFix(severity=severity, section=chk.section, action=chk.message))
    
    final = None
    if ai_complete and ai_score is not None:
        final = round(min(100, rb.rule_score + ai_score), 0)
    
    result = ResumeReviewResult(
        parsed=parsed,
        rule_bundle=rb,
        section_feedback=ai_sections,
        priority_fixes=fixes,
        ai_score=ai_score,
        ai_assessment_complete=ai_complete,
        final_score=final,
        summary=f"Rule score: {rb.rule_score:.0f}/85. {'AI review complete.' if ai_complete else 'AI review unavailable.'}",
        target_role=role,
    )
    
    if deep:
        refl = _try_import("core.reflection")
        if refl:
            try:
                extra = refl.deep_review(result)
                if extra:
                    result.summary = result.summary + "\n\n**Deep Review:**\n" + extra
            except Exception:
                pass
    
    return result, ""

# ── Skill gap ─────────────────────────────────────────────────────────────────
def compute_gap(resume_skills: list, role: str, jd_text: str = "") -> tuple[Optional[GapReport], str]:
    sg = _try_import("core.skill_gap")
    if sg is None:
        return None, "core.skill_gap module unavailable"
    try:
        jd_skills = None
        if jd_text.strip():
            jd_skills = sg.extract_jd_skills(jd_text)
        gap = sg.compute_gap(resume_skills, role, jd_skills)
        gap.roadmap = sg.build_roadmap(gap)
        gap.project_ideas = sg.build_project_ideas(gap)
        return gap, ""
    except Exception as e:
        logger.error("compute_gap failed: %s", traceback.format_exc()[-500:])
        return None, f"Gap analysis failed: {type(e).__name__}"

# ── Questions ─────────────────────────────────────────────────────────────────
def generate_questions(role: str, difficulty: str, count: int,
                       categories: list, resume_ctx: str = "") -> tuple[list, str]:
    qg = _try_import("core.question_gen")
    if qg is None:
        return [], "core.question_gen module unavailable"
    try:
        qs = qg.generate_questions(role=role, difficulty=difficulty, count=count,
                                   categories=categories, resume_context=resume_ctx)
        return qs, ""
    except Exception as e:
        logger.error("generate_questions failed: %s", e)
        return [], f"Question generation failed: {type(e).__name__}"

# ── Interview ─────────────────────────────────────────────────────────────────
def evaluate_answer(question, answer_text: str) -> tuple[Optional[InterviewAnswer], str]:
    iv = _try_import("core.interview")
    if iv is None:
        return None, "core.interview module unavailable"
    try:
        result = iv.evaluate_answer(question, answer_text)
        return result, ""
    except Exception as e:
        logger.error("evaluate_answer failed: %s", e)
        return None, f"Evaluation failed: {type(e).__name__}"

def build_interview_summary(session: InterviewSession) -> dict:
    iv = _try_import("core.interview")
    if iv is None:
        return {}
    try:
        return iv.build_interview_summary(session)
    except Exception as e:
        logger.error("build_interview_summary failed: %s", e)
        return {}

# ── Persistence ───────────────────────────────────────────────────────────────
def save_review(result: ResumeReviewResult, origin: str = "live"):
    try:
        from core.db import init_db, save_resume_review
        init_db()
        save_resume_review(result, origin=origin)
    except Exception as e:
        logger.error("save_review failed: %s", e)

def save_gap(gap: GapReport, origin: str = "live"):
    try:
        from core.db import init_db, save_gap_report
        init_db()
        save_gap_report(gap, origin=origin)
    except Exception as e:
        logger.error("save_gap failed: %s", e)

def save_interview(session: InterviewSession, summary: dict, origin: str = "live"):
    try:
        from core.db import init_db, save_session
        init_db()
        save_session(session.role, session.difficulty, session.avg_score,
                     summary, [a.model_dump() for a in session.answers],
                     user_id=1, origin=origin)
    except Exception as e:
        logger.error("save_interview failed: %s", e)
