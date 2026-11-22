"""
ui/components.py — Reusable 3D animated UI presentation components for PrepLio.
All untrusted text is safely escaped or passed to native Streamlit controls.
"""
from __future__ import annotations

import html
from typing import Optional
import streamlit as st
import ui.theme as T


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
    """Render a 3D animated hero showcase banner."""
    mode_color = "#10B981" if mode == "live" else "#F59E0B"
    mode_text = "Live Mode" if mode == "live" else "Demo Mode"
    status_icon = "🟢" if ollama_ready else "🟡"
    status_text = "Qwen3:4b Active" if ollama_ready else "Offline Fallback"

    st.markdown(
        f"""
        <div class="hero-3d-wrapper">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
                <div>
                    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">
                        <span style="font-size:1.8rem; filter:drop-shadow(0 4px 8px rgba(79,70,229,0.3));">🎓</span>
                        <span style="font-size:0.85rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:#4F46E5;">
                            Placement Preparation Assistant
                        </span>
                        <span class="chip-3d" style="background:#EEF2FF; border-color:#C7D2FE; color:#4338CA; font-size:0.75rem;">
                            v2.0 Pro 3D
                        </span>
                    </div>
                    <div class="hero-title-gradient">PrepLio Career Intelligence</div>
                    <div style="color:{T.COLORS['secondary_text']}; font-size:0.95rem; max-width:680px; line-height:1.5;">
                        Targeting <b>{escape_text(target_role)}</b> with deterministic heuristics, RapidFuzz benchmark matching, and local AI mock interview evaluation.
                    </div>
                </div>
                <div style="display:flex; flex-direction:column; gap:0.4rem; align-items:flex-end;">
                    <div class="chip-3d" style="background:rgba(255,255,255,0.9); border-color:#E2E8F0;">
                        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:{mode_color}; margin-right:6px; animation: liveDotGlow 2s infinite;"></span>
                        <span>{escape_text(mode_text)}</span>
                    </div>
                    <div class="chip-3d" style="background:rgba(255,255,255,0.9); border-color:#E2E8F0; font-size:0.75rem;">
                        <span>{status_icon} {escape_text(status_text)}</span>
                    </div>
                    <div style="font-size:0.75rem; color:{T.COLORS['muted']}; margin-top:0.2rem;">
                        🔒 100% Local In-Memory Privacy
                    </div>
                </div>
            </div>
            
            <div style="display:flex; gap:0.5rem; margin-top:1.25rem; flex-wrap:wrap;">
                <span class="chip-3d" style="border-left:3px solid #4F46E5;">📋 85-pt Rule Heuristics</span>
                <span class="chip-3d" style="border-left:3px solid #10B981;">🎯 RapidFuzz Benchmark</span>
                <span class="chip-3d" style="border-left:3px solid #8B5CF6;">🎙️ STAR Interview Coach</span>
                <span class="chip-3d" style="border-left:3px solid #F59E0B;">📈 Trajectory Analytics</span>
                <span class="chip-3d" style="border-left:3px solid #06B6D4;">📄 ReportLab PDF Export</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
