"""
core/db.py — SQLite persistence for PrepLio.
Database: data/preplio.db
NOTE: Resume raw text is NEVER logged or stored in plain form.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

_DB_PATH = Path(__file__).parent.parent / "data" / "preplio.db"


def _get_conn() -> sqlite3.Connection:
    """Return a connection to the database, creating directories as needed."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create all tables if they do not exist."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS resume_reviews (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL DEFAULT 1,
                target_role    TEXT    NOT NULL DEFAULT '',
                file_name      TEXT    NOT NULL DEFAULT '',
                file_hash      TEXT    NOT NULL DEFAULT '',
                rule_score     REAL    NOT NULL DEFAULT 0.0,
                ai_score       REAL,
                final_score    REAL,
                ai_complete    INTEGER NOT NULL DEFAULT 0,
                summary        TEXT    NOT NULL DEFAULT '',
                priority_fixes TEXT    NOT NULL DEFAULT '[]',
                section_feedback TEXT  NOT NULL DEFAULT '[]',
                origin         TEXT    NOT NULL DEFAULT 'live',
                reviewed_at    TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS gap_reports (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL DEFAULT 1,
                role          TEXT    NOT NULL DEFAULT '',
                match_pct     REAL    NOT NULL DEFAULT 0.0,
                must_haves    TEXT    NOT NULL DEFAULT '[]',
                good_to_haves TEXT    NOT NULL DEFAULT '[]',
                roadmap       TEXT    NOT NULL DEFAULT '[]',
                project_ideas TEXT    NOT NULL DEFAULT '[]',
                origin        TEXT    NOT NULL DEFAULT 'live',
                generated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS interview_sessions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL DEFAULT 1,
                role         TEXT    NOT NULL DEFAULT '',
                difficulty   TEXT    NOT NULL DEFAULT 'medium',
                origin       TEXT    NOT NULL DEFAULT 'live',
                avg_score    REAL    NOT NULL DEFAULT 0.0,
                report       TEXT    NOT NULL DEFAULT '{}',
                answers      TEXT    NOT NULL DEFAULT '[]',
                started_at   TEXT    NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_resume_review(*args, **kwargs) -> int:
    """Persist a resume review.
    Accepts either (result_obj, origin="live") or keyword arguments.
    Returns the new row id.
    """
    user_id = kwargs.get("user_id", 1)
    origin = kwargs.get("origin", "live")
    
    if args and hasattr(args[0], "rule_bundle"):
        # Called as save_resume_review(result, origin="live")
        r = args[0]
        if len(args) > 1:
            origin = args[1]
        target_role = getattr(r, "target_role", "")
        parsed = getattr(r, "parsed", None)
        file_name = getattr(parsed, "file_name", "") if parsed else ""
        file_hash = getattr(parsed, "file_hash", "") if parsed else ""
        rule_score = r.rule_bundle.rule_score if hasattr(r, "rule_bundle") else 0.0
        ai_score = getattr(r, "ai_score", None)
        final_score = getattr(r, "final_score", None)
        ai_complete = bool(getattr(r, "ai_assessment_complete", False))
        summary = getattr(r, "summary", "")
        fixes = [f.model_dump() if hasattr(f, "model_dump") else f for f in getattr(r, "priority_fixes", [])]
        sections = [
            s.model_dump(exclude={"original_bullets", "suggested_rewrites"}) if hasattr(s, "model_dump") else s
            for s in getattr(r, "section_feedback", [])
        ]
        reviewed_at = getattr(r, "reviewed_at", datetime.utcnow())
        if hasattr(reviewed_at, "isoformat"):
            reviewed_at = reviewed_at.isoformat()
    else:
        target_role = kwargs.get("target_role", "")
        file_name = kwargs.get("file_name", "")
        file_hash = kwargs.get("file_hash", "")
        rule_score = kwargs.get("rule_score", 0.0)
        ai_score = kwargs.get("ai_score")
        final_score = kwargs.get("final_score")
        ai_complete = bool(kwargs.get("ai_complete", False))
        summary = kwargs.get("summary", "")
        fixes = kwargs.get("priority_fixes", [])
        sections = kwargs.get("section_feedback", [])
        reviewed_at = kwargs.get("reviewed_at", datetime.utcnow().isoformat())

    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO resume_reviews
                (user_id, target_role, file_name, file_hash,
                 rule_score, ai_score, final_score, ai_complete,
                 summary, priority_fixes, section_feedback, origin, reviewed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                target_role,
                file_name,
                file_hash,
                rule_score,
                ai_score,
                final_score,
                1 if ai_complete else 0,
                summary,
                json.dumps(fixes or []),
                json.dumps(sections or []),
                origin,
                reviewed_at,
            ),
        )
        conn.commit()
        return cur.lastrowid  # type: ignore[return-value]
    finally:
        conn.close()


def save_gap_report(*args, **kwargs) -> int:
    """Persist a gap report.
    Accepts either (gap_obj, origin="live") or keyword arguments.
    Returns the new row id.
    """
    user_id = kwargs.get("user_id", 1)
    origin = kwargs.get("origin", "live")
    
    if args and hasattr(args[0], "match_pct"):
        g = args[0]
        if len(args) > 1:
            origin = args[1]
        role = getattr(g, "role", "")
        match_pct = getattr(g, "match_pct", 0.0)
        must_haves = [m.model_dump() if hasattr(m, "model_dump") else m for m in getattr(g, "must_haves", [])]
        good_to_haves = [m.model_dump() if hasattr(m, "model_dump") else m for m in getattr(g, "good_to_haves", [])]
        roadmap = getattr(g, "roadmap", [])
        project_ideas = getattr(g, "project_ideas", [])
        generated_at = getattr(g, "generated_at", datetime.utcnow())
        if hasattr(generated_at, "isoformat"):
            generated_at = generated_at.isoformat()
    else:
        role = kwargs.get("role", "")
        match_pct = kwargs.get("match_pct", 0.0)
        must_haves = kwargs.get("must_haves", [])
        good_to_haves = kwargs.get("good_to_haves", [])
        roadmap = kwargs.get("roadmap", [])
        project_ideas = kwargs.get("project_ideas", [])
        generated_at = kwargs.get("generated_at", datetime.utcnow().isoformat())

    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO gap_reports
                (user_id, role, match_pct, must_haves, good_to_haves, roadmap, project_ideas, origin, generated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                role,
                match_pct,
                json.dumps(must_haves or []),
                json.dumps(good_to_haves or []),
                json.dumps(roadmap or []),
                json.dumps(project_ideas or []),
                origin,
                generated_at,
            ),
        )
        conn.commit()
        return cur.lastrowid  # type: ignore[return-value]
    finally:
        conn.close()


def save_session(
    role: str,
    difficulty: str,
    avg: float,
    report_dict: dict[str, Any],
    answers: list[Any],
    user_id: int = 1,
    origin: str = "live",
) -> int:
    """Persist an interview session. Returns the new row id."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO interview_sessions
                (user_id, role, difficulty, origin, avg_score, report, answers)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                role,
                difficulty,
                origin,
                avg,
                json.dumps(report_dict),
                json.dumps(answers),
            ),
        )
        conn.commit()
        return cur.lastrowid  # type: ignore[return-value]
    finally:
        conn.close()


def score_history(user_id: int = 1, role: Optional[str] = None, limit: int = 50) -> list[dict[str, Any]]:
    """Return recent interview sessions for the user."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        query = """
            SELECT role, difficulty, origin, avg_score, started_at
            FROM interview_sessions
            WHERE user_id = ?
        """
        params: list[Any] = [user_id]
        if role:
            query += " AND role = ?"
            params.append(role)
        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def ats_history(user_id: int = 1, role: Optional[str] = None, limit: int = 50) -> list[dict[str, Any]]:
    """Return recent resume review scores for the user."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        query = """
            SELECT target_role, target_role as role, rule_score, ai_score, final_score, ai_complete, reviewed_at
            FROM resume_reviews
            WHERE user_id = ?
        """
        params: list[Any] = [user_id]
        if role:
            query += " AND target_role = ?"
            params.append(role)
        query += " ORDER BY reviewed_at ASC LIMIT ?"
        params.append(limit)
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def gap_history(user_id: int = 1, role: Optional[str] = None, limit: int = 50) -> list[dict[str, Any]]:
    """Return recent gap reports for the user."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        query = """
            SELECT role, match_pct, origin, generated_at
            FROM gap_reports
            WHERE user_id = ?
        """
        params: list[Any] = [user_id]
        if role:
            query += " AND role = ?"
            params.append(role)
        query += " ORDER BY generated_at DESC LIMIT ?"
        params.append(limit)
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def weak_topic_counts(user_id: int = 1, limit: int = 20) -> dict[str, int]:
    """Aggregate weak topics across all sessions for the user as a dict {topic: count}."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT report FROM interview_sessions WHERE user_id = ?
            """,
            (user_id,),
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    counts: dict[str, int] = {}
    for row in rows:
        try:
            report = json.loads(row["report"])
            for topic in report.get("weak_topics", []):
                counts[topic] = counts.get(topic, 0) + 1
        except (json.JSONDecodeError, TypeError):
            pass

    sorted_topics = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    return dict(sorted_topics)


def get_latest_review(user_id: int = 1) -> dict[str, Any] | None:
    """Return the most recent resume review for the user, or None."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT target_role, target_role as role, file_name, file_hash, rule_score, ai_score,
                   final_score, ai_complete, summary, priority_fixes, section_feedback, reviewed_at
            FROM resume_reviews
            WHERE user_id = ?
            ORDER BY reviewed_at DESC
            LIMIT 1
            """,
            (user_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        d = dict(row)
        try:
            d["priority_fixes"] = json.loads(d["priority_fixes"])
        except Exception:
            pass
        try:
            d["section_feedback"] = json.loads(d["section_feedback"])
        except Exception:
            pass
        return d
    finally:
        conn.close()


def delete_all_data(user_id: int = 1) -> None:
    """Delete all rows for the given user from every table."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM resume_reviews WHERE user_id = ?", (user_id,))
        cur.execute("DELETE FROM gap_reports WHERE user_id = ?", (user_id,))
        cur.execute("DELETE FROM interview_sessions WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()
