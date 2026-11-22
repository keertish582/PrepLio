"""
tests/test_ui_state.py — Unit tests for centralized session state management.
"""
import pytest
from unittest.mock import MagicMock
import streamlit as st

import ui.state as S


@pytest.fixture(autouse=True)
def clean_session_state():
    """Reset session state before every test."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    S.init_state()
    yield


def test_init_state_defaults():
    assert S.get(S.APP_MODE) == "demo"
    assert S.get(S.SELECTED_ROLE) == "Software Developer"
    assert S.get(S.DEEP_REVIEW) is False
    assert S.get(S.FILE_HASH) is None
    assert S.get(S.REVIEW_RESULT) is None
    assert S.get(S.INTERVIEW_STATE) == "idle"
    assert S.get(S.INTERVIEW_ANSWERS) == []


def test_file_fingerprint():
    data1 = b"Sample resume content A"
    data2 = b"Sample resume content B"
    fp1 = S.file_fingerprint(data1)
    fp2 = S.file_fingerprint(data2)
    assert len(fp1) == 32
    assert fp1 != fp2
    assert fp1 == S.file_fingerprint(data1)


def test_on_file_change_invalidation():
    # Set initial state
    S.set_val(S.FILE_HASH, "hash_v1")
    S.set_val(S.REVIEW_RESULT, "dummy_result")
    S.set_val(S.REVIEW_STALE, False)
    S.set_val(S.GAP_STALE, False)

    # Change file
    S.on_file_change("hash_v2")
    assert S.get(S.FILE_HASH) == "hash_v2"
    assert S.get(S.REVIEW_RESULT) is None
    assert S.get(S.REVIEW_STALE) is False
    assert S.get(S.GAP_STALE) is True
    assert S.get(S.QUESTIONS_STALE) is True


def test_on_role_change_stale_flagging():
    S.set_val(S.SELECTED_ROLE, "Software Developer")
    S.set_val(S.REVIEW_ROLE, "Software Developer")
    S.set_val(S.REVIEW_RESULT, "dummy_review")
    S.set_val(S.GAP_ROLE, "Software Developer")

    # Change role to Data Scientist
    S.on_role_change("Data Scientist")
    assert S.get(S.SELECTED_ROLE) == "Data Scientist"
    assert S.get(S.REVIEW_STALE) is True
    assert S.get(S.GAP_STALE) is True
    assert S.get(S.QUESTIONS_STALE) is True


def test_clear_session():
    S.set_val(S.FILE_HASH, "xyz")
    S.set_val(S.EXTRACTED_TEXT, "Private candidate text")
    S.set_val(S.REVIEW_RESULT, "private_result")
    S.set_val(S.INTERVIEW_ANSWERS, ["ans1", "ans2"])
    S.set_val(S.SELECTED_ROLE, "DevOps Engineer")

    S.clear_session()

    assert S.get(S.FILE_HASH) is None
    assert S.get(S.EXTRACTED_TEXT) is None
    assert S.get(S.REVIEW_RESULT) is None
    assert S.get(S.INTERVIEW_ANSWERS) == []
    # Role and mode should be preserved
    assert S.get(S.SELECTED_ROLE) == "DevOps Engineer"


def test_user_profile_state_and_db():
    from core.db import init_db, get_or_create_user, update_user_profile, get_user_by_id
    init_db()
    user = get_or_create_user(
        identifier="+919876543210",
        name="Rahul Sharma",
        role="Software Developer",
        education="B.Tech CS",
        status="Actively Preparing",
    )
    assert user["id"] is not None
    assert user["identifier"] == "+919876543210"
    assert user["name"] == "Rahul Sharma"

    update_user_profile(user["id"], "Rahul S.", "Data Scientist", "M.Tech CS", "Interview Prep")
    updated = get_user_by_id(user["id"])
    assert updated is not None
    assert updated["name"] == "Rahul S."
    assert updated["role"] == "Data Scientist"
    assert updated["education"] == "M.Tech CS"
