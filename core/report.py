"""
core/report.py — PDF and JSON export for PrepLio.
"""
from __future__ import annotations

import io
import json
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.platypus import PageBreak


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe(text: Any) -> str:
    """Escape & < > for ReportLab Paragraph markup."""
    s = str(text) if text is not None else ""
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    return s


def _page_number_footer(canvas, doc):  # type: ignore[no-untyped-def]
    """Draw page number at the bottom of each page."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#888888"))
    page_text = f"Page {doc.page}"
    canvas.drawCentredString(A4[0] / 2, 1.0 * cm, page_text)
    canvas.restoreState()


# ---------------------------------------------------------------------------
# PDF builder
# ---------------------------------------------------------------------------

def build_report_pdf(
    *,
    role: str = "",
    origin: str = "",
    rule_score: float | None = None,
    ai_score: float | None = None,
    final_score: float | None = None,
    ai_complete: bool = False,
    summary: str = "",
    priority_fixes: list[Any] | None = None,
    section_feedback: list[Any] | None = None,
    gap_report: dict[str, Any] | None = None,
    interview_summary: dict[str, Any] | None = None,
) -> bytes:
    """Build a PDF report and return it as bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2.5 * cm,
        title="PrepLio Report",
        author="PrepLio",
    )

    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#4F46E5"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    style_h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#172033"),
        spaceBefore=12,
        spaceAfter=4,
    )
    style_body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )
    style_bullet = ParagraphStyle(
        "Bullet",
        parent=style_body,
        leftIndent=16,
        bulletIndent=6,
    )

    story: list[Any] = []

    # --- Title ---
    story.append(Paragraph("PrepLio — Placement Report", style_title))
    if role:
        story.append(Paragraph(f"<b>Target Role:</b> {_safe(role)}", style_body))
    if origin:
        story.append(Paragraph(f"<b>Origin:</b> {_safe(origin)}", style_body))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#4F46E5")))
    story.append(Spacer(1, 0.3 * cm))

    # --- Scores ---
    story.append(Paragraph("Scores", style_h2))
    score_data = [["Metric", "Value"]]
    if rule_score is not None:
        score_data.append(["ATS / Rule Score", f"{rule_score:.1f}"])
    if ai_score is not None:
        score_data.append(["AI Score", f"{ai_score:.1f}"])
    if final_score is not None:
        score_data.append(["Final Score", f"{final_score:.1f}"])
    score_data.append(["AI Assessment Complete", "Yes" if ai_complete else "No"])

    if len(score_data) > 1:
        t = Table(score_data, colWidths=[8 * cm, 8 * cm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(t)
    story.append(Spacer(1, 0.3 * cm))

    # --- Summary ---
    if summary:
        story.append(Paragraph("Summary", style_h2))
        story.append(Paragraph(_safe(summary), style_body))
        story.append(Spacer(1, 0.3 * cm))

    # --- Priority Fixes ---
    if priority_fixes:
        story.append(Paragraph("Priority Fixes", style_h2))
        for fix in priority_fixes:
            if isinstance(fix, dict):
                sev = _safe(fix.get("severity", "medium")).upper()
                sec = _safe(fix.get("section", ""))
                act = _safe(fix.get("action", ""))
                story.append(
                    Paragraph(
                        f"<b>[{sev}]</b> <i>{sec}</i>: {act}",
                        style_bullet,
                    )
                )
            else:
                story.append(Paragraph(f"• {_safe(fix)}", style_bullet))
        story.append(Spacer(1, 0.3 * cm))

    # --- Section Feedback ---
    if section_feedback:
        story.append(Paragraph("Section Feedback", style_h2))
        for sf in section_feedback:
            if not isinstance(sf, dict):
                continue
            sec_name = _safe(sf.get("section_name", ""))
            score = sf.get("score", 0)
            max_s = sf.get("max_score", 10)
            story.append(
                Paragraph(
                    f"<b>{sec_name}</b> — {score}/{max_s}",
                    style_body,
                )
            )
            explanation = sf.get("explanation", "")
            if explanation:
                story.append(Paragraph(_safe(explanation), style_body))
            strengths = sf.get("strengths", [])
            for s in strengths:
                story.append(Paragraph(f"✓ {_safe(s)}", style_bullet))
            weaknesses = sf.get("weaknesses", [])
            for w in weaknesses:
                story.append(Paragraph(f"✗ {_safe(w)}", style_bullet))
            story.append(Spacer(1, 0.2 * cm))

    # --- Gap Report ---
    if gap_report and isinstance(gap_report, dict):
        story.append(Paragraph("Skill Gap Report", style_h2))
        story.append(
            Paragraph(
                f"<b>Match:</b> {gap_report.get('match_pct', 0):.1f}%",
                style_body,
            )
        )
        mh = gap_report.get("must_haves", [])
        if mh:
            story.append(Paragraph("Must-Haves:", style_body))
            for item in mh:
                if isinstance(item, dict):
                    matched = "✓" if item.get("matched") else "✗"
                    story.append(
                        Paragraph(
                            f"{matched} {_safe(item.get('skill', ''))}",
                            style_bullet,
                        )
                    )
        gth = gap_report.get("good_to_haves", [])
        if gth:
            story.append(Paragraph("Good-to-Haves:", style_body))
            for item in gth:
                if isinstance(item, dict):
                    matched = "✓" if item.get("matched") else "✗"
                    story.append(
                        Paragraph(
                            f"{matched} {_safe(item.get('skill', ''))}",
                            style_bullet,
                        )
                    )
        story.append(Spacer(1, 0.3 * cm))

    # --- Interview Summary ---
    if interview_summary and isinstance(interview_summary, dict):
        story.append(Paragraph("Interview Summary", style_h2))
        avg = interview_summary.get("avg_score")
        if avg is not None:
            story.append(Paragraph(f"<b>Average Score:</b> {avg:.1f}", style_body))
        strengths = interview_summary.get("strengths", [])
        if strengths:
            story.append(Paragraph("Strengths:", style_body))
            for s in strengths:
                story.append(Paragraph(f"✓ {_safe(s)}", style_bullet))
        weak_topics = interview_summary.get("weak_topics", [])
        if weak_topics:
            story.append(Paragraph("Weak Topics:", style_body))
            for w in weak_topics:
                story.append(Paragraph(f"✗ {_safe(w)}", style_bullet))
        practice = interview_summary.get("practice_plan", [])
        if practice:
            story.append(Paragraph("Practice Plan:", style_body))
            for p in practice:
                story.append(Paragraph(f"• {_safe(p)}", style_bullet))

    doc.build(story, onFirstPage=_page_number_footer, onLaterPages=_page_number_footer)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# JSON builder
# ---------------------------------------------------------------------------

def build_report_json(
    *,
    role: str = "",
    origin: str = "",
    rule_score: float | None = None,
    ai_score: float | None = None,
    final_score: float | None = None,
    ai_complete: bool = False,
    summary: str = "",
    priority_fixes: list[Any] | None = None,
    section_feedback: list[Any] | None = None,
    gap_report: dict[str, Any] | None = None,
    interview_summary: dict[str, Any] | None = None,
) -> bytes:
    """Build a JSON report and return it as UTF-8 bytes."""
    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "scoring_version": "1.0",
        "generated_at": now_iso,
        "role": role,
        "origin": origin,
        "completeness": {"ai_assessment_complete": ai_complete},
        "warnings": [] if ai_complete else ["AI assessment incomplete — final score not available"],
        "scores": {
            "rule_score": rule_score,
            "ai_score": ai_score,
            "final_score": final_score if ai_complete else None,
            "ai_complete": ai_complete,
        },
        "summary": summary,
        "priority_fixes": priority_fixes or [],
        "section_feedback": section_feedback or [],
        "gap_report": gap_report or {},
        "interview_summary": interview_summary or {},
    }
    return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
