from __future__ import annotations
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional
import pandas as pd

PALETTE = dict(accent="#4F46E5", success="#15803D", warning="#A16207",
               error="#B91C1C", bg="#F6F8FC", surface="#FFFFFF",
               text="#172033", secondary="#526176", border="#E2E8F0")

LAYOUT_BASE = dict(
    paper_bgcolor=PALETTE["surface"],
    plot_bgcolor=PALETTE["surface"],
    font=dict(family="system-ui, -apple-system, sans-serif", color=PALETTE["text"]),
    margin=dict(l=40, r=20, t=40, b=40),
)

def ats_gauge(score: Optional[float], max_val: float = 100, label: str = "Resume Readiness") -> go.Figure:
    """Gauge chart for resume readiness score."""
    if score is None:
        fig = go.Figure()
        fig.add_annotation(text="Score pending — complete AI review", x=0.5, y=0.5,
                           showarrow=False, font=dict(color=PALETTE["secondary"], size=14))
        fig.update_layout(**LAYOUT_BASE, title=dict(text=label, font=dict(size=14)))
        return fig
    
    color = PALETTE["error"] if score < 50 else (PALETTE["warning"] if score < 75 else PALETTE["success"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0,1], "y": [0,1]},
        title={"text": label, "font": {"size": 14, "color": PALETTE["text"]}},
        number={"font": {"size": 36, "color": color}, "suffix": f"/{max_val:.0f}"},
        gauge={
            "axis": {"range": [0, max_val], "tickwidth": 1, "tickcolor": PALETTE["border"]},
            "bar": {"color": color},
            "bgcolor": PALETTE["bg"],
            "steps": [
                {"range": [0, max_val*0.5], "color": "#FEE2E2"},
                {"range": [max_val*0.5, max_val*0.75], "color": "#FEF3C7"},
                {"range": [max_val*0.75, max_val], "color": "#DCFCE7"},
            ],
            "threshold": {"line": {"color": PALETTE["accent"], "width": 3},
                          "thickness": 0.75, "value": score},
        }
    ))
    fig.update_layout(**LAYOUT_BASE, height=250)
    return fig

def rule_breakdown_bar(checks: list[dict]) -> go.Figure:
    """Horizontal bar chart of rule check scores."""
    if not checks:
        fig = go.Figure()
        fig.add_annotation(text="No rule checks available", x=0.5, y=0.5, showarrow=False,
                           font=dict(color=PALETTE["secondary"]))
        fig.update_layout(**LAYOUT_BASE, title="Rule Checks")
        return fig
    
    names = [c.get("rule_name","").replace("_"," ").title() for c in checks]
    scores = [c.get("score", 0) for c in checks]
    maxes = [c.get("max_score", 1) for c in checks]
    colors = [PALETTE["success"] if c.get("passed") else PALETTE["error"] for c in checks]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=names, x=scores, orientation="h", name="Score",
        marker_color=colors, text=[f"{s:.0f}/{m:.0f}" for s,m in zip(scores,maxes)],
        textposition="outside", hovertemplate="%{y}: %{x}<extra></extra>"
    ))
    fig.update_layout(**LAYOUT_BASE, title="Rule Check Results",
                      xaxis=dict(title="Score", range=[0, max(maxes)+2]),
                      yaxis=dict(title=""), height=max(300, len(checks)*40))
    return fig

def section_scores_radar(sections: list[dict]) -> go.Figure:
    """Radar chart of section scores."""
    if not sections or len(sections) < 3:
        fig = go.Figure()
        fig.add_annotation(text="Need at least 3 sections for radar chart", x=0.5, y=0.5,
                           showarrow=False, font=dict(color=PALETTE["secondary"]))
        fig.update_layout(**LAYOUT_BASE, title="Section Scores")
        return fig
    
    names = [s.get("section_name","") for s in sections]
    scores = [s.get("score", 0) for s in sections]
    names_closed = names + [names[0]]
    scores_closed = scores + [scores[0]]
    
    fig = go.Figure(go.Scatterpolar(
        r=scores_closed, theta=names_closed, fill="toself",
        line_color=PALETTE["accent"], fillcolor=f"rgba(79,70,229,0.15)",
        hovertemplate="%{theta}: %{r:.1f}/10<extra></extra>"
    ))
    fig.update_layout(**LAYOUT_BASE, title="Section Scores (out of 10)",
                      polar=dict(radialaxis=dict(visible=True, range=[0,10],
                                                  tickfont=dict(size=10))),
                      height=350)
    return fig

def match_donut(match_pct: float, label: str = "Role Match") -> go.Figure:
    """Donut chart for skill match percentage."""
    color = PALETTE["error"] if match_pct < 50 else (PALETTE["warning"] if match_pct < 75 else PALETTE["success"])
    fig = go.Figure(go.Pie(
        values=[match_pct, 100-match_pct],
        labels=[f"Matched", "Gap"],
        hole=0.65,
        marker_colors=[color, PALETTE["border"]],
        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
        textinfo="none",
    ))
    fig.add_annotation(text=f"{match_pct:.0f}%", x=0.5, y=0.5,
                       font=dict(size=28, color=color, family="system-ui"), showarrow=False)
    fig.update_layout(**LAYOUT_BASE, title=label, showlegend=True,
                      legend=dict(orientation="h", y=-0.1), height=280)
    return fig

def score_trend_line(history: list[dict]) -> go.Figure:
    """Line chart of score over time."""
    if not history:
        fig = go.Figure()
        fig.add_annotation(text="No history yet — save your first analysis to see trends",
                           x=0.5, y=0.5, showarrow=False, font=dict(color=PALETTE["secondary"]))
        fig.update_layout(**LAYOUT_BASE, title="Score Trend")
        return fig
    
    df = pd.DataFrame(history)
    fig = go.Figure()
    
    if "rule_score" in df.columns:
        fig.add_trace(go.Scatter(x=df["reviewed_at"], y=df["rule_score"],
                                  mode="lines+markers", name="Rule Score (0–85)",
                                  line=dict(color=PALETTE["accent"], width=2),
                                  hovertemplate="%{x}: %{y:.1f}<extra>Rule</extra>"))
    
    if "final_score" in df.columns:
        complete = df[df["ai_complete"].astype(bool)]
        if not complete.empty:
            fig.add_trace(go.Scatter(x=complete["reviewed_at"], y=complete["final_score"],
                                      mode="lines+markers", name="Final Score (0–100)",
                                      line=dict(color=PALETTE["success"], width=2, dash="dash"),
                                      hovertemplate="%{x}: %{y:.0f}<extra>Final</extra>"))
    
    fig.update_layout(**LAYOUT_BASE, title="Score Trend Over Time",
                      xaxis=dict(title="Date"), yaxis=dict(title="Score"),
                      legend=dict(orientation="h", y=-0.15), height=320)
    return fig

def weak_topics_bar(counts: dict) -> go.Figure:
    """Bar chart of weak topic frequencies."""
    if not counts:
        fig = go.Figure()
        fig.add_annotation(text="No weak topics recorded yet",
                           x=0.5, y=0.5, showarrow=False, font=dict(color=PALETTE["secondary"]))
        fig.update_layout(**LAYOUT_BASE, title="Weak Topics")
        return fig
    
    sorted_items = sorted(counts.items(), key=lambda x: -x[1])
    topics, freqs = zip(*sorted_items)
    
    fig = go.Figure(go.Bar(
        x=list(topics), y=list(freqs),
        marker_color=PALETTE["warning"],
        hovertemplate="%{x}: %{y} sessions<extra></extra>"
    ))
    fig.update_layout(**LAYOUT_BASE, title="Weak Topics (Interview Sessions)",
                      xaxis=dict(title="Topic"), yaxis=dict(title="Frequency"), height=300)
    return fig

def category_scores_bar(cat_scores: dict) -> go.Figure:
    """Bar chart of interview category scores."""
    if not cat_scores:
        fig = go.Figure()
        fig.add_annotation(text="No category scores available",
                           x=0.5, y=0.5, showarrow=False, font=dict(color=PALETTE["secondary"]))
        fig.update_layout(**LAYOUT_BASE, title="Category Scores")
        return fig
    
    cats = list(cat_scores.keys())
    scores = list(cat_scores.values())
    colors = [PALETTE["success"] if s >= 7 else (PALETTE["warning"] if s >= 5 else PALETTE["error"]) for s in scores]
    
    fig = go.Figure(go.Bar(
        x=cats, y=scores, marker_color=colors,
        text=[f"{s:.1f}/10" for s in scores], textposition="outside",
        hovertemplate="%{x}: %{y:.1f}/10<extra></extra>"
    ))
    fig.update_layout(**LAYOUT_BASE, title="Interview Category Scores (0–10)",
                      yaxis=dict(range=[0,11], title="Score"), height=320)
    return fig
