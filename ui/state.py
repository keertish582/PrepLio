from __future__ import annotations
import hashlib
from typing import Any, Optional
import streamlit as st

# ── State key constants ──────────────────────────────────────────────────────
APP_MODE = "app_mode"               # "live" | "demo"
SELECTED_ROLE = "selected_role"
DEEP_REVIEW = "deep_review"
FILE_HASH = "file_hash"
FILE_NAME = "file_name"
FILE_SIZE = "file_size"
EXTRACTED_TEXT = "extracted_text"
PARSED_RESUME = "parsed_resume"
REVIEW_RESULT = "review_result"
REVIEW_STALE = "review_stale"
REVIEW_ROLE = "review_role"
GAP_RESULT = "gap_result"
GAP_STALE = "gap_stale"
GAP_ROLE = "gap_role"
QUESTIONS = "questions"
QUESTIONS_STALE = "questions_stale"
INTERVIEW_STATE = "interview_state"       # idle|active|submitting|feedback|completed
INTERVIEW_SESSION = "interview_session"
ACTIVE_QUESTION_IDX = "active_question_idx"
INTERVIEW_ANSWERS = "interview_answers"
EXPORT_PDF_BYTES = "export_pdf_bytes"
EXPORT_JSON_BYTES = "export_json_bytes"
OLLAMA_STATUS = "ollama_status"
OLLAMA_CHECKED_AT = "ollama_checked_at"
USER_ID = "user_id"
USER_NAME = "user_name"
USER_IDENTIFIER = "user_identifier"
USER_EDUCATION = "user_education"
USER_STATUS = "user_status"
IS_LOGGED_IN = "is_logged_in"

DEFAULTS: dict[str, Any] = {
    APP_MODE: "demo",
    SELECTED_ROLE: "Software Developer",
    DEEP_REVIEW: False,
    FILE_HASH: None,
    FILE_NAME: None,
    FILE_SIZE: None,
    EXTRACTED_TEXT: None,
    PARSED_RESUME: None,
    REVIEW_RESULT: None,
    REVIEW_STALE: False,
    REVIEW_ROLE: None,
    GAP_RESULT: None,
    GAP_STALE: False,
    GAP_ROLE: None,
    QUESTIONS: None,
    QUESTIONS_STALE: False,
    INTERVIEW_STATE: "idle",
    INTERVIEW_SESSION: None,
    ACTIVE_QUESTION_IDX: 0,
    INTERVIEW_ANSWERS: [],
    EXPORT_PDF_BYTES: None,
    EXPORT_JSON_BYTES: None,
    OLLAMA_STATUS: None,
    OLLAMA_CHECKED_AT: None,
    USER_ID: 1,
    USER_NAME: "Candidate",
    USER_IDENTIFIER: "",
    USER_EDUCATION: "B.Tech Computer Science",
    USER_STATUS: "Actively Preparing",
    IS_LOGGED_IN: False,
}

def init_state():
    """Call once at app start to initialize all missing session-state keys."""
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get(key: str, default: Any = None) -> Any:
    val = st.session_state.get(key, DEFAULTS.get(key))
    return val if val is not None else default

def set_val(key: str, value: Any):
    st.session_state[key] = value

def file_fingerprint(file_bytes: bytes) -> str:
    return hashlib.md5(file_bytes).hexdigest()

def on_file_change(new_hash: str):
    """Invalidate all dependent state when a new file is uploaded."""
    if get(FILE_HASH) != new_hash:
        st.session_state[FILE_HASH] = new_hash
        st.session_state[REVIEW_RESULT] = None
        st.session_state[REVIEW_STALE] = False
        st.session_state[GAP_STALE] = True  # mark gap stale (old file)
        st.session_state[QUESTIONS_STALE] = True

def on_role_change(new_role: str):
    """Mark dependent results stale when role changes."""
    old_role = get(SELECTED_ROLE)
    if old_role and old_role != new_role:
        st.session_state[SELECTED_ROLE] = new_role
        # Mark stale but keep old results visible
        if get(REVIEW_ROLE) and get(REVIEW_ROLE) != new_role:
            st.session_state[REVIEW_STALE] = True
        if get(GAP_ROLE) and get(GAP_ROLE) != new_role:
            st.session_state[GAP_STALE] = True
        st.session_state[QUESTIONS_STALE] = True
    else:
        st.session_state[SELECTED_ROLE] = new_role

def clear_session():
    """Remove all private/analysis state. Keep mode, role, and user profile."""
    keep = {
        APP_MODE: get(APP_MODE),
        SELECTED_ROLE: get(SELECTED_ROLE),
        USER_ID: get(USER_ID),
        USER_NAME: get(USER_NAME),
        USER_IDENTIFIER: get(USER_IDENTIFIER),
        USER_EDUCATION: get(USER_EDUCATION),
        USER_STATUS: get(USER_STATUS),
        IS_LOGGED_IN: get(IS_LOGGED_IN),
    }
    for k in DEFAULTS:
        st.session_state[k] = DEFAULTS[k]
    for k, v in keep.items():
        st.session_state[k] = v
