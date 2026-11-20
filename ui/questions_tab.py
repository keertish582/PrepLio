"""
ui/questions_tab.py — Screen 3: Targeted Interview Question Bank.
Teammate B frontend integration for question generation.
"""
from __future__ import annotations

import streamlit as st
import ui.state as S
import ui.theme as T
import ui.components as C
from ui.demo_data import DEMO_QUESTIONS
from core.schemas import Question

AVAILABLE_CATEGORIES = [
    "Technical",
    "System Design",
    "Problem Solving",
    "Behavioral",
    "Domain Knowledge",
]


def render():
    st.markdown('<div class="section-h">Placement Interview Question Bank</div>', unsafe_allow_html=True)
    st.markdown("Generate curated technical and behavioral interview questions tailored to your target role and project portfolio.")

    mode = S.get(S.APP_MODE)
    if mode == "demo":
        T.demo_banner()

    _render_form(mode)

    questions: list[Question] | None = S.get(S.QUESTIONS)
    if questions:
        _render_questions_list(questions)

    T.footer()


def _render_form(mode: str):
    C.card_start("Configure Question Generation")

    current_role = S.get(S.SELECTED_ROLE) or "Software Developer"

    with st.form("question_gen_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            role = st.text_input("Target Role", value=current_role)
        with col2:
            difficulty = st.selectbox("Interview Difficulty", ["easy", "medium", "hard"], index=1)
        with col3:
            count = st.slider("Question Count", min_value=3, max_value=12, value=5)

        categories = st.multiselect(
            "Question Categories",
            AVAILABLE_CATEGORIES,
            default=["Technical", "Problem Solving", "System Design"],
        )

        has_resume = S.get(S.PARSED_RESUME) is not None
        include_resume = st.checkbox(
            "Include candidate resume & project context in question prompt",
            value=has_resume,
            help="Injects your parsed resume experience to generate customized behavioral and project questions.",
        )

        submitted = st.form_submit_button("⚡ Generate Questions", type="primary", use_container_width=True)

    if submitted:
        if not categories:
            st.warning("Please select at least one question category.")
            C.card_end()
            return

        resume_context = ""
        if include_resume:
            parsed = S.get(S.PARSED_RESUME)
            if parsed and parsed.raw_text:
                resume_context = parsed.raw_text[:600]

        _generate_questions(role, difficulty, count, categories, resume_context, mode)

    C.card_end()


def _generate_questions(role: str, difficulty: str, count: int, categories: list[str], resume_context: str, mode: str):
    if mode == "demo":
        qs = [q.model_copy(deep=True) for q in DEMO_QUESTIONS[:count]]
        S.set_val(S.QUESTIONS, qs)
        S.set_val(S.QUESTIONS_STALE, False)
        st.success(f"Generated {len(qs)} demo questions for {role}.")
        st.rerun()
        return

    from ui.adapters import generate_questions
    with st.spinner(f"Generating {count} questions for {role} using local Ollama model..."):
        qs, err = generate_questions(role, difficulty, count, categories, resume_context)

    if err:
        st.warning(f"⚠️ Integration Note: {err}")
        st.info("Falling back to curated domain questions for continuous practice.")
        qs = [q.model_copy(deep=True) for q in DEMO_QUESTIONS[:count]]

    S.set_val(S.QUESTIONS, qs)
    S.set_val(S.QUESTIONS_STALE, False)
    st.rerun()


def _render_questions_list(questions: list[Question]):
    st.markdown("---")
    st.markdown('<div class="section-h">Generated Questions</div>', unsafe_allow_html=True)

    col_toggle, _ = st.columns([1, 2])
    with col_toggle:
        practice_mode = st.toggle("Practice Mode (Collapse expected talking points)", value=True)

    for q in questions:
        diff_pill = {"easy": "🟢 Easy", "medium": "🟡 Medium", "hard": "🔴 Hard"}.get(q.difficulty, q.difficulty)
        cat_badge = f"**[{q.category.upper()}]** · *{q.topic}*"

        with st.expander(f"Question {q.number}: {q.question_text[:70]}... | {diff_pill}", expanded=not practice_mode):
            st.markdown(cat_badge)
            st.markdown(f"### {q.question_text}")

            st.caption("Copy question prompt:")
            st.code(q.question_text, language=None)

            if q.key_points:
                st.markdown("**Expected Key Points & Evaluation Criteria:**")
                for kp in q.key_points:
                    st.markdown(f"- 🎯 {kp}")
