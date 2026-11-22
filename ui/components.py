"""
ui/components.py — Reusable 3D animated UI presentation components for PrepLio.
All untrusted text is safely escaped or passed to native Streamlit controls.
"""
from __future__ import annotations

import html
from typing import Optional
import streamlit as st
import ui.theme as T
import ui.state as S


def escape_text(text: str) -> str:
    """Safely escape text for HTML display."""
    return html.escape(str(text))


def card_start(title: Optional[str] = None, badge: Optional[str] = None):
    """Render the opening of a 3D elevated UI card."""
    header_html = ""
    if title or badge:
        b_html = f'<span class="chip-3d" style="font-size:0.75rem;padding:0.15rem 0.6rem;">{escape_text(badge)}</span>' if badge else ""
        header_html = f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.85rem; border-bottom:1px solid rgba(226,232,240,0.6); padding-bottom:0.5rem;">
            <div style="font-weight:700; font-size:1.1rem; color:{T.COLORS['primary_text']}; letter-spacing:-0.02em;">{escape_text(title)}</div>
            {b_html}
        </div>
        """
    st.markdown(f'<div class="pp-card">{header_html}', unsafe_allow_html=True)


def card_end():
    """Render the closing of a 3D elevated UI card."""
    st.markdown('</div>', unsafe_allow_html=True)


def render_hero_banner(target_role: str, mode: str, ollama_ready: bool):
    """Render a clean, responsive 3D animated hero showcase banner."""
    mode_color = "#10B981" if mode == "live" else "#F59E0B"
    mode_text = "Live Mode" if mode == "live" else "Demo Mode"
    status_icon = "🟢" if ollama_ready else "🟡"
    status_text = "Qwen3:4b Active" if ollama_ready else "Offline Fallback"

    user_name = S.get(S.USER_NAME) or "Candidate"
    is_logged_in = S.get(S.IS_LOGGED_IN)
    user_identifier = S.get(S.USER_IDENTIFIER) or ""

    user_pill = ""
    if is_logged_in and user_identifier:
        user_pill = f"""
        <div class="chip-3d" style="background:#F0FDF4; border-color:#86EFAC; color:#15803D; font-size:0.78rem;">
            👤 <b>{escape_text(user_name)}</b> ({escape_text(user_identifier)})
        </div>
        """

    banner_html = f"""
<div class="hero-3d-wrapper">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
        <div>
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.35rem;">
                <span style="font-size:1.75rem; filter:drop-shadow(0 4px 8px rgba(79,70,229,0.3));">🎓</span>
                <span style="font-size:0.85rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#4F46E5;">
                    Placement Preparation Assistant
                </span>
                <span class="chip-3d" style="background:#EEF2FF; border-color:#C7D2FE; color:#4338CA; font-size:0.75rem;">
                    Pro 3D
                </span>
            </div>
            <div class="hero-title-gradient">PrepLio Career Intelligence</div>
            <div style="color:{T.COLORS['secondary_text']}; font-size:0.95rem; max-width:680px; line-height:1.5;">
                Targeting <b>{escape_text(target_role)}</b> with deterministic heuristics, RapidFuzz benchmark matching, and local AI mock interview evaluation.
            </div>
        </div>
        <div style="display:flex; flex-direction:column; gap:0.4rem; align-items:flex-end;">
            {user_pill}
            <div class="chip-3d" style="background:rgba(255,255,255,0.9); border-color:#E2E8F0;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:{mode_color}; margin-right:6px; animation: liveDotGlow 2s infinite;"></span>
                <span>{escape_text(mode_text)}</span>
            </div>
            <div class="chip-3d" style="background:rgba(255,255,255,0.9); border-color:#E2E8F0; font-size:0.75rem;">
                <span>{status_icon} {escape_text(status_text)}</span>
            </div>
            <div style="font-size:0.75rem; color:{T.COLORS['muted']}; margin-top:0.15rem;">
                🔒 100% Local In-Memory Privacy
            </div>
        </div>
    </div>
</div>
"""
    st.markdown(banner_html, unsafe_allow_html=True)


def render_profile_widget():
    """Render the Candidate Login & Profile management widget."""
    is_logged_in = S.get(S.IS_LOGGED_IN)
    user_name = S.get(S.USER_NAME) or "Candidate"
    user_identifier = S.get(S.USER_IDENTIFIER) or ""
    user_education = S.get(S.USER_EDUCATION) or "B.Tech Computer Science"
    user_status = S.get(S.USER_STATUS) or "Actively Preparing"
    curr_role = S.get(S.SELECTED_ROLE) or "Software Developer"

    if is_logged_in:
        # Display Active 3D Profile Card
        profile_card_html = f"""
        <div class="pp-card" style="margin-bottom:1rem; border-left:4px solid #4F46E5; background:linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(245,247,255,0.9) 100%);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.75rem;">
                <div style="display:flex; align-items:center; gap:0.85rem;">
                    <div style="width:48px; height:48px; border-radius:50%; background:linear-gradient(135deg, #4F46E5, #7C3AED); color:#fff; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1.2rem; box-shadow:0 4px 10px rgba(79,70,229,0.3);">
                        {escape_text(user_name[:2].upper())}
                    </div>
                    <div>
                        <div style="font-weight:700; font-size:1.05rem; color:#0F172A; display:flex; align-items:center; gap:0.5rem;">
                            <span>{escape_text(user_name)}</span>
                            <span class="chip-3d" style="font-size:0.7rem; padding:0.1rem 0.5rem; background:#DCFCE7; color:#15803D; border-color:#86EFAC;">Active Profile</span>
                        </div>
                        <div style="font-size:0.82rem; color:#64748B;">
                            📱/✉️ <b>{escape_text(user_identifier)}</b> • 🎓 {escape_text(user_education)}
                        </div>
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:0.5rem;">
                    <span class="chip-3d" style="font-size:0.75rem;">🎯 {escape_text(curr_role)}</span>
                    <span class="chip-3d" style="font-size:0.75rem; border-left:3px solid #10B981;">🚀 {escape_text(user_status)}</span>
                </div>
            </div>
        </div>
        """
        st.markdown(profile_card_html, unsafe_allow_html=True)

        with st.expander("⚙️ Edit Profile Details / Switch Account", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full Name", value=user_name, key="edit_prof_name")
                new_edu = st.text_input("Education / University", value=user_education, key="edit_prof_edu")
            with col2:
                new_status = st.selectbox(
                    "Placement Status",
                    ["Actively Applying", "Mock Interview Practice", "Skill Assessment", "Beginner"],
                    index=["Actively Applying", "Mock Interview Practice", "Skill Assessment", "Beginner"].index(user_status)
                    if user_status in ["Actively Applying", "Mock Interview Practice", "Skill Assessment", "Beginner"]
                    else 0,
                    key="edit_prof_status",
                )
                new_role = st.selectbox(
                    "Target Role",
                    ["Software Developer", "Data Scientist", "Frontend Developer", "DevOps Engineer"],
                    index=["Software Developer", "Data Scientist", "Frontend Developer", "DevOps Engineer"].index(curr_role)
                    if curr_role in ["Software Developer", "Data Scientist", "Frontend Developer", "DevOps Engineer"]
                    else 0,
                    key="edit_prof_role",
                )

            col_save, col_logout = st.columns([2, 1])
            with col_save:
                if st.button("💾 Update Profile", key="btn_update_profile", use_container_width=True):
                    try:
                        from core.db import update_user_profile
                        update_user_profile(S.get(S.USER_ID), new_name, new_role, new_edu, new_status)
                    except Exception:
                        pass
                    S.set_val(S.USER_NAME, new_name)
                    S.set_val(S.USER_EDUCATION, new_edu)
                    S.set_val(S.USER_STATUS, new_status)
                    if new_role != curr_role:
                        S.on_role_change(new_role)
                    st.success("Profile updated successfully!")
                    st.rerun()

            with col_logout:
                if st.button("🚪 Logout / Switch", key="btn_logout_profile", use_container_width=True):
                    S.set_val(S.IS_LOGGED_IN, False)
                    S.set_val(S.USER_IDENTIFIER, "")
                    S.set_val(S.USER_NAME, "Candidate")
                    st.rerun()

    else:
        # Display Candidate Login & Profile Creation Card
        card_start("Candidate Login & Profile Setup", "Sign In")
        st.caption("Enter with your **Mobile Number** or **Email** to personalize your placement readiness tracking.")

        with st.form("candidate_login_form"):
            col1, col2 = st.columns(2)
            with col1:
                identifier_input = st.text_input(
                    "Mobile Number or Email *",
                    placeholder="+91 9876543210 or yourname@gmail.com",
                    key="login_identifier_input",
                )
                name_input = st.text_input(
                    "Candidate Full Name",
                    placeholder="e.g. Rahul Sharma",
                    key="login_name_input",
                )
            with col2:
                edu_input = st.text_input(
                    "Degree & College",
                    placeholder="e.g. B.Tech Computer Science (2025)",
                    key="login_edu_input",
                )
                role_input = st.selectbox(
                    "Target Placement Role",
                    ["Software Developer", "Data Scientist", "Frontend Developer", "DevOps Engineer"],
                    index=["Software Developer", "Data Scientist", "Frontend Developer", "DevOps Engineer"].index(curr_role)
                    if curr_role in ["Software Developer", "Data Scientist", "Frontend Developer", "DevOps Engineer"]
                    else 0,
                    key="login_role_input",
                )

            col_submit, col_demo_btn = st.columns([2, 1])
            with col_submit:
                submitted = st.form_submit_button("🚀 Sign In & Enter Dashboard", type="primary", use_container_width=True)
            with col_demo_btn:
                demo_login = st.form_submit_button("⚡ Quick Demo Profile", use_container_width=True)

        if submitted:
            if not identifier_input.strip():
                st.warning("Please provide your mobile number or email to proceed.")
            else:
                try:
                    from core.db import init_db, get_or_create_user
                    init_db()
                    user = get_or_create_user(
                        identifier=identifier_input.strip(),
                        name=name_input.strip(),
                        role=role_input,
                        education=edu_input.strip() or "Undergraduate",
                        status="Actively Preparing",
                    )
                    S.set_val(S.USER_ID, user.get("id", 1))
                    S.set_val(S.USER_IDENTIFIER, user.get("identifier", identifier_input.strip()))
                    S.set_val(S.USER_NAME, user.get("name", name_input.strip() or "Candidate"))
                    S.set_val(S.USER_EDUCATION, user.get("education", edu_input.strip() or "Undergraduate"))
                    S.set_val(S.USER_STATUS, user.get("status", "Actively Preparing"))
                    S.set_val(S.IS_LOGGED_IN, True)
                    if role_input != curr_role:
                        S.on_role_change(role_input)
                    st.success(f"Welcome, {S.get(S.USER_NAME)}! Profile activated.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to initialize profile: {e}")

        elif demo_login:
            S.set_val(S.USER_ID, 1)
            S.set_val(S.USER_IDENTIFIER, "alex.candidate@demo.io")
            S.set_val(S.USER_NAME, "Alex Johnson")
            S.set_val(S.USER_EDUCATION, "B.Tech Computer Science")
            S.set_val(S.USER_STATUS, "Actively Preparing")
            S.set_val(S.IS_LOGGED_IN, True)
            st.success("Demo profile activated.")
            st.rerun()

        card_end()


def metric_badge(label: str, value: str, subtext: Optional[str] = None, badge_type: str = "normal"):
    """Render a 3D elevated metric tile with ambient gradient top border."""
    color_map = {
        "success": ("#10B981", "#D1FAE5"),
        "warning": ("#F59E0B", "#FEF3C7"),
        "error": ("#EF4444", "#FEE2E2"),
        "accent": ("#4F46E5", "#EEF2FF"),
        "normal": ("#0F172A", "#F1F5F9"),
    }
    col, bg_accent = color_map.get(badge_type, color_map["normal"])
    sub_html = f'<div style="font-size:0.75rem; font-weight:500; color:{T.COLORS["secondary_text"]}; margin-top:0.2rem;">{escape_text(subtext)}</div>' if subtext else ""

    st.markdown(
        f"""
        <div class="metric-3d" style="border-top:3px solid {col};">
            <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:{T.COLORS['secondary_text']}; letter-spacing:0.06em;">
                {escape_text(label)}
            </div>
            <div style="font-size:1.85rem; font-weight:800; color:{col}; margin:0.25rem 0; letter-spacing:-0.03em;">
                {escape_text(value)}
            </div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def priority_pill(severity: str, section: str, action: str):
    """Render a 3D prioritized fix card with ambient side glow."""
    sev = severity.lower()
    icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(sev, "⚪")
    color = {"high": "#EF4444", "medium": "#F59E0B", "low": "#10B981"}.get(sev, T.COLORS["muted"])
    bg_pill = {"high": "#FEF2F2", "medium": "#FFFBEB", "low": "#ECFDF5"}.get(sev, "#F8FAFC")

    st.markdown(
        f"""
        <div class="priority-3d-box" style="border-left: 4px solid {color};">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;">
                <span style="font-weight:700; font-size:0.82rem; color:{color}; display:inline-flex; align-items:center; gap:0.3rem;">
                    <span>{icon}</span> {escape_text(severity.upper())} PRIORITY
                </span>
                <span class="chip-3d" style="font-size:0.72rem; padding:0.1rem 0.5rem; background:{bg_pill}; border-color:{color}; color:{color};">
                    {escape_text(section)}
                </span>
            </div>
            <div style="color:{T.COLORS['primary_text']}; font-size:0.92rem; font-weight:500; line-height:1.45;">
                {escape_text(action)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def skill_badge(skill: str, matched: bool, evidence: str = "not_found"):
    """Render a 3D tactile skill badge with evidence indicator."""
    if matched:
        icon_map = {"exact": "🎯", "alias": "🔄", "fuzzy": "≈"}
        icon = icon_map.get(evidence, "✓")
        bg = "#ECFDF5"
        text_color = "#047857"
        border = "#A7F3D0"
        shadow = "rgba(16, 185, 129, 0.15)"
    else:
        icon = "✕"
        bg = "#FEF2F2"
        text_color = "#B91C1C"
        border = "#FECACA"
        shadow = "rgba(239, 68, 68, 0.12)"

    st.markdown(
        f"""
        <span style="display:inline-flex; align-items:center; background:{bg}; color:{text_color}; border:1px solid {border}; border-radius:18px; padding:0.25rem 0.75rem; font-size:0.82rem; font-weight:700; margin:0.25rem 0.2rem; box-shadow:0 2px 6px {shadow}; transition:transform 0.2s ease;">
            <span style="margin-right:0.35rem;">{icon}</span>{escape_text(skill)}
        </span>
        """,
        unsafe_allow_html=True,
    )
