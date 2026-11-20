# PrepLio — Placement Preparation Assistant: Frontend Architecture & Plan

## 1. Application Overview
**PrepLio** is an offline-capable, single-user placement readiness assistant running on local Python with Streamlit, Plotly, and Qwen3:4b (via Ollama).

The application exposes 5 modular functional areas:
1. **Resume Review (B1/B3):** Deterministic rule validation (0–85 pts), LLM section feedback (0–15 pts), bullet rewrites, and priority fixes.
2. **Skill Gap Analysis (B2):** Target benchmark & custom JD matching with weighted scoring, 4-week roadmap, and portfolio project suggestions.
3. **Interview Questions:** Structured question generation by topic/difficulty with resume project context injection.
4. **Mock Interview Simulation:** Interactive text interview in Coaching or Simulation mode with multi-criteria rubric evaluation (Correctness 50%, Clarity 25%, Depth 25%).
5. **Progress & Analytics (B5):** Plotly historical score trajectories, weak topic frequency distributions, and saved evaluations.

---

## 2. Screen Layout & Component Inventory

### Application Shell
- **Page Layout:** Wide layout, system font stack, light palette (`#F6F8FC` background, `#FFFFFF` cards, `#4F46E5` accent).
- **Sidebar:**
  - Target Role selector (`Software Developer`, `Data Scientist`, `Frontend Developer`, `DevOps Engineer`).
  - Operating Mode toggle (`Live Mode` vs `Demo Mode`).
  - Model Name & Ollama Health status pill (`Ready`, `Model not downloaded`, `Ollama Offline`).
  - Deep Review toggle with duration warning.
  - Privacy statement (local processing guarantee).
  - Clear Session & Confirmed Deletion controls.
- **Header & Footer:**
  - Standard subtitle: *"Review your resume, identify skill gaps, and practice with purpose."*
  - Disclaimer footer: *"AI feedback is guidance, not a guarantee of selection."*

### Tab 1: Resume Review (`ui/resume_tab.py`)
- Upload dropzone accepting PDF/DOCX (max 5 MB).
- Sample resume quick-loaders (Strong resume / Needs work) in Demo Mode.
- Extracted text preview expander and editable comma-separated skills.
- Explicit "Review Resume" action button.
- 5-stage progress indicator (Validate → Extract → Rules → AI Review → Results).
- Results layout:
  - Resume Readiness gauge (`ui/analytics.ats_gauge`).
  - Rule breakdown horizontal bar chart (`ui/analytics.rule_breakdown_bar`).
  - Section scores radar chart (`ui/analytics.section_scores_radar`) for 3+ sections.
  - Priority fixes cards with severity badges (🔴 High, 🟡 Medium, 🟢 Low).
  - Section expanders with strengths, weaknesses, original vs suggested rewrites.
  - Export actions: PDF report download, JSON data export, and SQLite persistence.

### Tab 2: Skill Gap Analysis (`ui/gap_tab.py`)
- Candidate skill source: parsed resume skills or manual input.
- Target benchmark selector: standard role curriculum or custom job description.
- Custom JD NLP extractor with editable must-haves and good-to-haves.
- Explicit "Analyze Skill Gap" action button.
- Donut chart (`ui/analytics.match_donut`) displaying weighted match % (Must-have = 2x).
- Evidence pills: 🎯 Exact, 🔄 Alias, ≈ Fuzzy, ✕ Not found.
- 4-week structured roadmap cards (topics, resources, practice tasks, verification deliverables).
- 3 Recommended portfolio project cards.
- JSON export and local SQLite save.

### Tab 3: Questions (`ui/questions_tab.py`)
- Configuration form: Role, Difficulty (`easy`, `medium`, `hard`), Count (3–12), Categories multiselect, Resume context toggle.
- Form submit trigger (`Generate Questions`).
- Expandable question cards with category/topic badges, difficulty tags, and copyable prompt code blocks.
- Practice mode toggle to conceal expected key talking points.

### Tab 4: Mock Interview (`ui/interview_tab.py`)
- Lifecycle State Machine: `idle` → `active` → `submitting` → `completed`.
- Session configuration: Role, Difficulty, Question count, Feedback style (`Coaching` vs `Simulation`).
- Active question card: Question prompt, topic, progress bar.
- Answer submission text area with single-submission lock.
- Coaching card: Immediate score breakdown (Correctness, Clarity, Depth), covered points, missed points.
- Simulation summary: Category scores bar chart (`ui/analytics.category_scores_bar`), strengths, weak topics, practice plan.
- SQLite session save (`save_session`).

### Tab 5: Progress (`ui/progress_tab.py`)
- Live mode: queries local SQLite tables (`resume_reviews`, `gap_reports`, `interview_sessions`).
- Demo mode: renders synthetic milestones with clear demo indication.
- Metrics row: Latest review score, rule subtotal, sections evaluated, role.
- Plotly charts:
  - Resume readiness trend (`ui/analytics.score_trend_line`).
  - Mock interview average score trend (0–10 scale).
  - Weak topics frequency distribution (`ui/analytics.weak_topics_bar`).
- Detailed expandable historical records table.

---

## 3. Session-State Structure (`ui/state.py`)

| Key | Type | Default | Purpose |
|---|---|---|---|
| `app_mode` | `str` | `"demo"` | Current mode (`"live"` or `"demo"`) |
| `selected_role` | `str` | `"Software Developer"` | Active target role |
| `deep_review` | `bool` | `False` | Deep review toggle |
| `file_hash` | `str | None` | `None` | MD5 fingerprint of uploaded document |
| `file_name` | `str | None` | `None` | Name of uploaded document |
| `file_size` | `int | None` | `None` | Byte size of uploaded document |
| `extracted_text` | `str | None` | `None` | Extracted resume text |
| `parsed_resume` | `ParsedResume | None` | `None` | Parsed resume Pydantic model |
| `review_result` | `ResumeReviewResult | None` | `None` | Resume evaluation output |
| `review_stale` | `bool` | `False` | Invalidation flag for resume review |
| `review_role` | `str | None` | `None` | Role for which review was computed |
| `gap_result` | `GapReport | None` | `None` | Skill gap analysis output |
| `gap_stale` | `bool` | `False` | Invalidation flag for skill gap |
| `gap_role` | `str | None` | `None` | Role for which gap was computed |
| `questions` | `list[Question] | None` | `None` | Generated questions list |
| `questions_stale` | `bool` | `False` | Invalidation flag for questions |
| `interview_state` | `str` | `"idle"` | `"idle"`, `"active"`, `"completed"` |
| `interview_session`| `InterviewSession | None` | `None` | Active mock interview session |
| `active_question_idx`| `int` | `0` | Current question index |
| `interview_answers`| `list[InterviewAnswer]` | `[]` | Collected interview evaluations |
| `export_pdf_bytes` | `bytes | None` | `None` | Cached PDF report bytes |
| `export_json_bytes`| `bytes | None` | `None` | Cached JSON export bytes |
| `ollama_status` | `dict | None` | `None` | Bounded health-check cache |
| `ollama_checked_at`| `float | None` | `None` | Timestamp of last health check |

---

## 4. Backend Integration Mapping

| UI Module | Backend Function | Location | In/Out Contract |
|---|---|---|---|
| Resume Parse | `extract_text(bytes, filename)` | `core/parser.py` | `(str, str)` text & error |
| Resume Structure | `extract_resume(text)` | `core/parser.py` | `ParsedResume` model |
| Deterministic Rules | `rule_checks(parsed)` | `core/parser.py` | `list[RuleCheckResult]` |
| Rule Score | `rule_score(checks)` | `core/parser.py` | `float` (0–85) |
| AI Review Pipeline | `review_resume_live(parsed, role, deep)` | `ui/adapters.py` + `core/llm.py` | `(ResumeReviewResult, str)` |
| Role Data | `load_roles()` | `core/skill_gap.py` | `dict[str, dict]` |
| Skill Gap Match | `compute_gap(skills, role, jd)` | `core/skill_gap.py` | `GapReport` model |
| Study Roadmap | `build_roadmap(gap)` | `core/skill_gap.py` | `list[dict]` (4 weeks) |
| Project Ideas | `build_project_ideas(gap)` | `core/skill_gap.py` | `list[dict]` (3 projects) |
| Question Gen | `generate_questions(...)` | `core/question_gen.py` | `list[Question]` |
| Answer Evaluation | `evaluate_answer(q, ans)` | `core/interview.py` | `InterviewAnswer` model |
| Session Summary | `build_interview_summary(session)` | `core/interview.py` | `dict` summary |
| PDF Export | `build_report_pdf(**kwargs)` | `core/report.py` | `bytes` ReportLab document |
| JSON Export | `build_report_json(**kwargs)` | `core/report.py` | `bytes` UTF-8 JSON |
| SQLite Save Review | `save_resume_review(...)` | `core/db.py` | `int` row id |
| SQLite Save Gap | `save_gap_report(...)` | `core/db.py` | `int` row id |
| SQLite Save Interview| `save_session(role, diff, avg, report, ans)` | `core/db.py` | `int` row id (Preserved) |
| SQLite History | `ats_history()`, `score_history()` | `core/db.py` | `list[dict]` |

---

## 5. Implementation Checklist

- [x] Inspect existing dependencies and environment
- [x] Initialize requirements.txt and `.streamlit/config.toml`
- [x] Create Pydantic v2 schemas (`core/schemas.py`)
- [x] Create SQLite persistence engine (`core/db.py`)
- [x] Implement ReportLab PDF and JSON generators (`core/report.py`)
- [x] Implement PDF/DOCX parser and 85-pt rule checks (`core/parser.py`)
- [x] Implement role knowledge bases and RapidFuzz matcher (`core/skill_gap.py`)
- [x] Implement LLM adapter with bounded Ollama check (`core/llm.py`)
- [x] Implement question generator (`core/question_gen.py`)
- [x] Implement mock interview evaluator (`core/interview.py`)
- [x] Implement Deep Review narrative adapter (`core/reflection.py`)
- [x] Build theme tokens and sanitized CSS (`ui/theme.py`)
- [x] Build centralized session state with invalidation logic (`ui/state.py`)
- [x] Build comprehensive synthetic demo fixtures (`ui/demo_data.py`)
- [x] Build backend integration adapters (`ui/adapters.py`)
- [x] Build Plotly analytics figure generators (`ui/analytics.py`)
- [x] Build UI reusable components (`ui/components.py`)
- [x] Build Resume Review screen (`ui/resume_tab.py`)
- [x] Build Skill Gap screen (`ui/gap_tab.py`)
- [x] Build Questions screen (`ui/questions_tab.py`)
- [x] Build Mock Interview screen (`ui/interview_tab.py`)
- [x] Build Progress screen (`ui/progress_tab.py`)
- [x] Build application shell and navigation (`app.py` <= 200 lines)
- [x] Write automated tests across state, adapters, analytics, app
- [x] Verify complete test suite execution with pytest
