"""
ui/theme.py — Design system, color tokens, and 3D animated styling for PrepLio.
"""

COLORS = {
    "bg": "#F6F8FC",
    "surface": "#FFFFFF",
    "surface_glass": "rgba(255, 255, 255, 0.85)",
    "primary_text": "#0F172A",
    "secondary_text": "#475569",
    "accent": "#4F46E5",
    "accent_hover": "#4338CA",
    "accent_light": "rgba(79, 70, 229, 0.08)",
    "accent_glow": "rgba(79, 70, 229, 0.35)",
    "success": "#10B981",
    "success_bg": "#ECFDF5",
    "warning": "#F59E0B",
    "warning_bg": "#FFFBEB",
    "error": "#EF4444",
    "error_bg": "#FEF2F2",
    "border": "#E2E8F0",
    "border_highlight": "rgba(79, 70, 229, 0.25)",
    "muted": "#94A3B8",
}

CSS = """
<style>
/* ── Global Page & Typography ────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.stApp {
    background: radial-gradient(circle at 10% 20%, rgba(238, 242, 255, 0.8) 0%, rgba(246, 248, 252, 1) 70%),
                radial-gradient(circle at 90% 80%, rgba(243, 232, 255, 0.6) 0%, rgba(246, 248, 252, 1) 70%);
    background-attachment: fixed;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── 3D Keyframe Animations ──────────────────────────────────────────────── */
@keyframes float3D {
    0%, 100% {
        transform: translateY(0px) perspective(1000px) rotateX(0deg) rotateY(0deg);
    }
    50% {
        transform: translateY(-8px) perspective(1000px) rotateX(1deg) rotateY(-1deg);
    }
}

@keyframes floatReverse3D {
    0%, 100% {
        transform: translateY(0px) perspective(1000px) rotateX(0deg);
    }
    50% {
        transform: translateY(6px) perspective(1000px) rotateX(-1deg);
    }
}

@keyframes pulseNeon {
    0%, 100% {
        box-shadow: 0 0 15px rgba(79, 70, 229, 0.25), 0 0 30px rgba(79, 70, 229, 0.1);
    }
    50% {
        box-shadow: 0 0 25px rgba(99, 102, 241, 0.45), 0 0 50px rgba(99, 102, 241, 0.2);
    }
}

@keyframes liveDotGlow {
    0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    70% {
        transform: scale(1);
        box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
    }
    100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes shimmerEffect {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* ── 3D Card Architecture ────────────────────────────────────────────────── */
.pp-card {
    position: relative;
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 16px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03),
                0 10px 20px -3px rgba(79, 70, 229, 0.05),
                inset 0 1px 0 rgba(255, 255, 255, 0.95);
    transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1),
                box-shadow 0.35s cubic-bezier(0.16, 1, 0.3, 1),
                border-color 0.35s ease;
    transform-style: preserve-3d;
}

.pp-card:hover {
    transform: translateY(-4px) perspective(1000px) rotateX(1deg);
    box-shadow: 0 16px 32px -6px rgba(79, 70, 229, 0.12),
                0 8px 16px -4px rgba(0, 0, 0, 0.04),
                inset 0 1px 0 rgba(255, 255, 255, 1);
    border-color: rgba(99, 102, 241, 0.35);
}

/* ── 3D Metric Tile ──────────────────────────────────────────────────────── */
.metric-3d {
    position: relative;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.9) 100%);
    backdrop-filter: blur(12px);
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 1rem 1.25rem;
    text-align: center;
    box-shadow: 0 4px 10px -2px rgba(0, 0, 0, 0.03),
                0 8px 16px -4px rgba(79, 70, 229, 0.04),
                inset 0 1px 0 rgba(255, 255, 255, 1);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.metric-3d:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 12px 24px -4px rgba(79, 70, 229, 0.14),
                0 4px 8px -2px rgba(0, 0, 0, 0.04);
    border-color: rgba(79, 70, 229, 0.3);
}

/* ── 3D Priority Fix Pill ────────────────────────────────────────────────── */
.priority-3d-box {
    position: relative;
    background: #FFFFFF;
    border-radius: 12px;
    padding: 0.85rem 1.15rem;
    margin-bottom: 0.65rem;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02),
                0 6px 14px rgba(0, 0, 0, 0.03);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.priority-3d-box:hover {
    transform: translateX(4px) translateY(-2px);
    box-shadow: 0 8px 20px -2px rgba(0, 0, 0, 0.08);
}

/* ── 3D Hero Banner ──────────────────────────────────────────────────────── */
.hero-3d-wrapper {
    position: relative;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(243, 244, 255, 0.92) 50%, rgba(238, 242, 255, 0.95) 100%);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(199, 210, 254, 0.7);
    border-radius: 20px;
    padding: 1.75rem 2.25rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 30px -5px rgba(79, 70, 229, 0.12),
                0 20px 40px -15px rgba(0, 0, 0, 0.05),
                inset 0 1px 1px rgba(255, 255, 255, 1);
    overflow: hidden;
}

.hero-3d-wrapper::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 60%);
    pointer-events: none;
    animation: float3D 12s ease-in-out infinite alternate;
}

.hero-title-gradient {
    font-size: 2.15rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #0F172A 0%, #312E81 40%, #4F46E5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.35rem;
}

/* ── 3D Interactive Pills ────────────────────────────────────────────────── */
.chip-3d {
    display: inline-flex;
    align-items: center;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.8rem;
    font-weight: 600;
    color: #334155;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255, 255, 255, 1);
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    margin: 0.2rem;
}

.chip-3d:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 5px 12px rgba(79, 70, 229, 0.15);
    border-color: #818CF8;
}

/* ── Streamlit Tabs Styling ──────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(10px);
    padding: 6px;
    border-radius: 14px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 8px 16px;
    font-weight: 600;
    color: #475569;
    border: none;
    transition: all 0.2s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(241, 245, 249, 0.8);
    color: #4F46E5;
}

.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #4F46E5 !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15) !important;
    transform: translateY(-1px);
}

/* ── Streamlit Button Enhancements ───────────────────────────────────────── */
button[kind="primary"] {
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 50%, #4338CA 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.25rem !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 8px 22px rgba(79, 70, 229, 0.45) !important;
}

button[kind="primary"]:active {
    transform: translateY(1px) scale(0.99) !important;
}

button[kind="secondary"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

button[kind="secondary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05) !important;
}

/* ── Demo Banner & Stale Warnings ────────────────────────────────────────── */
.demo-banner {
    position: relative;
    background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
    border: 1px solid #F59E0B;
    border-radius: 12px;
    padding: 0.65rem 1.25rem;
    color: #92400E;
    font-weight: 600;
    font-size: 0.9rem;
    text-align: center;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.8);
    animation: float3D 6s ease-in-out infinite;
}

.stale-warning {
    background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
    border-left: 4px solid #F97316;
    border-radius: 8px;
    padding: 0.75rem 1.25rem;
    color: #9A3412;
    font-size: 0.88rem;
    font-weight: 500;
    margin: 0.75rem 0;
    box-shadow: 0 2px 8px rgba(249, 115, 22, 0.1);
}

.section-h {
    font-size: 1.25rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #0F172A;
    margin: 1.25rem 0 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.section-h::after {
    content: '';
    flex: 1;
    height: 2px;
    background: linear-gradient(90deg, #4F46E5 0%, rgba(79, 70, 229, 0.1) 80%, transparent 100%);
    border-radius: 2px;
}

.pp-footer {
    color: #94A3B8;
    font-size: 0.85rem;
    text-align: center;
    padding: 1.5rem 0 0.75rem;
    border-top: 1px solid #E2E8F0;
    margin-top: 2.5rem;
}
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)


def demo_banner():
    import streamlit as st
    st.markdown(
        '<div class="demo-banner">✨ <b>Demo Mode Active</b> — Operating with synthetic candidate fixtures & offline models. No cloud API calls.</div>',
        unsafe_allow_html=True,
    )


def stale_warning(msg: str):
    import streamlit as st
    st.markdown(f'<div class="stale-warning">⚡ <b>Configuration Updated:</b> {msg}</div>', unsafe_allow_html=True)


def card_open():
    import streamlit as st
    st.markdown('<div class="pp-card">', unsafe_allow_html=True)


def card_close():
    import streamlit as st
    st.markdown('</div>', unsafe_allow_html=True)


def footer():
    import streamlit as st
    st.markdown(
        '<div class="pp-footer">🛡️ <b>PrepLio</b> • Privacy-Preserving Placement Preparation • AI feedback is guidance, not a guarantee of selection.</div>',
        unsafe_allow_html=True,
    )


def severity_label(sev: str) -> str:
    icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(sev.lower(), "⚪")
    return f'<span>{icon} {sev.upper()}</span>'
