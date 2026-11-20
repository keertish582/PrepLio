"""
core/parser.py — B1: PDF/DOCX Parser + Rule Checks
"""
from __future__ import annotations

import re
import logging
from typing import Optional

from core.schemas import RuleCheckResult, ParsedResume

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Action verbs used for bullet quality check
# ---------------------------------------------------------------------------
ACTION_VERBS = {
    "developed", "built", "led", "managed", "designed", "implemented",
    "improved", "created", "analyzed", "architected", "automated",
    "collaborated", "configured", "coordinated", "debugged", "delivered",
    "deployed", "engineered", "established", "executed", "facilitated",
    "generated", "identified", "integrated", "launched", "maintained",
    "mentored", "migrated", "monitored", "optimized", "organized",
    "oversaw", "planned", "produced", "programmed", "reduced", "refactored",
    "researched", "resolved", "reviewed", "scaled", "secured", "shipped",
    "simplified", "streamlined", "supported", "tested", "trained", "wrote",
}

# ---------------------------------------------------------------------------
# Section heading patterns
# ---------------------------------------------------------------------------
SECTION_PATTERNS = {
    "Contact": re.compile(
        r"^(contact|personal\s+info(rmation)?|contact\s+info(rmation)?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "Summary": re.compile(
        r"^(summary|objective|professional\s+summary|career\s+objective|profile)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "Experience": re.compile(
        r"^(experience|work\s+experience|professional\s+experience|employment(\s+history)?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "Education": re.compile(
        r"^(education(al\s+background)?|academic(s|\s+background)?|qualifications?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "Skills": re.compile(
        r"^(skills?|technical\s+skills?|core\s+competencies|competencies|technologies)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "Projects": re.compile(
        r"^(projects?|personal\s+projects?|side\s+projects?|portfolio)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "Certifications": re.compile(
        r"^(certifications?|certificates?|licenses?\s+&\s+certifications?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "Awards": re.compile(
        r"^(awards?|honors?|achievements?|recognitions?|accomplishments?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
}


# ---------------------------------------------------------------------------
# File extraction
# ---------------------------------------------------------------------------

def extract_text(file_bytes: bytes, filename: str) -> tuple[str, str]:
    """
    Extract text from PDF or DOCX bytes.

    Returns:
        (text, error_msg) — on success error_msg is ""; on failure text is "".
    """
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext == "pdf":
        return _extract_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        return _extract_docx(file_bytes)
    else:
        return "", f"Unsupported file type: .{ext}. Please upload a PDF or DOCX."


def _extract_pdf(file_bytes: bytes) -> tuple[str, str]:
    try:
        import io
        import pdfplumber

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = []
            for page in pdf.pages:
                txt = page.extract_text()
                if txt:
                    pages.append(txt)
            full_text = "\n".join(pages).strip()

        if not full_text:
            return "", "PDF appears to be empty or image-based (no extractable text)."
        return full_text, ""
    except Exception as exc:
        logger.warning("pdfplumber failed: %s", exc)
        # Fallback to pypdf
        try:
            import io
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(file_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
            full_text = "\n".join(pages).strip()
            if not full_text:
                return "", "PDF appears to be empty or image-based (no extractable text)."
            return full_text, ""
        except Exception as exc2:
            return "", f"Failed to read PDF: {exc2}"


def _extract_docx(file_bytes: bytes) -> tuple[str, str]:
    try:
        import io
        from docx import Document

        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n".join(paragraphs).strip()
        if not full_text:
            return "", "DOCX appears to be empty."
        return full_text, ""
    except Exception as exc:
        return "", f"Failed to read DOCX: {exc}"


# ---------------------------------------------------------------------------
# Section splitter
# ---------------------------------------------------------------------------

def split_sections(text: str) -> dict[str, str]:
    """
    Detect standard resume sections by scanning heading lines.
    Returns dict mapping canonical section_name -> content string.
    """
    if not text:
        return {}

    lines = text.splitlines()
    # Build list of (line_index, section_name) for heading matches
    heading_positions: list[tuple[int, str]] = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        # Check known section patterns
        matched = False
        for section_name, pattern in SECTION_PATTERNS.items():
            if pattern.match(stripped):
                heading_positions.append((i, section_name))
                matched = True
                break

        if not matched:
            # Heuristic: ALL CAPS line (≤ 5 words, > 3 chars, e.g. WORK HISTORY, PUBLICATIONS)
            words = stripped.split()
            if 1 <= len(words) <= 5 and stripped.isupper() and len(stripped) > 3:
                heading_positions.append((i, stripped.title()))

    if not heading_positions:
        return {"Full Text": text}

    sections: dict[str, str] = {}
    for idx, (line_idx, section_name) in enumerate(heading_positions):
        start = line_idx + 1
        end = heading_positions[idx + 1][0] if idx + 1 < len(heading_positions) else len(lines)
        content = "\n".join(lines[start:end]).strip()
        # Merge duplicate section names
        if section_name in sections:
            sections[section_name] += "\n" + content
        else:
            sections[section_name] = content

    return sections


# ---------------------------------------------------------------------------
# Resume entity extractor
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(
    r"(\+?\d[\d\s\-().]{7,}\d)"
)


def extract_resume(text: str) -> ParsedResume:
    """
    Parse contact info (email/phone), extract skills from Skills section.
    Returns ParsedResume populated with what could be found.
    """
    sections = split_sections(text)

    # --- Contact extraction ---
    contact: dict[str, str] = {}
    email_match = _EMAIL_RE.search(text)
    if email_match:
        contact["email"] = email_match.group()

    # Look in first 20 lines for phone
    header_text = "\n".join(text.splitlines()[:20])
    phone_match = _PHONE_RE.search(header_text)
    if phone_match:
        raw_phone = phone_match.group().strip()
        # Basic sanity: at least 7 digits
        digits = re.sub(r"\D", "", raw_phone)
        if len(digits) >= 7:
            contact["phone"] = raw_phone

    # --- Skills extraction ---
    skills: list[str] = []
    skill_section_text = ""
    for key, val in sections.items():
        if "skill" in key.lower() or "technolog" in key.lower() or "competenc" in key.lower():
            skill_section_text = val
            break

    if skill_section_text:
        # Split by comma, newline, pipe, semicolon, bullet
        raw_skills = re.split(r"[,\n|;•·\-–]", skill_section_text)
        skills = [s.strip() for s in raw_skills if 1 < len(s.strip()) < 60]

    return ParsedResume(
        raw_text=text,
        sections=sections,
        skills=skills,
        contact=contact,
    )


# ---------------------------------------------------------------------------
# Rule checks
# ---------------------------------------------------------------------------

def rule_checks(parsed_resume: ParsedResume) -> list[RuleCheckResult]:
    """
    Run deterministic rule checks on a ParsedResume.
    Returns list of RuleCheckResult.
    """
    text = parsed_resume.raw_text
    sections = parsed_resume.sections
    results: list[RuleCheckResult] = []

    def _sections_containing(*keywords: str) -> str:
        """Return concatenated content of sections whose name contains any keyword."""
        combined = []
        for name, content in sections.items():
            if any(kw in name.lower() for kw in keywords):
                combined.append(content)
        return "\n".join(combined)

    # 1. has_contact_info (10 pts)
    has_email = bool(_EMAIL_RE.search(text))
    has_phone = bool(_PHONE_RE.search("\n".join(text.splitlines()[:30])))
    contact_pass = has_email or has_phone
    results.append(RuleCheckResult(
        rule_name="has_contact_info",
        passed=contact_pass,
        score=10.0 if contact_pass else 0.0,
        max_score=10.0,
        message="Email or phone found." if contact_pass else "No email or phone number detected.",
        section="Contact",
    ))

    # 2. has_summary (5 pts)
    summary_text = _sections_containing("summary", "objective", "profile")
    has_summary = bool(summary_text.strip())
    results.append(RuleCheckResult(
        rule_name="has_summary",
        passed=has_summary,
        score=5.0 if has_summary else 0.0,
        max_score=5.0,
        message="Summary/Objective section found." if has_summary else "No summary or objective section found.",
        section="Summary",
    ))

    # 3. has_experience (15 pts)
    exp_text = _sections_containing("experience", "employment", "work")
    has_exp = bool(exp_text.strip())
    results.append(RuleCheckResult(
        rule_name="has_experience",
        passed=has_exp,
        score=15.0 if has_exp else 0.0,
        max_score=15.0,
        message="Experience section found." if has_exp else "No work experience section found.",
        section="Experience",
    ))

    # 4. has_education (15 pts)
    edu_text = _sections_containing("education", "academic", "qualification")
    has_edu = bool(edu_text.strip())
    results.append(RuleCheckResult(
        rule_name="has_education",
        passed=has_edu,
        score=15.0 if has_edu else 0.0,
        max_score=15.0,
        message="Education section found." if has_edu else "No education section found.",
        section="Education",
    ))

    # 5. has_skills (10 pts)
    skills_text = _sections_containing("skill", "technolog", "competenc")
    has_skills = bool(skills_text.strip())
    results.append(RuleCheckResult(
        rule_name="has_skills",
        passed=has_skills,
        score=10.0 if has_skills else 0.0,
        max_score=10.0,
        message="Skills section found." if has_skills else "No skills section found.",
        section="Skills",
    ))

    # 6. bullet_action_verbs (10 pts)
    exp_lines = exp_text.splitlines() if exp_text else []
    bullet_lines = [
        l.strip().lstrip("•·-–▪▸▹◦○●")
        for l in exp_lines
        if l.strip().startswith(("•", "·", "-", "–", "▪", "▸", "▹", "◦", "○", "●"))
        or (l.strip() and l.strip()[0].isupper() and len(l.strip()) > 20)
    ]
    action_verb_hits = 0
    for bullet in bullet_lines:
        first_word = bullet.strip().split()[0].lower().rstrip(".,;") if bullet.strip() else ""
        if first_word in ACTION_VERBS:
            action_verb_hits += 1

    verb_ratio = action_verb_hits / max(len(bullet_lines), 1)
    verb_pass = verb_ratio >= 0.4 or action_verb_hits >= 3
    results.append(RuleCheckResult(
        rule_name="bullet_action_verbs",
        passed=verb_pass,
        score=10.0 if verb_pass else round(10.0 * verb_ratio, 1),
        max_score=10.0,
        message=(
            f"{action_verb_hits} bullets start with action verbs."
            if verb_pass
            else f"Only {action_verb_hits} bullets start with action verbs. Use strong action verbs."
        ),
        section="Experience",
    ))

    # 7. quantified_achievements (10 pts)
    quant_re = re.compile(r"\d+\s*(%|percent|x|k\b|\+|million|billion|users|customers|ms\b|seconds?|hours?|days?|weeks?|months?|years?)")
    quant_hits = sum(1 for l in (exp_text + "\n" + _sections_containing("project")).splitlines() if quant_re.search(l.lower()))
    quant_pass = quant_hits >= 3
    results.append(RuleCheckResult(
        rule_name="quantified_achievements",
        passed=quant_pass,
        score=10.0 if quant_hits >= 3 else round(min(10.0, quant_hits * 3.33), 1),
        max_score=10.0,
        message=(
            f"{quant_hits} quantified achievements found."
            if quant_pass
            else f"Only {quant_hits} quantified achievements. Add numbers and metrics."
        ),
        section="Experience",
    ))

    # 8. no_personal_pronouns (5 pts)
    pronoun_re = re.compile(r"\b(I|my|me)\b", re.IGNORECASE)
    pronoun_matches = pronoun_re.findall(text)
    no_pronouns = len(pronoun_matches) == 0
    results.append(RuleCheckResult(
        rule_name="no_personal_pronouns",
        passed=no_pronouns,
        score=5.0 if no_pronouns else 0.0,
        max_score=5.0,
        message="No personal pronouns found." if no_pronouns else f"Found {len(pronoun_matches)} personal pronoun(s). Remove 'I', 'my', 'me'.",
        section="General",
    ))

    # 9. reasonable_length (5 pts)
    word_count = len(text.split())
    length_pass = 300 <= word_count <= 1200
    results.append(RuleCheckResult(
        rule_name="reasonable_length",
        passed=length_pass,
        score=5.0 if length_pass else 0.0,
        max_score=5.0,
        message=f"Resume has {word_count} words (ideal: 300-1200)." if length_pass
                else f"Resume has {word_count} words. {'Too short — add more detail.' if word_count < 300 else 'Too long — aim for under 1200 words.'}",
        section="General",
    ))

    return results


def rule_score(checks: list[RuleCheckResult]) -> float:
    """Return total score from rule checks."""
    return round(sum(c.score for c in checks), 1)


def rule_score_breakdown(checks: list[RuleCheckResult]) -> dict[str, float]:
    """Return {rule_name: score} mapping."""
    return {c.rule_name: c.score for c in checks}
