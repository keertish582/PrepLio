COLORS = {
    "bg": "#F6F8FC",
    "surface": "#FFFFFF",
    "primary_text": "#172033",
    "secondary_text": "#526176",
    "accent": "#4F46E5",
    "success": "#15803D",
    "warning": "#A16207",
    "error": "#B91C1C",
    "border": "#E2E8F0",
    "muted": "#94A3B8",
}

CSS = """
<style>
/* Page base */
.stApp { background-color: #F6F8FC; }
/* Hide default Streamlit hamburger/footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
/* Card component */
.pp-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
/* Score badge */
.pp-score-badge {
    display: inline-block;
    background: #4F46E5;
    color: #fff;
    font-size: 2rem;
    font-weight: 700;
    border-radius: 50%;
    width: 72px; height: 72px;
    line-height: 72px;
    text-align: center;
}
/* Severity pills */
.sev-high   { color: #B91C1C; font-weight: 600; }
.sev-medium { color: #A16207; font-weight: 600; }
.sev-low    { color: #15803D; font-weight: 600; }
/* Demo banner */
.demo-banner {
    background: #FEF3C7;
    border: 1px solid #F59E0B;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    color: #92400E;
    font-weight: 600;
    text-align: center;
    margin-bottom: 1rem;
}
/* Stale result warning */
.stale-warning {
    background: #FFF7ED;
    border-left: 4px solid #F97316;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    color: #7C2D12;
    margin: 0.5rem 0;
}
/* Footer */
.pp-footer {
    color: #94A3B8;
    font-size: 0.8rem;
    text-align: center;
    padding: 1rem 0;
    border-top: 1px solid #E2E8F0;
    margin-top: 2rem;
}
/* Upload area */
.upload-hint {
    color: #526176;
    font-size: 0.875rem;
    text-align: center;
    padding: 0.5rem;
}
/* Section heading */
.section-h {
    font-size: 1.1rem;
    font-weight: 700;
    color: #172033;
    margin: 1rem 0 0.5rem;
    border-bottom: 2px solid #4F46E5;
    padding-bottom: 0.25rem;
}
</style>
"""

def inject_css():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)

def demo_banner():
    import streamlit as st
    st.markdown('<div class="demo-banner">🧪 Demo Mode — synthetic sample data; no live AI assessment.</div>', unsafe_allow_html=True)

def stale_warning(msg: str):
    import streamlit as st
    st.markdown(f'<div class="stale-warning">⚠️ {msg}</div>', unsafe_allow_html=True)

def card_open():
    import streamlit as st
    st.markdown('<div class="pp-card">', unsafe_allow_html=True)

def card_close():
    import streamlit as st
    st.markdown('</div>', unsafe_allow_html=True)

def footer():
    import streamlit as st
    st.markdown('<div class="pp-footer">AI feedback is guidance, not a guarantee of selection.</div>', unsafe_allow_html=True)

def severity_label(sev: str) -> str:
    css_class = f"sev-{sev.lower()}"
    icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(sev.lower(), "⚪")
    return f'<span class="{css_class}">{icon} {sev.upper()}</span>'
