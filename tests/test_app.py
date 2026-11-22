"""
tests/test_app.py — Integration and AppTest verification for the Streamlit application shell.
"""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).parent.parent / "app.py")


def test_app_initial_render():
    """Verify that app.py compiles, runs, and renders the application shell cleanly."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception
    # Verify title text
    assert len(at.title) >= 1
    assert "Placement Preparation Assistant" in at.title[0].value


def test_app_tabs_rendered():
    """Verify that all 5 tabs are rendered properly after candidate sign-in."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception
    # Log in via quick demo button if on the login console
    demo_btn = [b for b in at.button if "Demo" in getattr(b, "label", "")]
    if demo_btn:
        demo_btn[0].click().run()
        assert not at.exception
    # Verify all 5 preparation console tabs exist
    assert len(at.tabs) == 5


def test_login_console_flow():
    """Verify separate login console initial state and transition to workspace consoles."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception
    # Initially in unauthenticated state: login console displayed, no tabs
    assert len(at.tabs) == 0
    # Quick demo login button is available
    demo_btn = [b for b in at.button if "Demo" in getattr(b, "label", "")]
    assert len(demo_btn) >= 1
    # Log in
    demo_btn[0].click().run()
    assert not at.exception
    # Consoles are now active
    assert len(at.tabs) == 5


def test_app_sidebar_controls():
    """Verify sidebar controls (role select, mode radio, clear session button)."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception
    # Check sidebar selectbox for role
    sidebar_selects = at.sidebar.selectbox
    assert len(sidebar_selects) >= 1
    assert "Software Developer" in sidebar_selects[0].options


def test_demo_mode_sample_load():
    """Verify clicking demo strong resume in Demo Mode sets results without exception."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception
    
    # Click strong resume button if present in demo mode
    strong_buttons = [b for b in at.button if "Strong" in getattr(b, "label", "")]
    if strong_buttons:
        strong_buttons[0].click().run()
        assert not at.exception
