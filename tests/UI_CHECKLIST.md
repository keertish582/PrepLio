# PrepLio — Manual UI Verification Checklist

Use this checklist to perform thorough manual end-to-end acceptance testing of the PrepLio Streamlit frontend.

---

## 1. Document Upload & Parsing (Tab 1: Resume Review)
- [ ] **Valid PDF Upload:** Upload a standard text-based PDF resume (< 5 MB). Verify filename and file size appear immediately with green confirmation.
- [ ] **Valid DOCX Upload:** Upload a `.docx` resume. Verify text extraction completes without error.
- [ ] **Oversized Upload:** Attempt uploading a document > 5 MB. Verify an explicit warning prevents analysis.
- [ ] **Empty Document:** Upload a 0-byte or blank document. Verify friendly guidance message appears instead of a Python exception.
- [ ] **Scanned/Unselectable PDF:** Upload an image-only PDF. Verify friendly warning: *"Insufficient extractable text found... text may not be selectable"*.
- [ ] **Encrypted PDF:** Upload a password-protected PDF. Verify clear error: *"Document is password-protected or encrypted"*.
- [ ] **Long Filenames:** Upload a file with a 50+ character filename. Verify UI wraps text cleanly without breaking the layout.
- [ ] **Editable Extracted Skills:** Inspect the extracted content preview expander. Edit comma-separated skills in the text area and confirm downstream gap analysis respects edits.

---

## 2. Review Pipeline & Scoring (Tab 1: Resume Review)
- [ ] **5-Stage Progress Bar:** Click "Review Resume". Verify progress transitions through all 5 genuine stages:
  1. Validating document structure
  2. Extracting text, sections, and candidate skills
  3. Running deterministic placement checks (0–85 pts)
  4. Reviewing sections with AI
  5. Preparing final readiness scores
- [ ] **Scoring Notice:** Verify clear disclaimer is visible: *"Project-defined heuristic based on resume rules (0–85) and AI feedback (0–15). Not an employer ATS result or a prediction of selection."*
- [ ] **Rule Breakdown Chart:** Verify horizontal Plotly bar chart renders checks with passed (green) and failed (red) bars.
- [ ] **Section Scores Radar:** Verify polar radar chart renders when 3+ sections are present.
- [ ] **Priority Fixes (Max 6):** Verify priority items display correct severity pills (🔴 High, 🟡 Medium, 🟢 Low).
- [ ] **Section Expanders:** Verify strengths (✅) and weaknesses (⚠️) are distinct. Check suggested rewrites show side-by-side original vs STAR suggested rewrite.
- [ ] **AI Outage Graceful Handling:** When Ollama is offline or uninstalled, verify rule score (X/85) is shown with an honest *"AI assessment unavailable"* tag, and the final score is marked incomplete (never showing a misleading zero or crash).

---

## 3. Skill Gap Analysis (Tab 2)
- [ ] **Resume Skills Inheritance:** Verify skills extracted in Tab 1 automatically populate Tab 2.
- [ ] **Manual Skills Fallback:** In an empty session, enter comma-separated skills manually and verify gap computes accurately.
- [ ] **Standard Role Mode:** Select each predefined role (`Software Developer`, `Data Scientist`, `Frontend Developer`, `DevOps Engineer`). Expand curriculum and verify must-haves and good-to-haves display.
- [ ] **Custom JD Mode:** Paste a custom job description, click "Extract Requirements from JD", verify extracted must-haves/good-to-haves appear in editable text boxes.
- [ ] **Evidence Badges:** Verify match evidence notation displays correctly: 🎯 Exact, 🔄 Recognized alias, ≈ Semantic fuzzy match, ✕ Not found.
- [ ] **Punctuation Skills:** Verify correct matching for punctuation-sensitive skills like `C++`, `C#`, `.NET`, `Node.js`, `CI/CD`.
- [ ] **Weighted Score:** Verify must-have skills are explained as counting double (2x).
- [ ] **Roadmap Cards:** Verify expandable 4-week study cards contain topics, curated resources, practice tasks, and completion evidence.
- [ ] **Project Ideas:** Verify 3 portfolio project cards render with practiced skills, descriptions, and concrete deliverables.

---

## 4. Question Bank (Tab 3)
- [ ] **Form Submission:** Verify questions are generated *only* when the form submit button is clicked (no accidental regeneration on tab clicks).
- [ ] **Category Multiselect:** Test selecting subsets of categories (`Technical`, `System Design`, `Behavioral`, `Problem Solving`).
- [ ] **Resume Context Toggle:** Enable the toggle and verify questions reference projects/skills from the uploaded resume.
- [ ] **Practice Mode Toggle:** Toggle "Practice Mode". Verify expected key talking points collapse when active and expand when disabled.
- [ ] **Copyable Text:** Verify question prompts can be copied via native code block copy controls.

---

## 5. Text-Based Mock Interview Simulation (Tab 4)
- [ ] **State Machine Progression:** Verify clean transitions: `idle` → `active` → `completed`.
- [ ] **Coaching Mode:** Submit an answer in Coaching Mode. Verify immediate rubric breakdown appears on the subsequent question card (Correctness 50%, Clarity 25%, Depth 25%, Covered points, Nuances to emphasize).
- [ ] **Simulation Mode:** Run in Simulation Mode. Verify expected points and evaluations remain concealed until all questions are completed.
- [ ] **Single Submission Lock:** Verify pressing Enter or re-clicking submit does not duplicate answers or skip questions.
- [ ] **Early Exit Confirmation:** Click "End Interview Early" and verify confirmation prompt prevents accidental session loss.
- [ ] **Final Summary:** Verify candidate average score (0–10), category scores Plotly bar chart, identified strengths, weak topics, and practice plan render cleanly.

---

## 6. Progress Tracking & Persistence (Tab 5)
- [ ] **Live vs Demo Separation:** In Demo Mode, verify synthetic milestones are displayed with an amber Demo banner. Verify save buttons are disabled/noted.
- [ ] **Local SQLite Persistence:** In Live Mode, click "Save Review Locally" in Tab 1 and "Save Interview" in Tab 4. Switch to Tab 5 and verify saved records appear in history charts and tables.
- [ ] **Score Scale Separation:** Verify 0–10 interview scores are strictly separated from 0–100 resume scores and plotted on distinct, labeled axes.
- [ ] **Role Filtering:** Select a role filter from the dropdown. Verify historical records filter appropriately.
- [ ] **Empty State:** With a fresh database, verify friendly empty state message: *"No saved sessions yet. Complete an analysis and choose Save locally."*

---

## 7. Exports & Privacy Controls
- [ ] **PDF Report Export:** Click "Generate PDF Report" in Tab 1. Verify a valid A4 PDF downloads with header, role, scores, priority fixes, section feedback, disclaimer, and page numbers.
- [ ] **JSON Data Export:** Click "Generate JSON Export". Verify valid JSON conforming to schema v1.0 downloads with raw resume text excluded.
- [ ] **Session Invalidation:**
  - Change target role in the sidebar after review: verify stale banner appears over old results.
  - Upload a new resume: verify prior results are cleared or flagged stale.
- [ ] **Clear Session:** Click "Clear Session" in the sidebar. Verify memory state is wiped while preserving the selected role.
- [ ] **Delete Data Confirmation:** Click "Delete Data" in the sidebar. Verify warning prompt appears. Click "Confirm" and verify all SQLite records are deleted.
