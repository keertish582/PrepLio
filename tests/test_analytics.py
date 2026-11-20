"""
tests/test_analytics.py — Unit tests for Plotly visualization generators and report exporters.
"""
import pytest
import plotly.graph_objects as go
import ui.analytics as A
from core.report import build_report_pdf, build_report_json


def test_ats_gauge_populated():
    fig = A.ats_gauge(82.5, 100.0, "Resume Readiness")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].value == 82.5


def test_ats_gauge_empty():
    fig = A.ats_gauge(None, 100.0, "Resume Readiness")
    assert isinstance(fig, go.Figure)
    # Shows annotation when score is None
    assert len(fig.layout.annotations) > 0


def test_rule_breakdown_bar_populated():
    checks = [
        {"rule_name": "has_contact_info", "score": 10.0, "max_score": 10.0, "passed": True},
        {"rule_name": "quantified_achievements", "score": 4.0, "max_score": 10.0, "passed": False},
    ]
    fig = A.rule_breakdown_bar(checks)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1


def test_rule_breakdown_bar_empty():
    fig = A.rule_breakdown_bar([])
    assert isinstance(fig, go.Figure)
    assert len(fig.layout.annotations) > 0


def test_section_scores_radar():
    sections = [
        {"section_name": "Experience", "score": 8.0},
        {"section_name": "Education", "score": 9.0},
        {"section_name": "Skills", "score": 7.5},
    ]
    fig = A.section_scores_radar(sections)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1


def test_section_scores_radar_insufficient():
    # Fewer than 3 sections should safely render an annotation without error
    sections = [{"section_name": "Experience", "score": 8.0}]
    fig = A.section_scores_radar(sections)
    assert isinstance(fig, go.Figure)
    assert len(fig.layout.annotations) > 0


def test_match_donut():
    fig = A.match_donut(68.5, "Role Match")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].values[0] == 68.5


def test_score_trend_line_populated():
    history = [
        {"reviewed_at": "2026-11-01", "rule_score": 50.0, "final_score": 60.0, "ai_complete": True},
        {"reviewed_at": "2026-11-10", "rule_score": 70.0, "final_score": 80.0, "ai_complete": True},
    ]
    fig = A.score_trend_line(history)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1


def test_score_trend_line_empty():
    fig = A.score_trend_line([])
    assert isinstance(fig, go.Figure)
    assert len(fig.layout.annotations) > 0


def test_weak_topics_bar_dict():
    counts = {"System Design": 4, "Data Structures": 2}
    fig = A.weak_topics_bar(counts)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1


def test_weak_topics_bar_empty():
    fig = A.weak_topics_bar({})
    assert isinstance(fig, go.Figure)
    assert len(fig.layout.annotations) > 0


def test_category_scores_bar():
    cats = {"Technical": 7.5, "Behavioral": 8.2}
    fig = A.category_scores_bar(cats)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1


def test_build_report_pdf():
    pdf_bytes = build_report_pdf(
        role="Software Developer",
        origin="live",
        rule_score=78.0,
        ai_score=11.0,
        final_score=89.0,
        ai_complete=True,
        summary="Solid candidate profile.",
        priority_fixes=[{"severity": "medium", "section": "Experience", "action": "Add metrics."}],
        section_feedback=[{"section_name": "Experience", "score": 8.0, "strengths": ["Clear bullets"], "weaknesses": []}],
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")


def test_build_report_json():
    json_bytes = build_report_json(
        role="Software Developer",
        origin="live",
        rule_score=75.0,
        ai_score=None,
        final_score=None,
        ai_complete=False,
        summary="Rules completed.",
    )
    import json
    data = json.loads(json_bytes.decode("utf-8"))
    assert data["role"] == "Software Developer"
    assert data["scores"]["rule_score"] == 75.0
    assert data["scores"]["final_score"] is None
    assert data["completeness"]["ai_assessment_complete"] is False
