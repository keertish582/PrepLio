"""
ui/progress_tab.py — Screen 5: Progress Tracking & Analytics Dashboard.
Module B5 frontend implementation.
"""
from __future__ import annotations

from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import ui.state as S
import ui.theme as T
import ui.analytics as A
import ui.components as C


def render():
    st.markdown('<div class="section-h">Placement Preparation Progress & History</div>', unsafe_allow_html=True)
    st.markdown("Track your readiness trajectory over time, analyze recurring interview weak topics, and inspect saved evaluation history.")

    mode = S.get(S.APP_MODE)
    if mode == "demo":
        T.demo_banner()
        _render_demo_progress()
        T.footer()
        return

    # Live Mode
    _render_live_progress()
    T.footer()


def _render_live_progress():
    try:
        from core.db import init_db, ats_history, score_history, gap_history, weak_topic_counts, get_latest_review
        init_db()

        # Optional Role Filter
        col_f, _ = st.columns([2, 3])
        with col_f:
            role_filter_options = ["All Roles", "Software Developer", "Data Scientist", "Frontend Developer", "DevOps Engineer"]
            selected_filter = st.selectbox("Filter History by Role:", role_filter_options, index=0)
            role_arg = None if selected_filter == "All Roles" else selected_filter

        ats_records = ats_history(role=role_arg)
        interview_records = score_history(role=role_arg)
        gap_records = gap_history(role=role_arg)
        weak_counts = weak_topic_counts()
        latest_rev = get_latest_review()

        # Empty state check
        if not ats_records and not interview_records and not gap_records:
            st.info("📭 No saved sessions yet. Complete an analysis in any tab and choose **Save locally** to track your preparation progress over time.")
            return

        # Latest Review Snapshot
        if latest_rev:
            st.markdown('<div class="section-h">Latest Saved Review</div>', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                C.metric_badge("Role", latest_rev.get("role", "—"), "Target role", "normal")
            with col2:
                C.metric_badge("Rule Score", f"{latest_rev.get('rule_score', 0):.0f} / 85", "Deterministic checks", "accent")
            with col3:
                final_val = f"{latest_rev['final_score']:.0f} / 100" if (latest_rev.get("final_score") is not None and latest_rev.get("ai_complete")) else "Incomplete"
                badge_style = "success" if latest_rev.get("ai_complete") else "warning"
                C.metric_badge("Final Score", final_val, "AI assessment included" if latest_rev.get("ai_complete") else "AI pending", badge_style)
            with col4:
                date_str = latest_rev.get("reviewed_at", "")[:10]
                C.metric_badge("Saved On", date_str or "Today", "Local persistence", "normal")

        # Visualizations Row 1: Resume Readiness Trend
        if ats_records:
            st.markdown('<div class="section-h">Resume Readiness Trend (0–85 Rule Score & 0–100 Complete Score)</div>', unsafe_allow_html=True)
            fig_trend = A.score_trend_line(ats_records)
            st.plotly_chart(fig_trend, use_container_width=True)

        # Visualizations Row 2: Interview Scores Trend (Separate 0-10 Scale!)
        if interview_records:
            st.markdown('<div class="section-h">Mock Interview Average Score Trend (0–10 Scale)</div>', unsafe_allow_html=True)
            df_iv = pd.DataFrame(interview_records)
            fig_iv = go.Figure()
            fig_iv.add_trace(go.Scatter(
                x=df_iv["started_at"],
                y=df_iv["avg_score"],
                mode="lines+markers",
                name="Interview Score (0–10)",
                line=dict(color=T.COLORS["accent"], width=2.5),
                marker=dict(size=7, color=T.COLORS["accent"]),
                hovertemplate="%{x|%Y-%m-%d}: %{y:.1f}/10<extra></extra>",
            ))
            fig_iv.update_layout(
                paper_bgcolor=T.COLORS["surface"],
                plot_bgcolor=T.COLORS["surface"],
                font=dict(family="system-ui, -apple-system, sans-serif", color=T.COLORS["primary_text"]),
                margin=dict(l=40, r=20, t=30, b=40),
                yaxis=dict(range=[0, 10.5], title="Score (0–10)"),
                xaxis=dict(title="Date"),
                height=300,
            )
            st.plotly_chart(fig_iv, use_container_width=True)

        # Visualizations Row 3: Weak Topics Across Sessions
        if weak_counts:
            st.markdown('<div class="section-h">Recurring Weak Topics (Across All Mock Interviews)</div>', unsafe_allow_html=True)
            fig_weak = A.weak_topics_bar(weak_counts)
            st.plotly_chart(fig_weak, use_container_width=True)

        # Tables History
        with st.expander("📊 View Detailed Saved Records Table", expanded=False):
            tab_r, tab_i, tab_g = st.tabs(["Resume Reviews", "Mock Interviews", "Skill Gap Reports"])
            
            with tab_r:
                if ats_records:
                    df_r = pd.DataFrame(ats_records)[["reviewed_at", "role", "rule_score", "ai_score", "final_score", "ai_complete"]]
                    df_r.columns = ["Date", "Role", "Rule Score (/85)", "AI Score (/15)", "Final (/100)", "AI Complete"]
                    st.dataframe(df_r, use_container_width=True)
                else:
                    st.caption("No resume reviews recorded.")

            with tab_i:
                if interview_records:
                    df_it = pd.DataFrame(interview_records)[["started_at", "role", "difficulty", "avg_score"]]
                    df_it.columns = ["Date", "Role", "Difficulty", "Average Score (/10)"]
                    st.dataframe(df_it, use_container_width=True)
                else:
                    st.caption("No mock interviews recorded.")

            with tab_g:
                if gap_records:
                    df_gp = pd.DataFrame(gap_records)[["generated_at", "role", "match_pct"]]
                    df_gp.columns = ["Date", "Role", "Role Match %"]
                    st.dataframe(df_gp, use_container_width=True)
                else:
                    st.caption("No skill gap reports recorded.")

    except Exception as e:
        st.error(f"❌ Failed to load progress data from database: {e}")


def _render_demo_progress():
    st.info("💡 **Demo Mode History Preview:** Displaying synthetic historical milestones to demonstrate trend tracking.")

    # Synthetic demo data
    base_time = datetime.utcnow() - timedelta(days=20)
    demo_ats = [
        {"reviewed_at": (base_time + timedelta(days=i * 5)).isoformat(),
         "role": "Software Developer",
         "rule_score": 48.0 + (i * 7.5),
         "ai_score": None if i < 2 else 9.0 + (i * 1.5),
         "final_score": None if i < 2 else 62.0 + (i * 9),
         "ai_complete": i >= 2}
        for i in range(5)
    ]
    demo_weak = {
        "System Design": 4,
        "Hash Map Collisions": 3,
        "STAR Behavioral Context": 2,
        "SQL Window Functions": 2,
        "Docker Multi-Stage": 1,
    }

    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        C.metric_badge("Role Tracked", "Software Dev", "Demo synthetic track", "normal")
    with col2:
        C.metric_badge("Latest Rule Score", "78 / 85", "+30 pts improvement", "accent")
    with col3:
        C.metric_badge("Latest Final Score", "89 / 100", "AI assessed", "success")
    with col4:
        C.metric_badge("Sessions Completed", "5 Reviews • 4 Mocks", "Practice milestones", "normal")

    # Score trend
    st.markdown('<div class="section-h">Resume Readiness Milestones (Demo)</div>', unsafe_allow_html=True)
    fig_demo_ats = A.score_trend_line(demo_ats)
    st.plotly_chart(fig_demo_ats, use_container_width=True)

    # Interview trend
    st.markdown('<div class="section-h">Mock Interview Score Trajectory (0–10 Scale Demo)</div>', unsafe_allow_html=True)
    demo_iv_days = ["Nov 01", "Nov 06", "Nov 11", "Nov 16"]
    demo_iv_scores = [5.2, 6.4, 7.1, 8.2]
    fig_demo_iv = go.Figure(go.Scatter(
        x=demo_iv_days,
        y=demo_iv_scores,
        mode="lines+markers",
        name="Interview Score (0–10)",
        line=dict(color=T.COLORS["accent"], width=2.5),
        marker=dict(size=8, color=T.COLORS["accent"]),
        hovertemplate="%{x}: %{y:.1f}/10<extra></extra>",
    ))
    fig_demo_iv.update_layout(
        paper_bgcolor=T.COLORS["surface"],
        plot_bgcolor=T.COLORS["surface"],
        font=dict(family="system-ui, -apple-system, sans-serif", color=T.COLORS["primary_text"]),
        margin=dict(l=40, r=20, t=30, b=40),
        yaxis=dict(range=[0, 10.5], title="Score (0–10)"),
        xaxis=dict(title="Practice Session"),
        height=300,
    )
    st.plotly_chart(fig_demo_iv, use_container_width=True)

    # Weak topics
    st.markdown('<div class="section-h">Frequent Weak Topics in Mock Interviews (Demo)</div>', unsafe_allow_html=True)
    fig_demo_weak = A.weak_topics_bar(demo_weak)
    st.plotly_chart(fig_demo_weak, use_container_width=True)
