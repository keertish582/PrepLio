"""
ui/resume_tab.py — Screen 1: Resume Review.
Module B1 & B3 frontend implementation.
"""
from __future__ import annotations

import streamlit as st
import ui.state as S
import ui.theme as T
import ui.analytics as A
import ui.components as C
from ui.demo_data import DEMO_REVIEW_STRONG, DEMO_REVIEW_WEAK
from core.schemas import ResumeReviewResult, ParsedResume

MAX_UPLOAD_MB = 5
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


def render():
    st.markdown('<div class="section-h">Resume Review</div>', unsafe_allow_html=True)
    st.markdown("Upload, inspect, and improve your resume with deterministic rule checks and structured AI section feedback.")

    mode = S.get(S.APP_MODE)
    if mode == "demo":
        T.demo_banner()

    if S.get(S.REVIEW_STALE):
        T.stale_warning(
            "Selected role or uploaded resume changed since last review. The results below reflect the previous analysis. Click 'Review resume' to update."
        )

    _render_upload_section(mode)

    result: ResumeReviewResult | None = S.get(S.REVIEW_RESULT)
    if result:
        _render_results_section(result, mode)

    T.footer()


def _render_upload_section(mode: str):
    C.card_start("Resume Document Upload")
    st.caption(f"Accepted formats: PDF, DOCX • Max size: {MAX_UPLOAD_MB} MB • Processed locally in memory")

    col_up, col_demo = st.columns([3, 2])
    with col_up:
        uploaded = st.file_uploader(
            "Choose a PDF or DOCX resume",
            type=["pdf", "docx"],
            key="resume_file_uploader",
            label_visibility="collapsed",
        )

    with col_demo:
        if mode == "demo":
            st.markdown("**Sample Resumes (Demo Mode):**")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                if st.button("🌟 Strong Resume", key="demo_btn_strong", use_container_width=True):
                    _load_demo_scenario("strong")
            with col_d2:
                if st.button("⚠️ Needs Work", key="demo_btn_weak", use_container_width=True):
                    _load_demo_scenario("weak")
        else:
            st.info("💡 Files are kept in memory and never sent to external cloud APIs.")

    if uploaded is not None:
        file_bytes = uploaded.read()
        file_name = uploaded.name
        file_size = len(file_bytes)

        # Size check
        if file_size > MAX_UPLOAD_BYTES:
            st.error(f"❌ File '{file_name}' ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed size of {MAX_UPLOAD_MB} MB.")
            C.card_end()
            return

        # Format validation
        lower_name = file_name.lower()
        if not (lower_name.endswith(".pdf") or lower_name.endswith(".docx")):
            st.error("❌ Unsupported file format. Please upload a standard .pdf or .docx document.")
            C.card_end()
            return

        # Fingerprint check
        fp = S.file_fingerprint(file_bytes)
        current_fp = S.get(S.FILE_HASH)
        if current_fp != fp:
            S.on_file_change(fp)
            S.set_val(S.FILE_NAME, file_name)
            S.set_val(S.FILE_SIZE, file_size)

        st.success(f"📄 **{file_name}** ({file_size / 1024:.1f} KB) ready for analysis.")

        # Action buttons
        btn_col1, btn_col2, _ = st.columns([2, 1, 3])
        with btn_col1:
            if st.button("🚀 Review Resume", type="primary", key="btn_run_review", use_container_width=True):
                _execute_review(file_bytes, file_name, mode)
        with btn_col2:
            if st.button("Clear", key="btn_clear_resume", use_container_width=True):
                S.clear_session()
                st.rerun()

    C.card_end()


def _load_demo_scenario(scenario: str):
    role = S.get(S.SELECTED_ROLE) or "Software Developer"
    if scenario == "strong":
        res = DEMO_REVIEW_STRONG.model_copy(deep=True)
    else:
        res = DEMO_REVIEW_WEAK.model_copy(deep=True)
    res.target_role = role
    S.set_val(S.REVIEW_RESULT, res)
    S.set_val(S.REVIEW_ROLE, role)
    S.set_val(S.REVIEW_STALE, False)
    S.set_val(S.PARSED_RESUME, res.parsed)
    S.set_val(S.EXTRACTED_TEXT, res.parsed.raw_text)
    S.set_val(S.EXPORT_PDF_BYTES, None)
    S.set_val(S.EXPORT_JSON_BYTES, None)
    st.rerun()


def _execute_review(file_bytes: bytes, file_name: str, mode: str):
    from ui.adapters import parse_document, review_resume_live
    role = S.get(S.SELECTED_ROLE)
    deep = S.get(S.DEEP_REVIEW)

    prog_bar = st.progress(0)
    status_text = st.empty()

    try:
        # Stage 1: Validate document
        status_text.info("Stage 1/5: Validating document structure...")
        prog_bar.progress(15)

        # Stage 2: Extract content
        status_text.info("Stage 2/5: Extracting text, sections, and candidate skills...")
        prog_bar.progress(35)
        parsed, parse_err = parse_document(file_bytes, file_name)
        if parse_err:
            prog_bar.empty()
            status_text.empty()
            _handle_parse_error(parse_err)
            return

        # Store parsed resume
        S.set_val(S.PARSED_RESUME, parsed)
        S.set_val(S.EXTRACTED_TEXT, parsed.raw_text)

        # Stage 3: Run rule checks
        status_text.info("Stage 3/5: Running deterministic placement checks (0-85 pts)...")
        prog_bar.progress(60)

        # Stage 4: Review sections
        status_text.info(f"Stage 4/5: Reviewing sections with AI for {role} role...")
        prog_bar.progress(85)

        if mode == "demo":
            review_res = DEMO_REVIEW_STRONG.model_copy(deep=True)
            review_res.parsed = parsed
            review_res.target_role = role
        else:
            review_res, rev_err = review_resume_live(parsed, role, deep=deep)
            if rev_err:
                st.warning(f"Note on AI review: {rev_err}")

        # Stage 5: Prepare results
        status_text.info("Stage 5/5: Preparing final readiness scores and action checklist...")
        prog_bar.progress(100)

        S.set_val(S.REVIEW_RESULT, review_res)
        S.set_val(S.REVIEW_ROLE, role)
        S.set_val(S.REVIEW_STALE, False)
        S.set_val(S.EXPORT_PDF_BYTES, None)
        S.set_val(S.EXPORT_JSON_BYTES, None)

        prog_bar.empty()
        status_text.success("✅ Resume review complete!")
        st.rerun()

    except Exception as e:
        prog_bar.empty()
        status_text.empty()
        st.error(f"❌ An error occurred during analysis: {type(e).__name__} - {str(e)}")


def _handle_parse_error(err: str):
    err_low = err.lower()
    if "encrypted" in err_low or "password" in err_low:
        st.error("🔒 Document is password-protected or encrypted. Please re-upload an unprotected PDF or DOCX.")
    elif "too short" in err_low or "insufficient" in err_low:
        st.warning("⚠️ Insufficient extractable text found. If this document was scanned, text may not be selectable. Please ensure selectable text is present.")
    elif "corrupt" in err_low:
        st.error("❌ Document file appears corrupted and could not be read. Please re-export or save a fresh copy.")
    else:
        st.error(f"❌ Extraction error: {err}")


def _render_results_section(result: ResumeReviewResult, mode: str):
    st.markdown("---")
    st.markdown('<div class="section-h">Evaluation Overview</div>', unsafe_allow_html=True)

    st.caption(
        "ℹ️ **Scoring Notice:** Project-defined heuristic based on resume rules (0–85) and AI feedback (0–15). "
        "Not an employer ATS result or a prediction of selection."
    )

    # Preview and editable extracted content
    parsed = result.parsed
    if parsed and parsed.raw_text:
        with st.expander("📄 Extracted Document Preview & Editable Skills", expanded=False):
            st.markdown(f"**Document:** `{parsed.file_name}` ({parsed.file_size_bytes / 1024:.1f} KB)")
            st.text_area("Extracted Text Preview (First 800 chars)", parsed.raw_text[:800] + ("..." if len(parsed.raw_text) > 800 else ""), height=120, disabled=True)
            
            raw_skills_val = ", ".join(parsed.skills)
            updated_skills_str = st.text_area(
                "Extracted Skills (Edit or add comma-separated skills below):",
                value=raw_skills_val,
                key="resume_skills_editor",
                height=80,
            )
            if updated_skills_str != raw_skills_val:
                parsed.skills = [s.strip() for s in updated_skills_str.split(",") if s.strip()]
                S.set_val(S.PARSED_RESUME, parsed)
                st.caption("Skills updated in session state.")

    # Top metrics row
    col_gauge, col_stats = st.columns([1, 1])

    with col_gauge:
        if result.final_score is not None and result.ai_assessment_complete:
            fig_g = A.ats_gauge(result.final_score, 100, "Resume Readiness")
            st.plotly_chart(fig_g, use_container_width=True)
        else:
            fig_g = A.ats_gauge(None, 100, "Resume Readiness")
            st.plotly_chart(fig_g, use_container_width=True)
            st.info("ℹ️ Final score incomplete: AI assessment unavailable. Showing rule subtotal.")

    with col_stats:
        m1, m2 = st.columns(2)
        with m1:
            C.metric_badge("Deterministic Rules", f"{result.rule_bundle.rule_score:.0f} / 85", "Formatting, sections, metrics", "accent")
        with m2:
            ai_val = f"{result.ai_score:.1f} / 15" if (result.ai_score is not None and result.ai_assessment_complete) else "Unavailable"
            badge_t = "success" if result.ai_assessment_complete else "warning"
            C.metric_badge("AI Section Assessment", ai_val, "Role alignment & impact", badge_t)

        m3, m4 = st.columns(2)
        with m3:
            C.metric_badge("Sections Evaluated", f"{len(result.section_feedback)}", "Standard resume sections", "normal")
        with m4:
            passed_count = sum(1 for c in result.rule_bundle.checks if c.passed)
            total_checks = len(result.rule_bundle.checks)
            C.metric_badge("Checks Passed", f"{passed_count} / {total_checks}", "Rule-based criteria", "normal")

    # Rule breakdown chart
    if result.rule_bundle.checks:
        st.markdown('<div class="section-h">Deterministic Rule Breakdown</div>', unsafe_allow_html=True)
        checks_data = [c.model_dump() for c in result.rule_bundle.checks]
        fig_bar = A.rule_breakdown_bar(checks_data)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Section radar chart if 3+ sections
    if len(result.section_feedback) >= 3:
        sec_dicts = [{"section_name": s.section_name, "score": s.score} for s in result.section_feedback]
        fig_radar = A.section_scores_radar(sec_dicts)
        st.plotly_chart(fig_radar, use_container_width=True)

    # Executive summary
    if result.summary:
        st.markdown('<div class="section-h">Review Summary</div>', unsafe_allow_html=True)
        st.info(result.summary)

    # Priority fixes
    if result.priority_fixes:
        st.markdown('<div class="section-h">Priority Fixes (Max 6)</div>', unsafe_allow_html=True)
        st.caption("A checked task is for your personal tracking and does not automatically alter the computed score.")
        for i, fix in enumerate(result.priority_fixes[:6]):
            col_chk, col_content = st.columns([0.05, 0.95])
            with col_chk:
                st.checkbox("", key=f"fix_chk_{i}", label_visibility="collapsed")
            with col_content:
                C.priority_pill(fix.severity, fix.section, fix.action)

    # Section feedback expanders
    if result.section_feedback:
        st.markdown('<div class="section-h">Section-by-Section Feedback</div>', unsafe_allow_html=True)
        for s_idx, sec in enumerate(result.section_feedback):
            with st.expander(f"📌 {sec.section_name} — Score: {sec.score:.1f}/10", expanded=(s_idx == 0)):
                if sec.ai_generated:
                    st.caption("🤖 AI feedback is guidance. Verify suggestions before applying to your resume.")

                col_str, col_wk = st.columns(2)
                with col_str:
                    st.markdown("**Strengths:**")
                    if sec.strengths:
                        for s in sec.strengths:
                            st.markdown(f"- ✅ {s}")
                    else:
                        st.caption("No notable strengths recorded.")

                with col_wk:
                    st.markdown("**Areas for Improvement:**")
                    if sec.weaknesses:
                        for w in sec.weaknesses:
                            st.markdown(f"- ⚠️ {w}")
                    else:
                        st.caption("No significant weaknesses found.")

                if sec.original_bullets and sec.suggested_rewrites:
                    st.markdown("**Suggested Bullet Rewrites (STAR Method):**")
                    st.caption("Uses conservative placeholders such as [X%] where metrics should be inserted by you.")
                    for b_idx, (orig, rw) in enumerate(zip(sec.original_bullets, sec.suggested_rewrites)):
                        col_orig, col_rw = st.columns(2)
                        with col_orig:
                            st.markdown("*Original:*")
                            st.text_area(f"Original Bullet {b_idx+1}", value=orig, height=75, disabled=True, key=f"orig_{s_idx}_{b_idx}")
                        with col_rw:
                            st.markdown("*Suggested Rewrite (Copyable):*")
                            st.text_area(f"Rewrite {b_idx+1}", value=rw, height=75, key=f"rw_{s_idx}_{b_idx}")

                if sec.explanation:
                    st.markdown(f"**Coaching Note:** {sec.explanation}")

    # Export & Persistence actions
    st.markdown('<div class="section-h">Export & Save Actions</div>', unsafe_allow_html=True)
    exp_col1, exp_col2, exp_col3 = st.columns(3)

    with exp_col1:
        if st.button("📄 Generate PDF Report", key="btn_prep_pdf", use_container_width=True):
            _create_pdf_export(result, mode)
        pdf_bytes = S.get(S.EXPORT_PDF_BYTES)
        if pdf_bytes:
            st.download_button(
                "⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name=f"preplio_review_{result.target_role.lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="btn_dl_pdf",
            )

    with exp_col2:
        if st.button("📦 Generate JSON Export", key="btn_prep_json", use_container_width=True):
            _create_json_export(result, mode)
        json_bytes = S.get(S.EXPORT_JSON_BYTES)
        if json_bytes:
            st.download_button(
                "⬇️ Download JSON Data",
                data=json_bytes,
                file_name=f"preplio_review_{result.target_role.lower().replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True,
                key="btn_dl_json",
            )

    with exp_col3:
        if mode == "live":
            if st.button("💾 Save Review Locally", key="btn_save_db_review", use_container_width=True):
                from ui.adapters import save_review
                save_review(result, origin="live")
                st.success("✅ Review saved to local SQLite database.")
        else:
            st.caption("🔒 Save disabled in Demo Mode — synthetic data is not saved to disk.")


def _create_pdf_export(result: ResumeReviewResult, mode: str):
    from core.report import build_report_pdf
    try:
        fixes = [f.model_dump() for f in result.priority_fixes]
        secs = [s.model_dump(exclude={"original_bullets", "suggested_rewrites"}) for s in result.section_feedback]
        pdf = build_report_pdf(
            role=result.target_role,
            origin=mode,
            rule_score=result.rule_bundle.rule_score,
            ai_score=result.ai_score,
            final_score=result.final_score,
            ai_complete=result.ai_assessment_complete,
            summary=result.summary,
            priority_fixes=fixes,
            section_feedback=secs,
        )
        S.set_val(S.EXPORT_PDF_BYTES, pdf)
        st.success("PDF ready for download.")
        st.rerun()
    except Exception as e:
        st.error(f"PDF creation failed: {e}")


def _create_json_export(result: ResumeReviewResult, mode: str):
    from core.report import build_report_json
    try:
        fixes = [f.model_dump() for f in result.priority_fixes]
        secs = [s.model_dump(exclude={"original_bullets", "suggested_rewrites"}) for s in result.section_feedback]
        js = build_report_json(
            role=result.target_role,
            origin=mode,
            rule_score=result.rule_bundle.rule_score,
            ai_score=result.ai_score,
            final_score=result.final_score,
            ai_complete=result.ai_assessment_complete,
            summary=result.summary,
            priority_fixes=fixes,
            section_feedback=secs,
        )
        S.set_val(S.EXPORT_JSON_BYTES, js)
        st.success("JSON ready for download.")
        st.rerun()
    except Exception as e:
        st.error(f"JSON creation failed: {e}")
