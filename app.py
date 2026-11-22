"""
app.py — PrepLio Placement Preparation Assistant.
Main entry point, application shell, sidebar controls, and navigation.
"""
from __future__ import annotations

import time
import streamlit as st

import ui.state as S
import ui.theme as T
from ui.adapters import get_ollama_status

# Configure page layout
st.set_page_config(
    page_title="Placement Preparation Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply unified design system
T.inject_css()

# Initialize centralized session state
S.init_state()


def main():
    _render_sidebar()

    # Main header
    st.title("🎓 Placement Preparation Assistant")

    is_logged_in = S.get(S.IS_LOGGED_IN, False)

    # 1. Dedicated Login Console if not authenticated
    if not is_logged_in:
        from ui.components import render_login_console
        render_login_console()
        return

    # 2. Authenticated Consoles Workspace
    curr_role = S.get(S.SELECTED_ROLE) or "Software Developer"
    curr_mode = S.get(S.APP_MODE) or "demo"
    ollama_stat = S.get(S.OLLAMA_STATUS) or {}
    ollama_ready = bool(ollama_stat.get("model_ready", False))

    from ui.components import render_hero_banner, render_profile_badge
    render_hero_banner(curr_role, curr_mode, ollama_ready)
    render_profile_badge()

    # Top navigation tabs for preparation consoles
    tabs = st.tabs([
        "📄 Resume Review",
        "🎯 Skill Gap",
        "💡 Questions",
        "🎙️ Mock Interview",
        "📈 Progress & Analytics",
    ])

    from ui.resume_tab import render as r_resume
    from ui.gap_tab import render as r_gap
    from ui.questions_tab import render as r_questions
    from ui.interview_tab import render as r_interview
    from ui.progress_tab import render as r_progress

    for tab, render_fn in zip(tabs, (r_resume, r_gap, r_questions, r_interview, r_progress)):
        with tab:
            render_fn()


def _render_sidebar():
    with st.sidebar:
        st.markdown("### 🎓 PrepLio")
        st.caption("Local Career Readiness Assistant")

        is_logged_in = S.get(S.IS_LOGGED_IN, False)
        if is_logged_in:
            user_name = S.get(S.USER_NAME) or "Candidate"
            user_tag = S.get(S.USER_IDENTIFIER) or "Active"
            st.markdown(f"👤 **{user_name}** `({user_tag})`")
            if st.button("🚪 Logout / Switch", key="sidebar_logout_btn", use_container_width=True):
                S.set_val(S.IS_LOGGED_IN, False)
                S.set_val(S.USER_IDENTIFIER, "")
                S.clear_session()
                st.rerun()
        else:
            st.caption("🔒 *Candidate Portal — Sign In Below*")
        st.divider()

        # Target Role Selector
        roles_list = [
            "Software Developer",
            "Data Scientist",
            "Frontend Developer",
            "DevOps Engineer",
        ]
        curr_role = S.get(S.SELECTED_ROLE) or "Software Developer"
        role_idx = roles_list.index(curr_role) if curr_role in roles_list else 0
        new_role = st.selectbox("Target Role", roles_list, index=role_idx, key="sidebar_role_select")
        if new_role != curr_role:
            S.on_role_change(new_role)

        # Mode Selection
        curr_mode = S.get(S.APP_MODE) or "demo"
        mode_idx = 0 if curr_mode == "live" else 1
        new_mode_choice = st.radio(
            "Operating Mode",
            ["Live Mode (Local Ollama)", "Demo Mode (Offline Fixtures)"],
            index=mode_idx,
            key="sidebar_mode_select",
        )
        selected_mode = "live" if "Live" in new_mode_choice else "demo"
        if selected_mode != curr_mode:
            S.set_val(S.APP_MODE, selected_mode)
            st.rerun()

        # Model and Ollama Health Indicator (cached check)
        st.markdown("**Local AI Engine**")
        st.caption("Model: `qwen3:4b` via local Ollama")

        _render_ollama_status()

        # Deep Review Toggle
        curr_deep = S.get(S.DEEP_REVIEW)
        new_deep = st.toggle(
            "Deep Review Pass",
            value=curr_deep,
            key="sidebar_deep_toggle",
            help="Adds extra review passes and may take substantially longer.",
        )
        if new_deep != curr_deep:
            S.set_val(S.DEEP_REVIEW, new_deep)

        st.divider()

        # Privacy Notice
        st.markdown("**🔒 Privacy & Data Policy**")
        st.caption(
            "100% Local processing. Resumes and answers are kept in memory and never transmitted to cloud servers. "
            "Data is saved to local SQLite only on your explicit request."
        )

        # Session and Storage Management
        col_clear, col_del = st.columns(2)
        with col_clear:
            if st.button("Clear Session", key="btn_clear_sess", use_container_width=True):
                S.clear_session()
                st.rerun()

        with col_del:
            if st.button("Delete Data", key="btn_delete_db", use_container_width=True):
                st.session_state["show_confirm_delete"] = True

        if st.session_state.get("show_confirm_delete"):
            st.warning("⚠️ Delete all saved local records?")
            c_yes, c_no = st.columns(2)
            with c_yes:
                if st.button("Confirm", type="primary", key="btn_confirm_del"):
                    from core.db import delete_all_data
                    delete_all_data()
                    st.session_state["show_confirm_delete"] = False
                    st.success("All local records deleted.")
                    st.rerun()
            with c_no:
                if st.button("Cancel", key="btn_cancel_del"):
                    st.session_state["show_confirm_delete"] = False
                    st.rerun()


def _render_ollama_status():
    """Render bounded health check status for Ollama with rate-limiting."""
    now = time.time()
    last_check = S.get(S.OLLAMA_CHECKED_AT)
    status = S.get(S.OLLAMA_STATUS)

    # Check only if not checked or older than 60 seconds
    if not status or not last_check or (now - last_check > 60):
        status = get_ollama_status()
        S.set_val(S.OLLAMA_STATUS, status)
        S.set_val(S.OLLAMA_CHECKED_AT, now)

    if status.get("model_ready"):
        st.success(f"🟢 {status.get('message', 'Ready')}")
    elif status.get("available"):
        st.warning(f"🟡 {status.get('message', 'Model not ready')}")
    else:
        st.error("🔴 Ollama Offline")
        st.caption("Start Ollama locally: `ollama serve`")


if __name__ == "__main__":
    main()
