"""
ui/interview_tab.py — Screen 4: Text-Based Mock Interview Simulation.
Teammate B frontend integration for text interview evaluation.
"""
from __future__ import annotations

from datetime import datetime
import streamlit as st
import ui.state as S
import ui.theme as T
import ui.analytics as A
import ui.components as C
from ui.demo_data import DEMO_QUESTIONS, DEMO_SESSION, DEMO_INTERVIEW_ANSWERS
from core.schemas import InterviewSession, Question, InterviewAnswer


def render():
    st.markdown('<div class="section-h">Text-Based Mock Interview Simulation</div>', unsafe_allow_html=True)

    mode = S.get(S.APP_MODE)
    if mode == "demo":
        T.demo_banner()

    state = S.get(S.INTERVIEW_STATE) or "idle"

    if state == "idle":
        _render_setup(mode)
    elif state in ("active", "submitting"):
        _render_active_interview(mode)
    elif state == "completed":
        _render_completed_summary(mode)
    else:
        S.set_val(S.INTERVIEW_STATE, "idle")
        st.rerun()

    T.footer()


def _render_setup(mode: str):
    st.markdown("Practice responding to role-specific technical and behavioral questions under realistic interview conditions.")

    with st.expander("ℹ️ Interview Evaluation Rubric", expanded=False):
        st.markdown("""
- **Technical Correctness (50% weight):** Accuracy of technical facts, algorithms, and core concepts.
- **Communication Clarity (25% weight):** Structure, conciseness, and articulation (e.g. STAR method for behavioral).
- **Depth of Nuance (25% weight):** Trade-offs, edge cases, scalability, or concrete engineering real-world examples.
        """)

    C.card_start("Configure Simulation Session")

    current_role = S.get(S.SELECTED_ROLE) or "Software Developer"

    with st.form("interview_init_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            role = st.text_input("Role", value=current_role)
        with col2:
            difficulty = st.selectbox("Target Difficulty", ["easy", "medium", "hard"], index=1)
        with col3:
            q_count = st.slider("Questions", min_value=2, max_value=8, value=3)

        mode_choice = st.radio(
            "Evaluation Feedback Style:",
            [
                "Coaching Mode (Immediate feedback & rubric breakdown after each answer)",
                "Simulation Mode (Exam conditions: complete all answers before receiving comprehensive evaluation)",
            ],
            index=0,
        )

        started = st.form_submit_button("▶️ Start Mock Interview", type="primary", use_container_width=True)

    if started:
        style_key = "coaching" if "Coaching" in mode_choice else "simulation"
        _initialize_interview(role, difficulty, q_count, style_key, mode)

    C.card_end()


def _initialize_interview(role: str, difficulty: str, q_count: int, style_key: str, mode: str):
    if mode == "demo":
        questions = [q.model_copy(deep=True) for q in DEMO_QUESTIONS[:q_count]]
    else:
        from ui.adapters import generate_questions
        with st.spinner("Preparing interview questions with local Ollama..."):
            questions, err = generate_questions(role, difficulty, q_count, ["Technical", "Problem Solving", "System Design"])
        if not questions:
            st.warning(f"Using standard domain questions: {err}")
            questions = [q.model_copy(deep=True) for q in DEMO_QUESTIONS[:q_count]]

    new_session = InterviewSession(
        role=role,
        difficulty=difficulty,
        mode=style_key,
        questions=questions,
        answers=[],
        started_at=datetime.utcnow(),
    )
    S.set_val(S.INTERVIEW_SESSION, new_session)
    S.set_val(S.INTERVIEW_STATE, "active")
    S.set_val(S.ACTIVE_QUESTION_IDX, 0)
    S.set_val(S.INTERVIEW_ANSWERS, [])
    st.rerun()


def _render_active_interview(mode: str):
    session: InterviewSession | None = S.get(S.INTERVIEW_SESSION)
    if not session or not session.questions:
        S.set_val(S.INTERVIEW_STATE, "idle")
        st.rerun()
        return

    curr_idx = S.get(S.ACTIVE_QUESTION_IDX) or 0
    questions = session.questions
    answers: list[InterviewAnswer] = S.get(S.INTERVIEW_ANSWERS) or []

    # Check if finished
    if curr_idx >= len(questions):
        _finalize_session(session, answers, mode)
        return

    current_q = questions[curr_idx]
    total_q = len(questions)

    # Progress header
    st.progress((curr_idx) / total_q, text=f"Question {curr_idx + 1} of {total_q} • Mode: {session.mode.capitalize()}")

    # Display feedback for the previous question if in Coaching mode
    if session.mode == "coaching" and answers and len(answers) == curr_idx:
        prev_ans = answers[-1]
        _display_coaching_card(prev_ans)

    # Interviewer Card
    diff_pill = {"easy": "🟢 Easy", "medium": "🟡 Medium", "hard": "🔴 Hard"}.get(current_q.difficulty, current_q.difficulty)
    C.card_start(f"Interviewer: Question {curr_idx + 1}")
    st.caption(f"Category: **{current_q.category}** • Topic: *{current_q.topic}* • Difficulty: {diff_pill}")
    st.markdown(f"### \"{current_q.question_text}\"")
    C.card_end()

    # In simulation mode, do NOT reveal expected points during the active interview!
    if session.mode == "coaching":
        st.caption("💡 Coaching tip: Structure your answer logically with context, action, and results.")

    # Answer input form
    with st.form(f"answer_submission_form_{curr_idx}"):
        candidate_response = st.text_area(
            "Your Response:",
            height=160,
            placeholder="Type your answer thoroughly. Use technical specifics and trade-offs where applicable...",
            key=f"candidate_ans_input_{curr_idx}",
        )

        col_sub, col_end = st.columns([2, 1])
        with col_sub:
            submitted = st.form_submit_button("Submit Answer & Proceed →", type="primary", use_container_width=True)
        with col_end:
            early_exit = st.form_submit_button("End Interview Early", use_container_width=True)

    if submitted:
        if not candidate_response.strip():
            st.warning("Please type an answer before submitting.")
        else:
            _submit_candidate_answer(session, current_q, candidate_response, answers, curr_idx, mode)

    elif early_exit:
        if answers:
            _finalize_session(session, answers, mode)
        else:
            S.set_val(S.INTERVIEW_STATE, "idle")
            st.rerun()


def _submit_candidate_answer(
    session: InterviewSession,
    q: Question,
    ans_text: str,
    answers: list[InterviewAnswer],
    idx: int,
    mode: str,
):
    if mode == "demo":
        # Scripted demo response
        demo_ans_match = DEMO_INTERVIEW_ANSWERS[idx] if idx < len(DEMO_INTERVIEW_ANSWERS) else None
        if demo_ans_match:
            ans_obj = demo_ans_match.model_copy(deep=True)
            ans_obj.answer_text = ans_text
        else:
            ans_obj = InterviewAnswer(
                question_number=q.number,
                question_text=q.question_text,
                answer_text=ans_text,
                correctness=7.5,
                clarity=8.0,
                depth=7.0,
                overall_score=7.5,
                covered_points=q.key_points[:2],
                missed_points=q.key_points[2:],
                feedback="Clear structure with sound foundational logic. Elaborate more on performance trade-offs.",
            )
    else:
        from ui.adapters import evaluate_answer
        with st.spinner("AI evaluating answer against rubric (Correctness, Clarity, Depth)..."):
            ans_obj, err = evaluate_answer(q, ans_text)
        if ans_obj is None:
            ans_obj = InterviewAnswer(
                question_number=q.number,
                question_text=q.question_text,
                answer_text=ans_text,
                correctness=0.0,
                clarity=0.0,
                depth=0.0,
                overall_score=0.0,
                feedback=f"AI evaluation service was temporarily unavailable: {err}",
            )

    new_answers = list(answers) + [ans_obj]
    S.set_val(S.INTERVIEW_ANSWERS, new_answers)
    S.set_val(S.ACTIVE_QUESTION_IDX, idx + 1)
    st.rerun()


def _display_coaching_card(ans: InterviewAnswer):
    C.card_start("Coaching Feedback on Previous Response")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Overall Score", f"{ans.overall_score:.1f} / 10")
    with col2:
        st.metric("Correctness (50%)", f"{ans.correctness:.1f} / 10")
    with col3:
        st.metric("Clarity (25%)", f"{ans.clarity:.1f} / 10")
    with col4:
        st.metric("Depth (25%)", f"{ans.depth:.1f} / 10")

    if ans.feedback:
        st.info(f"**Coach's Note:** {ans.feedback}")

    if ans.covered_points:
        st.markdown("**Points You Covered Well:**")
        for cp in ans.covered_points:
            st.markdown(f"- ✅ {cp}")

    if ans.missed_points:
        st.markdown("**Key Nuances to Emphasize Next Time:**")
        for mp in ans.missed_points:
            st.markdown(f"- ⚠️ {mp}")

    C.card_end()


def _finalize_session(session: InterviewSession, answers: list[InterviewAnswer], mode: str):
    from ui.adapters import build_interview_summary

    session.answers = answers
    session.completed = True
    session.completed_at = datetime.utcnow()

    if answers:
        session.avg_score = round(sum(a.overall_score for a in answers) / len(answers), 2)
    else:
        session.avg_score = 0.0

    summary = build_interview_summary(session)
    session.category_scores = summary.get("category_scores", {})
    session.weak_topics = summary.get("weak_topics", [])
    session.strengths = summary.get("strengths", [])
    session.practice_plan = summary.get("practice_plan", [])

    S.set_val(S.INTERVIEW_SESSION, session)
    S.set_val(S.INTERVIEW_STATE, "completed")
    st.rerun()


def _render_completed_summary(mode: str):
    session: InterviewSession | None = S.get(S.INTERVIEW_SESSION)
    if not session:
        S.set_val(S.INTERVIEW_STATE, "idle")
        st.rerun()
        return

    st.success(f"🎉 Interview session concluded! Average Candidate Score: **{session.avg_score:.1f} / 10**")

    # Score breakdown
    col_c, col_w = st.columns([1, 1])

    with col_c:
        if session.category_scores:
            fig_cat = A.category_scores_bar(session.category_scores)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            C.metric_badge("Average Performance", f"{session.avg_score:.1f} / 10", "Across all evaluated questions", "accent")

    with col_w:
        if session.strengths:
            st.markdown("**Key Strengths Demonstrated:**")
            for strg in session.strengths:
                st.markdown(f"- 🌟 {strg}")

        if session.weak_topics:
            st.markdown("**Recommended Topics to Review:**")
            for wt in session.weak_topics:
                st.markdown(f"- ⚠️ {wt}")

        if session.practice_plan:
            st.markdown("**Actionable Next Steps:**")
            for plan_step in session.practice_plan:
                st.markdown(f"- 📌 {plan_step}")

    # Full answer transcript expander
    st.markdown('<div class="section-h">Question-by-Question Detailed Review</div>', unsafe_allow_html=True)
    for idx, (q, a) in enumerate(zip(session.questions, session.answers)):
        with st.expander(f"Q{idx + 1}: {q.question_text[:70]}... — Score: {a.overall_score:.1f}/10"):
            st.markdown(f"**Question:** {q.question_text}")
            st.markdown(f"**Your Answer:** {a.answer_text}")
            st.markdown(f"**Evaluation Feedback:** {a.feedback}")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Correctness", f"{a.correctness:.1f}/10")
            with c2:
                st.metric("Clarity", f"{a.clarity:.1f}/10")
            with c3:
                st.metric("Depth", f"{a.depth:.1f}/10")

            if a.missed_points:
                st.markdown("**Recommended talking points:**")
                for mp in a.missed_points:
                    st.markdown(f"- 💡 {mp}")

    # Actions
    st.markdown('<div class="section-h">Persistence & Reset</div>', unsafe_allow_html=True)
    col_s, col_r = st.columns(2)

    with col_s:
        if mode == "live":
            if st.button("💾 Save Interview Results Locally", key="btn_save_iv_db", use_container_width=True):
                from ui.adapters import save_interview, build_interview_summary
                summary = build_interview_summary(session)
                save_interview(session, summary, origin="live")
                st.success("✅ Interview session record saved to local database.")
        else:
            st.caption("🔒 Save disabled in Demo Mode.")

    with col_r:
        if st.button("🔄 Start New Interview Session", key="btn_reset_iv", use_container_width=True):
            S.set_val(S.INTERVIEW_STATE, "idle")
            S.set_val(S.INTERVIEW_SESSION, None)
            S.set_val(S.INTERVIEW_ANSWERS, [])
            S.set_val(S.ACTIVE_QUESTION_IDX, 0)
            st.rerun()
