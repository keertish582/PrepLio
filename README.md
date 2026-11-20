# PrepLio — Placement Preparation Assistant

> **"Review your resume, identify skill gaps, and practice with purpose."**

**PrepLio** is an offline-capable, single-user placement readiness assistant built with **Python 3.13**, **Streamlit**, **Plotly**, and **Qwen3:4b** running locally via Ollama. It evaluates resumes through deterministic heuristics and AI feedback, computes weighted benchmark skill gaps, generates targeted interview question banks, simulates mock interviews with multi-criteria rubric evaluation, and tracks candidate progress across local SQLite tables.

---

## Key Features

- **📄 B1 & B3: Resume Review:**
  - In-memory PDF/DOCX parsing (pdfplumber, pypdf, python-docx).
  - 85-point deterministic placement rule checks (contact info, sections, action verbs, quantified metrics, length, pronoun audits).
  - 15-point AI section assessment with STAR bullet rewrites and prioritized action items.
  - Transparent heuristic score notice (not an employer ATS predictor).
  - Export to structured PDF reports (ReportLab) and schema-validated JSON.

- **🎯 B2: Skill Gap Analysis:**
  - Role knowledge bases for `Software Developer`, `Data Scientist`, `Frontend Developer`, and `DevOps Engineer`.
  - Custom Job Description (JD) text extraction and editable requirements.
  - RapidFuzz token matching with recognized aliases (`postgres` → `SQL`, `k8s` → `Kubernetes`, etc.) and punctuation preservation (`C++`, `C#`, `.NET`, `Node.js`, `CI/CD`).
  - Weighted matching where core must-haves count double.
  - 4-week structured study roadmaps and portfolio project ideas with concrete deliverables.

- **💡 Questions Bank:**
  - Role-specific technical, behavioral, and system design questions.
  - Resume project context injection for personalized inquiry.
  - Practice mode with expandable key talking points.

- **🎙️ Mock Interview Simulation:**
  - Interactive text-based interview with explicit lifecycle state machine (`idle` → `active` → `completed`).
  - Dual modes: **Coaching Mode** (instant rubric feedback per question) and **Simulation Mode** (exam conditions with final debrief).
  - 3-factor evaluation rubric: Technical Correctness (50%), Communication Clarity (25%), and Nuanced Depth (25%).

- **📈 B5: Progress Tracking & Analytics:**
  - Plotly interactive visualizations: Resume Readiness Gauge, Rule Breakdown Bar, Section Radar Chart, Role Match Donut, Score Trajectory Lines, and Weak Topic Frequency Bars.
  - Scale separation: 0–10 interview scores are strictly isolated from 0–100 resume scores on separate labeled axes.
  - Local SQLite persistence with parameterized transactions.

- **🧪 Full Demo Mode:**
  - Complete, zero-dependency offline experience with synthetic fixtures.
  - Never claims sample data is live AI feedback; persistent Demo Mode banner.
  - No synthetic data is written into live database tables.

- **🔒 Local Privacy Guarantee:**
  - Zero external cloud calls, no telemetry, no CDNs, no tracking fonts.
  - Uploaded files remain in memory; raw resume text is never persisted to disk.
  - User-confirmed local data deletion.

---

## Architecture & Directory Structure

```
PrepLio/
├── app.py                     # Main application entry point & shell (< 200 lines)
├── requirements.txt           # Pinned tested dependency versions
├── .streamlit/
│   └── config.toml            # Headless server & light design theme tokens
│
├── core/                      # Core business logic & persistence
│   ├── schemas.py             # Pydantic v2 data models
│   ├── parser.py              # B1: Document parsing & deterministic rule checks
│   ├── skill_gap.py           # B2: Role knowledge & RapidFuzz skill gap matcher
│   ├── report.py              # B5: ReportLab PDF builder & JSON serializer
│   ├── db.py                  # Local SQLite storage & parameterized transactions
│   ├── llm.py                 # Ollama adapter & bounded health check
│   ├── question_gen.py        # Question bank generation
│   ├── interview.py           # Multi-criteria mock interview evaluator
│   └── reflection.py          # Optional Deep Review narrative pass
│
├── ui/                        # Presentation layer
│   ├── theme.py               # Design tokens, CSS injection, layout styling
│   ├── state.py               # Centralized session state & invalidation logic
│   ├── components.py          # Reusable cards, metric badges, and skill pills
│   ├── adapters.py            # Normalized backend adapters with error handling
│   ├── demo_data.py           # Synthetic demo fixtures (strong/weak/questions)
│   ├── analytics.py           # Reusable Plotly chart generators
│   ├── resume_tab.py          # Screen 1: Resume Review
│   ├── gap_tab.py             # Screen 2: Skill Gap Analysis
│   ├── questions_tab.py       # Screen 3: Targeted Question Bank
│   ├── interview_tab.py       # Screen 4: Text-Based Mock Interview
│   └── progress_tab.py        # Screen 5: Progress & Analytics Dashboard
│
├── data/
│   ├── roles/                 # Predefined JSON benchmark curricula
│   │   ├── software_developer.json
│   │   ├── data_scientist.json
│   │   ├── frontend_developer.json
│   │   └── devops_engineer.json
│   └── demo/                  # Realistic sample resume texts
│       ├── strong_resume.txt
│       └── weak_resume.txt
│
├── docs/
│   ├── frontend_plan.md       # Screen layout, components, state, integration plan
│   └── integration_contract.md# Documented backend contracts and signatures
│
└── tests/                     # Automated test suite (30 passing tests)
    ├── test_ui_state.py       # State initialization & invalidation tests
    ├── test_ui_adapters.py    # Backend adapters & fallback testing
    ├── test_analytics.py      # Plotly charts & export generator tests
    ├── test_app.py            # Streamlit AppTest integration verification
    └── UI_CHECKLIST.md        # Comprehensive manual verification checklist
```

---

## Tested Dependency Versions

| Package | Version |
|---|---|
| Python | 3.13.14 (Compatible with 3.11+) |
| Streamlit | 1.67.0 |
| Plotly | 6.8.0 |
| Pydantic | 2.14.4 |
| pandas | 3.0.4 |
| pdfplumber | 0.11.10 |
| pypdf | 6.21.3 |
| python-docx | 1.2.0 |
| RapidFuzz | 3.14.6 |
| ReportLab | 5.1.0 |
| pytest | 9.2.0 |
| ollama | 0.6.3 |

---

## Installation & Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Optional: Configure Local Ollama (For Live Mode)
PrepLio works out of the box in **Demo Mode** without Ollama installed. To enable **Live Mode**:
```bash
# Start local Ollama daemon
ollama serve

# Pull the lightweight model
ollama pull qwen3:4b
```

### 3. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## Automated Test Suite

To run the complete automated test suite:
```bash
python -m pytest -v
```

**Test Results:**
- `tests/test_analytics.py`: 14 tests covering all 7 Plotly figures (empty and populated states), PDF generation, and JSON schema conformance.
- `tests/test_app.py`: 4 integration tests using Streamlit `AppTest` verifying shell compile, tab layout, sidebar controls, and demo button flows.
- `tests/test_ui_adapters.py`: 7 tests verifying Ollama health checks, document parser error handling, rule evaluations, skill gap matching, and question/evaluator fallbacks.
- `tests/test_ui_state.py`: 5 tests verifying state defaults, file fingerprinting, reactive invalidation, and session wipes.
- **Summary:** **30 passed in 33s.**

---

## Manual UI Checklist

Follow `tests/UI_CHECKLIST.md` for a comprehensive 35-point manual inspection covering:
- File validations (empty, corrupt, encrypted, oversized).
- 5-stage progress indicator execution.
- Stale result warnings upon role or resume modification.
- Single-submit locks on mock interview answer submissions.
- PDF and JSON download verification.
- Confirmed database deletion verification.

---

## Privacy Policy

- **No Remote Telemetry:** All Streamlit usage stats and telemetry are disabled via `.streamlit/config.toml`.
- **In-Memory Documents:** Resumes are parsed in memory and never written to permanent disk storage.
- **Local SQLite Storage:** Only structured review metadata (scores, section feedback, weak topics) is stored when the user explicitly clicks *"Save locally"*.
- **Confirmation Protection:** Saved records can be wiped at any time using the confirmed *"Delete Data"* button in the sidebar.
