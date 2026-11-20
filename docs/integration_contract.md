# PrepLio — Backend Integration Contract

## Overview
This document specifies the integration boundaries and contracts between the Streamlit UI (Teammate B) and the core backend modules.

---

## 1. Preserved Signatures & Non-Negotiable Contracts

### `core/db.py`
The interview session persistence signature is strictly preserved:
```python
db.save_session(
    role: str,
    difficulty: str,
    avg: float,
    report_dict: dict,
    answers: list,
    user_id: int = 1,
    origin: str = "live"
) -> int
```

Additional database contracts:
```python
db.init_db() -> None
db.save_resume_review(*args, **kwargs) -> int
db.save_gap_report(*args, **kwargs) -> int
db.score_history(user_id: int = 1, role: Optional[str] = None, limit: int = 50) -> list[dict]
db.ats_history(user_id: int = 1, role: Optional[str] = None, limit: int = 50) -> list[dict]
db.weak_topic_counts(user_id: int = 1, limit: int = 20) -> dict[str, int]
db.get_latest_review(user_id: int = 1) -> dict | None
db.delete_all_data(user_id: int = 1) -> None
```

---

## 2. Parser & Rule Check Contracts (`core/parser.py`)

```python
extract_text(file_bytes: bytes, filename: str) -> tuple[str, str]
# Returns (extracted_text, error_message). On failure, text is "" and error_message is populated. Never raises.

split_sections(text: str) -> dict[str, str]
# Detects: Contact, Summary, Experience, Education, Skills, Projects, Certifications.

extract_resume(text: str) -> ParsedResume
# Extracts contact (email, phone), skills, and sections.

rule_checks(parsed: ParsedResume) -> list[RuleCheckResult]
# 9 deterministic rules evaluated up to 85.0 points total.

rule_score(checks: list[RuleCheckResult]) -> float
# Sum of check scores.
```

---

## 3. Role Knowledge & Skill Gap Matching (`core/skill_gap.py`)

```python
load_roles() -> dict[str, dict]
# Loads all role JSON definitions from data/roles/*.json. Cached via lru_cache.

compute_gap(resume_skills: list[str], role_name: str, jd_skills: dict | None = None) -> GapReport
# Uses RapidFuzz token_sort_ratio (threshold 80) and alias mapping.
# Weighted score: (matched_must_haves * 2 + matched_good_to_haves) / (total_must_haves * 2 + total_good_to_haves) * 100.

build_roadmap(gap: GapReport) -> list[dict]
# 4-week structured learning curriculum for missing skills.

build_project_ideas(gap: GapReport) -> list[dict]
# 3 hands-on portfolio projects with deliverables.
```

---

## 4. Teammate-Owned Contracts

### `core/llm.py`
```python
check_ollama() -> dict
# Returns {"available": bool, "model_ready": bool, "message": str}

chat(prompt: str, system: str = "", model: str = None) -> Optional[str]
# Single-turn chat with local Ollama. Returns None on failure or offline.
```

### `core/question_gen.py`
```python
generate_questions(
    role: str,
    difficulty: str = "medium",
    count: int = 5,
    categories: list[str] = None,
    resume_context: str = ""
) -> list[Question]
```

### `core/interview.py`
```python
evaluate_answer(question: Question, answer_text: str) -> InterviewAnswer
# Evaluates correctness (50%), clarity (25%), depth (25%). Returns InterviewAnswer.

build_interview_summary(session: InterviewSession) -> dict
# Returns summary with avg_score, category_scores, weak_topics, practice_plan.
```

### `core/reflection.py`
```python
deep_review(result: ResumeReviewResult) -> str
# Performs 3-paragraph executive recruiter deep analysis pass.
```

---

## 5. Report Generators (`core/report.py`)

```python
build_report_pdf(**kwargs) -> bytes
# Generates styled A4 PDF document using ReportLab. Dynamic text is escaped with _safe().

build_report_json(**kwargs) -> bytes
# Generates UTF-8 encoded JSON export conforming to schema v1.0.
```
