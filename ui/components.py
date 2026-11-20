"""
ui/components.py — Reusable UI presentation components for PrepLio.
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


def card_start(title: Optional[str] = None):
    """Render the opening of a polished UI card."""
    header_html = f'<div style="font-weight:600;font-size:1.05rem;color:{T.COLORS["primary_text"]};margin-bottom:0.5rem;">{escape_text(title)}</div>' if title else ""
    st.markdown(f'<div class="pp-card">{header_html}', unsafe_allow_html=True)


def card_end():
    """Render the closing of a polished UI card."""
    st.markdown('</div>', unsafe_allow_html=True)


def metric_badge(label: str, value: str, subtext: Optional[str] = None, badge_type: str = "normal"):
    """Render a clean metric display block."""
    color_map = {
        "success": T.COLORS["success"],
        "warning": T.COLORS["warning"],
        "error": T.COLORS["error"],
        "accent": T.COLORS["accent"],
        "normal": T.COLORS["primary_text"],
    }
    col = color_map.get(badge_type, T.COLORS["primary_text"])
    sub_html = f'<div style="font-size:0.75rem;color:{T.COLORS["secondary_text"]};">{escape_text(subtext)}</div>' if subtext else ""
    st.markdown(
        f"""
        <div style="background:{T.COLORS['surface']};border:1px solid {T.COLORS['border']};border-radius:8px;padding:0.75rem 1rem;text-align:center;">
            <div style="font-size:0.8rem;font-weight:600;text-transform:uppercase;color:{T.COLORS['secondary_text']};letter-spacing:0.05em;">{escape_text(label)}</div>
            <div style="font-size:1.6rem;font-weight:700;color:{col};margin:0.25rem 0;">{escape_text(value)}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def priority_pill(severity: str, section: str, action: str):
    """Render a priority fix item safely."""
    sev = severity.lower()
    icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(sev, "⚪")
    color = {"high": T.COLORS["error"], "medium": T.COLORS["warning"], "low": T.COLORS["success"]}.get(sev, T.COLORS["muted"])
    
    st.markdown(
        f"""
        <div style="border-left: 4px solid {color}; background:{T.COLORS['surface']}; border-top:1px solid {T.COLORS['border']}; border-right:1px solid {T.COLORS['border']}; border-bottom:1px solid {T.COLORS['border']}; border-radius:6px; padding:0.6rem 0.9rem; margin-bottom:0.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">
                <span style="font-weight:700; font-size:0.85rem; color:{color};">{icon} {escape_text(severity.upper())}</span>
                <span style="font-size:0.8rem; background:{T.COLORS['bg']}; color:{T.COLORS['secondary_text']}; padding:0.15rem 0.5rem; border-radius:4px; font-weight:500;">{escape_text(section)}</span>
            </div>
            <div style="color:{T.COLORS['primary_text']}; font-size:0.9rem;">{escape_text(action)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def skill_badge(skill: str, matched: bool, evidence: str = "not_found"):
    """Render a skill badge with evidence indicator."""
    if matched:
        icon_map = {"exact": "🎯", "alias": "🔄", "fuzzy": "≈"}
        icon = icon_map.get(evidence, "✓")
        bg = "#DCFCE7"
        text_color = T.COLORS["success"]
        border = "#86EFAC"
    else:
        icon = "✕"
        bg = "#FEE2E2"
        text_color = T.COLORS["error"]
        border = "#FCA5A5"
    
    st.markdown(
        f"""
        <span style="display:inline-flex;align-items:center;background:{bg};color:{text_color};border:1px solid {border};border-radius:14px;padding:0.2rem 0.6rem;font-size:0.82rem;font-weight:600;margin:0.2rem 0.2rem;">
            <span style="margin-right:0.3rem;">{icon}</span>{escape_text(skill)}
        </span>
        """,
        unsafe_allow_html=True,
    )
