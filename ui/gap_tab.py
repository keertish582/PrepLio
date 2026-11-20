"""
ui/gap_tab.py — Screen 2: Skill Gap Analysis.
Module B2 frontend implementation.
"""
from __future__ import annotations

import json
import streamlit as st
import ui.state as S
import ui.theme as T
import ui.analytics as A
import ui.components as C
from ui.demo_data import DEMO_GAP
from core.schemas import GapReport, SkillMatch


def render():
    st.markdown('<div class="section-h">Skill Gap Analysis & Learning Roadmap</div>', unsafe_allow_html=True)
    st.markdown("Compare your verified profile against industry benchmarks or custom job descriptions to identify key skill gaps and study roadmaps.")

    mode = S.get(S.APP_MODE)
    if mode == "demo":
        T.demo_banner()

    if S.get(S.GAP_STALE):
        T.stale_warning(
            "Target role or resume profile has changed. The analysis below reflects prior settings. Click 'Analyze Gap' to recompute."
        )

    _render_source_section(mode)

    gap_res: GapReport | None = S.get(S.GAP_RESULT)
    if gap_res:
        _render_results_section(gap_res, mode)

    T.footer()


def _render_source_section(mode: str):
    C.card_start("Target Benchmark & Candidate Profile")

    # Step 1: Candidate skill source
    parsed = S.get(S.PARSED_RESUME)
    candidate_skills: list[str] = []
    
    if parsed and parsed.skills:
        candidate_skills = parsed.skills
        st.success(f"✓ Using **{len(candidate_skills)}** skills extracted from your resume ({', '.join(candidate_skills[:8])}{'...' if len(candidate_skills) > 8 else ''}).")
    else:
        st.info("💡 No resume skills detected in the current session. You can enter your skills manually below or upload your resume in the **Resume Review** tab.")
        manual_skills_str = st.text_input(
            "Your Skills (comma-separated):",
            value="Python, SQL, Git, Docker, REST APIs" if mode == "demo" else "",
            placeholder="e.g. Python, SQL, Git, Docker, REST APIs, FastAPIs",
            key="gap_manual_skills",
        )
        if manual_skills_str.strip():
            candidate_skills = [s.strip() for s in manual_skills_str.split(",") if s.strip()]

    st.markdown("---")

    # Step 2: Target benchmark mode
    target_mode = st.radio(
        "Select benchmark specification:",
        ["Standard Role Benchmark", "Custom Job Description (JD)"],
        horizontal=True,
        key="gap_benchmark_mode",
    )

    role = S.get(S.SELECTED_ROLE) or "Software Developer"
    custom_jd_skills = None

    if target_mode == "Standard Role Benchmark":
        try:
            from core.skill_gap import load_roles
            roles = load_roles()
            role_info = roles.get(role, {})
            
            with st.expander(f"📋 View Standard Curriculum: {role}", expanded=False):
                col_m, col_g = st.columns(2)
                with col_m:
                    st.markdown("**Must-Have Core Skills:**")
                    for s in role_info.get("must_haves", []):
                        st.markdown(f"- 🔴 {s}")
                with col_g:
                    st.markdown("**Good-to-Have Complementary Skills:**")
                    for s in role_info.get("good_to_haves", []):
                        st.markdown(f"- 🟢 {s}")
        except Exception as e:
            st.caption(f"Role benchmark information could not be loaded: {e}")

    else:
        st.markdown("**Paste Job Description Text:**")
        jd_input = st.text_area(
            "Paste JD",
            height=140,
            placeholder="Paste complete job description requirements here...",
            label_visibility="collapsed",
            key="jd_raw_input",
        )
        col_ext, _ = st.columns([1, 2])
        with col_ext:
            if st.button("Extract Requirements from JD", key="btn_ext_jd", use_container_width=True) and jd_input.strip():
                try:
                    from core.skill_gap import extract_jd_skills
                    extracted = extract_jd_skills(jd_input)
                    st.session_state["jd_must_extracted"] = ", ".join(extracted.get("must_haves", []))
                    st.session_state["jd_good_extracted"] = ", ".join(extracted.get("good_to_haves", []))
                    st.success("Extracted requirements below. You can refine them before running the gap analysis.")
                except Exception as e:
                    st.error(f"Extraction failed: {e}")

        # Editable extracted JD skills
        raw_must = st.text_area(
            "Must-have requirements (editable, comma-separated):",
            value=st.session_state.get("jd_must_extracted", ""),
            key="jd_must_editor",
            height=60,
        )
        raw_good = st.text_area(
            "Good-to-have requirements (editable, comma-separated):",
            value=st.session_state.get("jd_good_extracted", ""),
            key="jd_good_editor",
            height=60,
        )
        if raw_must or raw_good:
            custom_jd_skills = {
                "must_haves": [s.strip() for s in raw_must.split(",") if s.strip()],
                "good_to_haves": [s.strip() for s in raw_good.split(",") if s.strip()],
            }

    # Action trigger
    col_act, _ = st.columns([1, 2])
    with col_act:
        if st.button("🔍 Analyze Skill Gap", type="primary", key="btn_exec_gap", use_container_width=True):
            if not candidate_skills:
                st.warning("Please provide at least one skill to match against requirements.")
            else:
                _run_gap_analysis(candidate_skills, role, custom_jd_skills, mode)

    C.card_end()


def _run_gap_analysis(candidate_skills: list[str], role: str, custom_jd_skills: dict | None, mode: str):
    if mode == "demo":
        gap = DEMO_GAP.model_copy(deep=True)
        gap.role = role
        S.set_val(S.GAP_RESULT, gap)
        S.set_val(S.GAP_ROLE, role)
        S.set_val(S.GAP_STALE, False)
        st.rerun()
        return

    from ui.adapters import compute_gap
    with st.spinner("Calculating skill overlap, alias mappings, and evidence matching..."):
        jd_text = ""
        if custom_jd_skills:
            jd_text = " ".join(custom_jd_skills.get("must_haves", []) + custom_jd_skills.get("good_to_haves", []))
        gap, err = compute_gap(candidate_skills, role, jd_text=jd_text)

    if err or gap is None:
        st.error(f"❌ Skill gap analysis failed: {err}")
        return

    S.set_val(S.GAP_RESULT, gap)
    S.set_val(S.GAP_ROLE, role)
    S.set_val(S.GAP_STALE, False)
    st.rerun()


def _render_results_section(gap: GapReport, mode: str):
    st.markdown("---")
    st.markdown('<div class="section-h">Benchmark Alignment Results</div>', unsafe_allow_html=True)

    col_chart, col_skills = st.columns([1, 1])

    with col_chart:
        fig_d = A.match_donut(gap.match_pct, f"Role Match ({gap.role})")
        st.plotly_chart(fig_d, use_container_width=True)
        st.caption("ℹ️ **Scoring Weight:** Must-have skills carry 2x weight relative to good-to-have skills.")

    with col_skills:
        # Must haves
        mh_matched = sum(1 for s in gap.must_haves if s.matched)
        C.metric_badge("Must-Have Coverage", f"{mh_matched} / {len(gap.must_haves)}", "Critical core competencies", "accent")
        
        st.markdown("**Core Requirements:**")
        for m in gap.must_haves:
            C.skill_badge(m.skill, m.matched, m.evidence)

        st.markdown("<br>", unsafe_allow_html=True)
        # Good to haves
        gth_matched = sum(1 for s in gap.good_to_haves if s.matched)
        C.metric_badge("Good-to-Have Coverage", f"{gth_matched} / {len(gap.good_to_haves)}", "Value-add secondary skills", "normal")
        
        st.markdown("**Secondary Skills:**")
        for g in gap.good_to_haves:
            C.skill_badge(g.skill, g.matched, g.evidence)

    st.caption("🔎 **Evidence Notation:** 🎯 Exact match • 🔄 Recognized alias • ≈ Semantic fuzzy match • ✕ Evidence not found. Matches reflect document evidence, not verified technical proficiency.")

    # Roadmap section
    if gap.roadmap:
        st.markdown('<div class="section-h">Targeted 4-Week Study Roadmap</div>', unsafe_allow_html=True)
        st.markdown("Prioritized curriculum focusing on your missing core requirements.")

        for week in gap.roadmap:
            w_num = week.get("week", 1)
            focus = week.get("focus_skill", "Core Skill")
            with st.expander(f"📅 Week {w_num}: Focus on {focus}", expanded=(w_num == 1)):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Key Topics to Study:**")
                    for top in week.get("topics", []):
                        st.markdown(f"- 📖 {top}")
                    
                    st.markdown("**Curated Reference Material:**")
                    for res in week.get("resources", []):
                        st.markdown(f"- 🔗 {res}")

                with c2:
                    st.markdown("**Hands-On Practice Tasks:**")
                    for task in week.get("tasks", []):
                        st.markdown(f"- [ ] {task}")

                    if week.get("completion_evidence"):
                        st.markdown(f"**Verification Deliverable:** `{week['completion_evidence']}`")

    # Project ideas
    if gap.project_ideas:
        st.markdown('<div class="section-h">Recommended Portfolio Projects</div>', unsafe_allow_html=True)
        cols = st.columns(len(gap.project_ideas[:3]))
        for idx, proj in enumerate(gap.project_ideas[:3]):
            with cols[idx]:
                C.card_start(proj.get("title", f"Project {idx+1}"))
                st.caption(f"**Practices:** {', '.join(proj.get('skills_practiced', []))}")
                st.markdown(proj.get("description", ""))
                if proj.get("deliverables"):
                    st.markdown("**Key Deliverables:**")
                    for d in proj["deliverables"]:
                        st.markdown(f"- `{d}`")
                C.card_end()

    # Save & Export
    st.markdown('<div class="section-h">Export & Save Actions</div>', unsafe_allow_html=True)
    c_save, c_json = st.columns(2)

    with c_save:
        if mode == "live":
            if st.button("💾 Save Gap Report Locally", key="btn_save_gap_db", use_container_width=True):
                from ui.adapters import save_gap
                save_gap(gap, origin="live")
                st.success("✅ Gap analysis saved to local SQLite database.")
        else:
            st.caption("🔒 Save disabled in Demo Mode.")

    with c_json:
        gap_dict = gap.model_dump()
        gap_json = json.dumps(gap_dict, indent=2, default=str).encode("utf-8")
        st.download_button(
            "⬇️ Export Gap Analysis (JSON)",
            data=gap_json,
            file_name=f"preplio_gap_{gap.role.lower().replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True,
            key="btn_dl_gap_json",
        )
