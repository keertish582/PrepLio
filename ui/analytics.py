"""
ui/analytics.py — High-impact Plotly visualization builders for PrepLio.
Provides 3D-styled, responsive charts with glassmorphic backgrounds and hover effects.
"""
from __future__ import annotations

from typing import Optional
import pandas as pd
import plotly.graph_objects as go

PALETTE = dict(
    accent="#4F46E5",
    accent_purple="#7C3AED",
    accent_cyan="#06B6D4",
    success="#10B981",
    warning="#F59E0B",
    error="#EF4444",
    bg="#F6F8FC",
    surface="#FFFFFF",
    text="#0F172A",
    secondary="#64748B",
    border="#E2E8F0",
)

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(255, 255, 255, 0.75)",
    plot_bgcolor="rgba(255, 255, 255, 0.75)",
    font=dict(family="Plus Jakarta Sans, system-ui, -apple-system, sans-serif", color=PALETTE["text"], size=12),
    margin=dict(l=45, r=25, t=45, b=45),
    hoverlabel=dict(
        bgcolor="#1E1B4B",
        font=dict(color="#FFFFFF", family="Plus Jakarta Sans, system-ui", size=12),
        bordercolor="#6366F1",
    ),
)


def ats_gauge(score: Optional[float], max_val: float = 100, label: str = "Resume Readiness") -> go.Figure:
    """3D-styled Gauge chart for resume readiness score."""
    if score is None:
        fig = go.Figure()
        fig.add_annotation(
            text="⏳ Score pending — Complete AI review",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(color=PALETTE["secondary"], size=14, weight="bold"),
        )
        fig.update_layout(**LAYOUT_BASE, title=dict(text=f"📊 {label}", font=dict(size=14, weight="bold")))
        return fig

    color = PALETTE["error"] if score < 50 else (PALETTE["warning"] if score < 75 else PALETTE["success"])
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": f"<b>{label}</b>", "font": {"size": 15, "color": PALETTE["text"]}},
            number={
                "font": {"size": 42, "color": color, "family": "Plus Jakarta Sans"},
                "suffix": f" <span style='font-size:18px;color:{PALETTE['secondary']}'>/{max_val:.0f}</span>",
            },
            gauge={
                "axis": {"range": [0, max_val], "tickwidth": 1.5, "tickcolor": PALETTE["border"]},
                "bar": {"color": color, "thickness": 0.28},
                "bgcolor": "rgba(241, 245, 249, 0.6)",
                "borderwidth": 1,
                "bordercolor": PALETTE["border"],
                "steps": [
                    {"range": [0, max_val * 0.5], "color": "rgba(254, 226, 226, 0.65)"},
                    {"range": [max_val * 0.5, max_val * 0.75], "color": "rgba(254, 243, 199, 0.65)"},
                    {"range": [max_val * 0.75, max_val], "color": "rgba(209, 250, 229, 0.65)"},
                ],
                "threshold": {
                    "line": {"color": PALETTE["accent"], "width": 4},
                    "thickness": 0.85,
                    "value": score,
                },
            },
        )
    )
    fig.update_layout(**LAYOUT_BASE, height=270)
    return fig


def rule_breakdown_bar(checks: list[dict]) -> go.Figure:
    """Horizontal bar chart with rounded 3D appearance."""
    if not checks:
        fig = go.Figure()
        fig.add_annotation(
            text="No rule checks available",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(color=PALETTE["secondary"], size=13),
        )
        fig.update_layout(**LAYOUT_BASE, title="Rule Checks")
        return fig

    names = [c.get("rule_name", "").replace("_", " ").title() for c in checks]
    scores = [c.get("score", 0) for c in checks]
    maxes = [c.get("max_score", 1) for c in checks]
    colors = [PALETTE["success"] if c.get("passed") else PALETTE["error"] for c in checks]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=names,
            x=scores,
            orientation="h",
            name="Score",
            marker=dict(
                color=colors,
                line=dict(color="rgba(255,255,255,0.8)", width=1.5),
            ),
            text=[f"  <b>{s:.0f}</b> / {m:.0f} pts" for s, m in zip(scores, maxes)],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Awarded: %{x} pts<extra></extra>",
        )
    )
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="<b>Deterministic Rule Check Results (0–85 pts)</b>", font=dict(size=14)),
        xaxis=dict(title="Points Awarded", range=[0, max(maxes) + 3], gridcolor="rgba(226,232,240,0.6)"),
        yaxis=dict(title="", autorange="reversed"),
        height=max(320, len(checks) * 42),
    )
    return fig


def section_scores_radar(sections: list[dict]) -> go.Figure:
    """Radar chart of section scores with glowing 3D surface."""
    if not sections or len(sections) < 3:
        fig = go.Figure()
        fig.add_annotation(
            text="Need at least 3 sections for radar geometry",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(color=PALETTE["secondary"], size=13),
        )
        fig.update_layout(**LAYOUT_BASE, title="Section Scores")
        return fig

    names = [s.get("section_name", "") for s in sections]
    scores = [s.get("score", 0) for s in sections]
    names_closed = names + [names[0]]
    scores_closed = scores + [scores[0]]

    fig = go.Figure(
        go.Scatterpolar(
            r=scores_closed,
            theta=names_closed,
            fill="toself",
            line=dict(color=PALETTE["accent"], width=2.5),
            fillcolor="rgba(79, 70, 229, 0.22)",
            marker=dict(size=7, color=PALETTE["accent_purple"], line=dict(color="#FFFFFF", width=2)),
            hovertemplate="<b>%{theta}</b><br>Score: %{r:.1f} / 10<extra></extra>",
        )
    )
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="<b>Section Competency Radar (0–10 Scale)</b>", font=dict(size=14)),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=10, color=PALETTE["secondary"])),
            bgcolor="rgba(248, 250, 252, 0.6)",
        ),
        height=360,
    )
    return fig


def match_donut(match_pct: float, label: str = "Role Match") -> go.Figure:
    """3D-styled Donut chart for skill match percentage."""
    color = PALETTE["error"] if match_pct < 50 else (PALETTE["warning"] if match_pct < 75 else PALETTE["success"])
    fig = go.Figure(
        go.Pie(
            values=[match_pct, 100 - match_pct],
            labels=["Matched Competencies", "Identified Gaps"],
            hole=0.72,
            marker=dict(
                colors=[color, "rgba(226, 232, 240, 0.6)"],
                line=dict(color=["#FFFFFF", "#FFFFFF"], width=[2, 1]),
            ),
            hovertemplate="<b>%{label}</b>: %{value:.1f}%<extra></extra>",
            textinfo="none",
            sort=False,
        )
    )
    fig.add_annotation(
        text=f"<b>{match_pct:.0f}%</b><br><span style='font-size:12px;color:{PALETTE['secondary']}'>ALIGNMENT</span>",
        x=0.5,
        y=0.5,
        font=dict(size=26, color=color, family="Plus Jakarta Sans"),
        showarrow=False,
    )
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=f"<b>{label}</b>", font=dict(size=14)),
        showlegend=True,
        legend=dict(orientation="h", y=-0.15, x=0.15),
        height=290,
    )
    return fig


def score_trend_line(history: list[dict]) -> go.Figure:
    """Line chart with filled glowing gradient under curves."""
    if not history:
        fig = go.Figure()
        fig.add_annotation(
            text="No history yet — Save your first review locally to track progress trends",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(color=PALETTE["secondary"], size=13),
        )
        fig.update_layout(**LAYOUT_BASE, title="Score Trend")
        return fig

    df = pd.DataFrame(history)
    fig = go.Figure()

    if "rule_score" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["reviewed_at"],
                y=df["rule_score"],
                mode="lines+markers",
                name="Rule Score (0–85)",
                line=dict(color=PALETTE["accent"], width=3, shape="spline"),
                fill="tozeroy",
                fillcolor="rgba(79, 70, 229, 0.08)",
                marker=dict(size=8, color=PALETTE["accent"], line=dict(color="#FFFFFF", width=2)),
                hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Rule Score: %{y:.1f} / 85<extra></extra>",
            )
        )

    if "final_score" in df.columns:
        complete = df[df["ai_complete"].astype(bool)]
        if not complete.empty:
            fig.add_trace(
                go.Scatter(
                    x=complete["reviewed_at"],
                    y=complete["final_score"],
                    mode="lines+markers",
                    name="Final Score (0–100)",
                    line=dict(color=PALETTE["success"], width=3, dash="dash", shape="spline"),
                    marker=dict(size=8, color=PALETTE["success"], line=dict(color="#FFFFFF", width=2)),
                    hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Final Complete Score: %{y:.0f} / 100<extra></extra>",
                )
            )

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="<b>Readiness Trajectory Over Time</b>", font=dict(size=14)),
        xaxis=dict(title="Review Date", gridcolor="rgba(226,232,240,0.6)"),
        yaxis=dict(title="Score", gridcolor="rgba(226,232,240,0.6)"),
        legend=dict(orientation="h", y=-0.18, x=0.2),
        height=330,
    )
    return fig


def weak_topics_bar(counts: dict) -> go.Figure:
    """Bar chart of weak topic frequencies with modern styling."""
    if not counts:
        fig = go.Figure()
        fig.add_annotation(
            text="No weak topics recorded yet",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(color=PALETTE["secondary"], size=13),
        )
        fig.update_layout(**LAYOUT_BASE, title="Weak Topics")
        return fig

    sorted_items = sorted(counts.items(), key=lambda x: -x[1])
    topics, freqs = zip(*sorted_items)

    fig = go.Figure(
        go.Bar(
            x=list(topics),
            y=list(freqs),
            marker=dict(
                color=PALETTE["warning"],
                line=dict(color="#FFFFFF", width=1.5),
            ),
            text=[f"<b>{f}</b> sessions" for f in freqs],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Flagged %{y} times<extra></extra>",
        )
    )
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="<b>Recurring Focus Topics from Mock Interviews</b>", font=dict(size=14)),
        xaxis=dict(title="Topic", gridcolor="rgba(226,232,240,0.6)"),
        yaxis=dict(title="Frequency", gridcolor="rgba(226,232,240,0.6)"),
        height=320,
    )
    return fig


def category_scores_bar(cat_scores: dict) -> go.Figure:
    """Bar chart of interview category scores."""
    if not cat_scores:
        fig = go.Figure()
        fig.add_annotation(
            text="No category scores available",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(color=PALETTE["secondary"], size=13),
        )
        fig.update_layout(**LAYOUT_BASE, title="Category Scores")
        return fig

    cats = list(cat_scores.keys())
    scores = list(cat_scores.values())
    colors = [PALETTE["success"] if s >= 7 else (PALETTE["warning"] if s >= 5 else PALETTE["error"]) for s in scores]

    fig = go.Figure(
        go.Bar(
            x=cats,
            y=scores,
            marker=dict(
                color=colors,
                line=dict(color="#FFFFFF", width=1.5),
            ),
            text=[f"<b>{s:.1f}</b> / 10" for s in scores],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Rubric Score: %{y:.1f} / 10<extra></extra>",
        )
    )
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="<b>Interview Category Breakdown (0–10 Scale)</b>", font=dict(size=14)),
        yaxis=dict(range=[0, 11.5], title="Performance Score", gridcolor="rgba(226,232,240,0.6)"),
        xaxis=dict(title="Category"),
        height=330,
    )
    return fig
