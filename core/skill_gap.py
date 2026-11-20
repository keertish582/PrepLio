"""
core/skill_gap.py — B2: Role Knowledge + Skill Gap Matching
"""
from __future__ import annotations

import functools
import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

from rapidfuzz import fuzz

from core.schemas import GapReport, SkillMatch

logger = logging.getLogger(__name__)

ROLES_DIR = Path(__file__).parent.parent / "data" / "roles"
FUZZY_THRESHOLD = 80  # rapidfuzz token_sort_ratio threshold


# ---------------------------------------------------------------------------
# Role loader (cached)
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def load_roles() -> dict[str, dict]:
    """
    Load all JSON files from data/roles/.
    Returns {role_name: role_data} dict. Cached after first load.
    """
    roles: dict[str, dict] = {}
    if not ROLES_DIR.exists():
        logger.warning("Roles directory not found: %s", ROLES_DIR)
        return roles

    for json_file in ROLES_DIR.glob("*.json"):
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
            role_name = data.get("role", json_file.stem.replace("_", " ").title())
            roles[role_name] = data
        except Exception as exc:
            logger.warning("Failed to load role file %s: %s", json_file, exc)

    return roles


def _reload_roles() -> dict[str, dict]:
    """Force-reload roles (clears LRU cache)."""
    load_roles.cache_clear()
    return load_roles()


# ---------------------------------------------------------------------------
# Skill matching helpers
# ---------------------------------------------------------------------------

def _normalize(s: str) -> str:
    return s.lower().strip()


def _match_skill(resume_skills_normalized: list[str], target_skill: str, aliases: dict) -> tuple[bool, str]:
    """
    Try to match target_skill against resume_skills_normalized.
    Returns (matched: bool, evidence: str) where evidence is 'exact', 'alias', 'fuzzy', or 'not_found'.
    """
    t_norm = _normalize(target_skill)

    # 1. Exact match
    if t_norm in resume_skills_normalized:
        return True, "exact"

    # 2. Alias match
    alias_list = aliases.get(target_skill, [])
    for alias in alias_list:
        a_norm = _normalize(alias)
        if a_norm in resume_skills_normalized:
            return True, "alias"
        # Also check if any resume skill contains this alias
        for rs in resume_skills_normalized:
            if a_norm in rs or rs in a_norm:
                return True, "alias"

    # 3. Fuzzy match
    for rs in resume_skills_normalized:
        score = fuzz.token_sort_ratio(t_norm, rs)
        if score >= FUZZY_THRESHOLD:
            return True, "fuzzy"

    return False, "not_found"


# ---------------------------------------------------------------------------
# Main gap computation
# ---------------------------------------------------------------------------

def compute_gap(
    resume_skills: list[str],
    role_name: str,
    jd_skills: Optional[dict] = None,
) -> GapReport:
    """
    Compute skill gap between resume_skills and the target role.

    Args:
        resume_skills: List of skills extracted from resume.
        role_name: Name of target role (must match a loaded role key).
        jd_skills: Optional dict with 'must_haves' and 'good_to_haves' overriding role data.

    Returns:
        GapReport populated with match details and percentage.
    """
    roles = load_roles()

    if jd_skills:
        role_data = {
            "role": role_name,
            "must_haves": jd_skills.get("must_haves", []),
            "good_to_haves": jd_skills.get("good_to_haves", []),
            "aliases": jd_skills.get("aliases", {}),
        }
    else:
        # Find role (case-insensitive fuzzy match on role name)
        role_data = None
        for rname, rdata in roles.items():
            if _normalize(rname) == _normalize(role_name):
                role_data = rdata
                break
        if not role_data:
            # Try partial match
            for rname, rdata in roles.items():
                if _normalize(role_name) in _normalize(rname) or _normalize(rname) in _normalize(role_name):
                    role_data = rdata
                    break
        if not role_data:
            logger.warning("Role '%s' not found. Using empty role data.", role_name)
            role_data = {"role": role_name, "must_haves": [], "good_to_haves": [], "aliases": {}}

    must_haves_raw: list[str] = role_data.get("must_haves", [])
    good_to_haves_raw: list[str] = role_data.get("good_to_haves", [])
    aliases: dict = role_data.get("aliases", {})

    resume_skills_normalized = [_normalize(s) for s in resume_skills if s.strip()]

    must_have_matches: list[SkillMatch] = []
    good_to_have_matches: list[SkillMatch] = []

    matched_must = 0
    matched_good = 0

    for skill in must_haves_raw:
        matched, evidence = _match_skill(resume_skills_normalized, skill, aliases)
        must_have_matches.append(SkillMatch(
            skill=skill,
            matched=matched,
            evidence=evidence,
            snippet="",
        ))
        if matched:
            matched_must += 1

    for skill in good_to_haves_raw:
        matched, evidence = _match_skill(resume_skills_normalized, skill, aliases)
        good_to_have_matches.append(SkillMatch(
            skill=skill,
            matched=matched,
            evidence=evidence,
            snippet="",
        ))
        if matched:
            matched_good += 1

    # Weighted match percentage: must-haves count double
    total_must = len(must_haves_raw)
    total_good = len(good_to_haves_raw)
    denominator = total_must * 2 + total_good
    if denominator > 0:
        match_pct = (matched_must * 2 + matched_good) / denominator * 100
    else:
        match_pct = 0.0

    gap = GapReport(
        role=role_data.get("role", role_name),
        must_haves=must_have_matches,
        good_to_haves=good_to_have_matches,
        match_pct=round(match_pct, 1),
    )

    # Build roadmap and project ideas
    gap.roadmap = build_roadmap(gap)
    gap.project_ideas = build_project_ideas(gap)

    return gap


# ---------------------------------------------------------------------------
# JD skill extractor
# ---------------------------------------------------------------------------

def extract_jd_skills(jd_text: str) -> dict[str, list[str]]:
    """
    Naive NLP extraction from job description text.
    Lines containing 'required'/'must'/'essential' -> must_haves.
    Rest -> good_to_haves.

    Returns {"must_haves": [...], "good_to_haves": [...]}
    """
    must_haves: list[str] = []
    good_to_haves: list[str] = []

    must_keywords = re.compile(r"\b(required|must|essential|mandatory|necessary)\b", re.IGNORECASE)

    # Common tech skill patterns to extract
    skill_pattern = re.compile(
        r"\b([A-Z][a-zA-Z0-9+#.]*(?:\s+[A-Z][a-zA-Z0-9+#.]*){0,2}|"
        r"[a-z][a-zA-Z0-9+#.]{2,}(?:\.[a-z]+)?)\b"
    )

    seen: set[str] = set()

    for line in jd_text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Extract candidate skill tokens from the line
        tokens: list[str] = []
        # Split by common delimiters
        parts = re.split(r"[,;|/]", line)
        for part in parts:
            p = part.strip().lstrip("•·-–▪▸ ")
            if 2 < len(p) < 60:
                tokens.append(p)

        is_must = bool(must_keywords.search(line))

        for token in tokens:
            if token.lower() in seen:
                continue
            seen.add(token.lower())
            if is_must:
                must_haves.append(token)
            else:
                good_to_haves.append(token)

    return {"must_haves": must_haves[:20], "good_to_haves": good_to_haves[:20]}


# ---------------------------------------------------------------------------
# Roadmap builder
# ---------------------------------------------------------------------------

def build_roadmap(gap: GapReport) -> list[dict]:
    """
    Create a week-by-week roadmap for missing must-have skills.
    Returns list of week dicts.
    """
    missing_must = [sm.skill for sm in gap.must_haves if not sm.matched]

    if not missing_must:
        return []

    roadmap: list[dict] = []
    for week_num, skill in enumerate(missing_must, start=1):
        skill_lower = skill.lower()
        entry = {
            "week": week_num,
            "focus_skill": skill,
            "topics": _topics_for_skill(skill),
            "tasks": [
                f"Complete an introductory tutorial on {skill}",
                f"Build a small hands-on exercise using {skill}",
                f"Read documentation and understand core concepts of {skill}",
                f"Complete 2-3 practice problems or mini-projects with {skill}",
            ],
            "completion_evidence": f"Demonstrate {skill} usage in a project or contribute to an open-source repo using {skill}",
            "resources": _resources_for_skill(skill),
        }
        roadmap.append(entry)

    return roadmap


def _topics_for_skill(skill: str) -> list[str]:
    skill_lower = skill.lower()
    topic_map = {
        "python": ["Variables, types, and control flow", "Functions and OOP", "Libraries: requests, json, os", "Testing with pytest"],
        "sql": ["SELECT, WHERE, JOIN", "Aggregations and GROUP BY", "Subqueries and CTEs", "Indexing and query optimization"],
        "git": ["Repository basics (init, clone)", "Branching and merging", "Pull requests and code review", "Conflict resolution"],
        "docker": ["Containers vs VMs", "Dockerfile authoring", "docker-compose", "Container networking"],
        "machine learning": ["Supervised vs unsupervised learning", "Model training and evaluation", "Cross-validation and overfitting", "scikit-learn pipeline"],
        "react": ["JSX and components", "State and props", "Hooks (useState, useEffect)", "Component lifecycle"],
        "aws": ["IAM and security basics", "EC2 and S3", "Lambda serverless", "VPC and networking"],
    }
    for key, topics in topic_map.items():
        if key in skill_lower:
            return topics
    return [
        f"Core fundamentals of {skill}",
        f"Common patterns and best practices for {skill}",
        f"Integrating {skill} in real projects",
        f"Advanced {skill} concepts",
    ]


def _resources_for_skill(skill: str) -> list[str]:
    skill_lower = skill.lower()
    resource_map = {
        "python": ["docs.python.org", "realpython.com", "Python Crash Course (book)", "Codecademy Python course"],
        "sql": ["SQLZoo (sqlzoo.net)", "Mode Analytics SQL Tutorial", "PostgreSQL Documentation", "W3Schools SQL"],
        "git": ["git-scm.com/doc", "learngitbranching.js.org", "GitHub Docs", "Atlassian Git Tutorial"],
        "docker": ["docs.docker.com", "Docker Getting Started Tutorial", "Play with Docker (labs.play-with-docker.com)"],
        "machine learning": ["fast.ai", "Coursera Machine Learning (Andrew Ng)", "scikit-learn docs", "Kaggle Learn"],
        "react": ["react.dev", "Scrimba React Course", "Full Stack Open (fullstackopen.com)", "React by Example"],
        "aws": ["AWS Free Tier", "AWS Documentation", "A Cloud Guru", "AWS Skill Builder"],
    }
    for key, resources in resource_map.items():
        if key in skill_lower:
            return resources
    return [
        f"Official {skill} documentation",
        f"YouTube tutorials on {skill}",
        f"Udemy / Coursera courses on {skill}",
        f"GitHub repositories with {skill} examples",
    ]


# ---------------------------------------------------------------------------
# Project idea builder
# ---------------------------------------------------------------------------

def build_project_ideas(gap: GapReport) -> list[dict]:
    """
    Create 3 project ideas targeting missing skills.
    """
    missing_skills = [sm.skill for sm in gap.must_haves if not sm.matched]
    missing_skills += [sm.skill for sm in gap.good_to_haves if not sm.matched]

    if not missing_skills:
        missing_skills = [sm.skill for sm in gap.must_haves[:3]]

    role = gap.role
    ideas: list[dict] = []

    # Idea 1: CLI / utility tool
    focus_1 = missing_skills[:2] if len(missing_skills) >= 2 else missing_skills
    ideas.append({
        "title": f"{role} Portfolio CLI Tool",
        "skills_practiced": focus_1,
        "description": f"Build a command-line tool that demonstrates {', '.join(focus_1)} skills relevant to {role} work. Focus on clean architecture and error handling.",
        "deliverables": [
            "Working CLI with at least 3 commands",
            "README with installation and usage",
            "Unit tests with 60%+ coverage",
            "GitHub repository with commit history",
        ],
    })

    # Idea 2: Web API / backend
    focus_2 = missing_skills[1:4] if len(missing_skills) >= 3 else missing_skills
    ideas.append({
        "title": f"{role} REST API Project",
        "skills_practiced": focus_2,
        "description": f"Create a RESTful API or backend service using {', '.join(focus_2[:2])}. Include authentication, data persistence, and documentation.",
        "deliverables": [
            "API with CRUD endpoints",
            "Database integration (SQLite or PostgreSQL)",
            "Authentication (JWT or API key)",
            "Postman collection or Swagger docs",
        ],
    })

    # Idea 3: End-to-end application
    focus_3 = missing_skills[:3] if len(missing_skills) >= 3 else missing_skills
    ideas.append({
        "title": f"End-to-End {role} Capstone Project",
        "skills_practiced": focus_3,
        "description": f"Build a complete, deployable application that integrates {', '.join(focus_3)} in a realistic {role} scenario. Deploy to a cloud platform.",
        "deliverables": [
            "Full working application",
            "Deployment to Heroku / Railway / Vercel / AWS",
            "CI/CD pipeline (GitHub Actions)",
            "Demo video or live URL",
        ],
    })

    return ideas[:3]
