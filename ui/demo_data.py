"""Synthetic demo data — never claims to be live AI output."""
from __future__ import annotations
from core.schemas import (ParsedResume, RuleCheckBundle, RuleCheckResult,
    ResumeReviewResult, SectionFeedback, PriorityFix,
    GapReport, SkillMatch, Question, InterviewAnswer, InterviewSession)
from datetime import datetime

# ── DEMO RESUME REVIEW — STRONG ──────────────────────────────────────────────
DEMO_REVIEW_STRONG = ResumeReviewResult(
    parsed=ParsedResume(
        raw_text="[Demo resume text — not shown for privacy demo]",
        sections={"Experience":"...", "Education":"...", "Skills":"...", "Projects":"..."},
        skills=["Python","SQL","Docker","Git","REST APIs","System Design"],
        contact={"email":"demo@example.com","phone":"000-000-0000"},
        file_name="demo_strong_resume.pdf", file_size_bytes=85000,
    ),
    rule_bundle=RuleCheckBundle(
        checks=[
            RuleCheckResult(rule_name="has_contact_info", passed=True, score=10, max_score=10, message="Email and phone found", section="Contact"),
            RuleCheckResult(rule_name="has_summary", passed=True, score=5, max_score=5, message="Summary section present", section="Summary"),
            RuleCheckResult(rule_name="has_experience", passed=True, score=15, max_score=15, message="Experience section present", section="Experience"),
            RuleCheckResult(rule_name="has_education", passed=True, score=15, max_score=15, message="Education section present", section="Education"),
            RuleCheckResult(rule_name="has_skills", passed=True, score=10, max_score=10, message="Skills section present", section="Skills"),
            RuleCheckResult(rule_name="bullet_action_verbs", passed=True, score=9, max_score=10, message="Most bullets start with action verbs", section="Experience"),
            RuleCheckResult(rule_name="quantified_achievements", passed=True, score=8, max_score=10, message="Several quantified achievements found", section="Experience"),
            RuleCheckResult(rule_name="no_personal_pronouns", passed=True, score=5, max_score=5, message="No personal pronouns", section="All"),
            RuleCheckResult(rule_name="reasonable_length", passed=True, score=5, max_score=5, message="Appropriate resume length", section="All"),
        ],
        rule_score=82.0, max_rule_score=85.0
    ),
    section_feedback=[
        SectionFeedback(section_name="Experience", score=8.5,
            strengths=["Strong action verbs", "Quantified impact in [X]% improvement metric"],
            weaknesses=["Some bullets are too long", "Missing technology stack context in one role"],
            original_bullets=["Developed backend services for data processing"],
            suggested_rewrites=["Developed Python-based backend services processing [X]M records daily, reducing latency by [X]%"],
            explanation="Experience section is well-structured with measurable outcomes. Recommend adding tech stack to all bullets.",
            ai_generated=False),
        SectionFeedback(section_name="Education", score=9.0,
            strengths=["Degree clearly stated", "Graduation year present"],
            weaknesses=["GPA omitted — include if above 3.5"],
            original_bullets=[], suggested_rewrites=[],
            explanation="Education is clean. If CGPA is strong, add it.", ai_generated=False),
        SectionFeedback(section_name="Skills", score=8.0,
            strengths=["Broad technical coverage", "Grouped by category"],
            weaknesses=["Missing proficiency levels", "Could highlight top 3–5 skills"],
            original_bullets=[], suggested_rewrites=[],
            explanation="Skills section covers the basics but doesn't differentiate level.", ai_generated=False),
    ],
    priority_fixes=[
        PriorityFix(severity="medium", section="Experience", action="Add specific numbers/metrics to all achievement bullets using [X%] format"),
        PriorityFix(severity="medium", section="Skills", action="Add proficiency levels (Expert/Proficient/Familiar) to skills"),
        PriorityFix(severity="low", section="Projects", action="Mention live deployment or GitHub link for each project"),
        PriorityFix(severity="low", section="Summary", action="Tailor summary to target role with 2 specific technology mentions"),
    ],
    ai_score=11.5, ai_assessment_complete=True, final_score=93,
    summary="Strong resume with clear structure and quantified achievements. Minor improvements in metrics specificity recommended.",
    target_role="Software Developer",
    reviewed_at=datetime(2026, 11, 20, 12, 0, 0)
)

# ── DEMO RESUME REVIEW — NEEDS WORK ──────────────────────────────────────────
DEMO_REVIEW_WEAK = ResumeReviewResult(
    parsed=ParsedResume(
        raw_text="[Demo resume text — not shown]",
        sections={"Experience":"...", "Education":"..."},
        skills=["Python","Excel"],
        contact={"email":"demo2@example.com"},
        file_name="demo_weak_resume.pdf", file_size_bytes=42000,
    ),
    rule_bundle=RuleCheckBundle(
        checks=[
            RuleCheckResult(rule_name="has_contact_info", passed=True, score=10, max_score=10, message="Email found (phone missing)", section="Contact"),
            RuleCheckResult(rule_name="has_summary", passed=False, score=0, max_score=5, message="No summary section found", section="Summary"),
            RuleCheckResult(rule_name="has_experience", passed=True, score=15, max_score=15, message="Experience section present", section="Experience"),
            RuleCheckResult(rule_name="has_education", passed=True, score=15, max_score=15, message="Education section present", section="Education"),
            RuleCheckResult(rule_name="has_skills", passed=False, score=0, max_score=10, message="No dedicated skills section", section="Skills"),
            RuleCheckResult(rule_name="bullet_action_verbs", passed=False, score=3, max_score=10, message="Most bullets use passive voice", section="Experience"),
            RuleCheckResult(rule_name="quantified_achievements", passed=False, score=0, max_score=10, message="No quantified achievements found", section="Experience"),
            RuleCheckResult(rule_name="no_personal_pronouns", passed=False, score=0, max_score=5, message="Personal pronouns found (I, my)", section="All"),
            RuleCheckResult(rule_name="reasonable_length", passed=True, score=5, max_score=5, message="Appropriate resume length", section="All"),
        ],
        rule_score=48.0, max_rule_score=85.0
    ),
    section_feedback=[
        SectionFeedback(section_name="Experience", score=4.5,
            strengths=["Relevant job titles"],
            weaknesses=["No action verbs","No metrics","Uses first-person language"],
            original_bullets=["I was responsible for managing the team"],
            suggested_rewrites=["Led a team of [X] engineers delivering [project] on schedule"],
            explanation="Experience bullets need a complete rewrite. Use action verbs + metrics.",
            ai_generated=False),
        SectionFeedback(section_name="Education", score=7.0,
            strengths=["Degree stated clearly"],
            weaknesses=["No CGPA","No relevant coursework"],
            original_bullets=[], suggested_rewrites=[],
            explanation="Add CGPA if strong. List 3–5 relevant courses.", ai_generated=False),
    ],
    priority_fixes=[
        PriorityFix(severity="high", section="Experience", action="Rewrite all bullets starting with strong action verbs (Developed, Built, Led, Designed)"),
        PriorityFix(severity="high", section="Skills", action="Add a dedicated Skills section listing technical tools and languages"),
        PriorityFix(severity="high", section="Summary", action="Add a 2–3 sentence professional summary targeting your role"),
        PriorityFix(severity="high", section="All", action="Remove all first-person pronouns (I, my, me) from resume"),
        PriorityFix(severity="medium", section="Experience", action="Add at least 3 quantified achievements with real numbers"),
        PriorityFix(severity="medium", section="Contact", action="Add phone number to contact section"),
    ],
    ai_score=None, ai_assessment_complete=False, final_score=None,
    summary="Resume needs significant structural improvements before applying. Priority: remove passive voice, add skills section, quantify achievements.",
    target_role="Software Developer",
    reviewed_at=datetime(2026, 11, 20, 10, 0, 0)
)

# ── DEMO GAP REPORT ───────────────────────────────────────────────────────────
DEMO_GAP = GapReport(
    role="Software Developer",
    must_haves=[
        SkillMatch(skill="Python", matched=True, evidence="exact", snippet="Python in Skills section"),
        SkillMatch(skill="Data Structures", matched=True, evidence="fuzzy", snippet="DSA coursework in Education"),
        SkillMatch(skill="Algorithms", matched=True, evidence="fuzzy", snippet="DSA coursework in Education"),
        SkillMatch(skill="SQL", matched=True, evidence="exact", snippet="SQL in Skills section"),
        SkillMatch(skill="Git", matched=True, evidence="exact", snippet="Git in Skills section"),
        SkillMatch(skill="Object-Oriented Programming", matched=False, evidence="not_found", snippet=""),
        SkillMatch(skill="REST APIs", matched=True, evidence="exact", snippet="REST APIs in Projects section"),
    ],
    good_to_haves=[
        SkillMatch(skill="Docker", matched=True, evidence="exact", snippet="Docker in Skills"),
        SkillMatch(skill="Linux", matched=False, evidence="not_found", snippet=""),
        SkillMatch(skill="System Design", matched=False, evidence="not_found", snippet=""),
        SkillMatch(skill="JavaScript", matched=False, evidence="not_found", snippet=""),
        SkillMatch(skill="CI/CD", matched=False, evidence="not_found", snippet=""),
        SkillMatch(skill="Unit Testing", matched=False, evidence="not_found", snippet=""),
        SkillMatch(skill="Cloud (AWS/GCP/Azure)", matched=False, evidence="not_found", snippet=""),
    ],
    match_pct=62.5,
    roadmap=[
        {"week": 1, "focus_skill": "Object-Oriented Programming", "topics": ["Classes & Inheritance", "SOLID Principles", "Design Patterns"], "tasks": ["Refactor a small project OOP", "Implement 3 design patterns"], "completion_evidence": "GitHub repo with OOP project", "resources": ["Python OOP Tutorial", "Head First Design Patterns"]},
        {"week": 2, "focus_skill": "System Design", "topics": ["Scalability", "Load Balancing", "Databases"], "tasks": ["Design a URL shortener", "Design a notification system"], "completion_evidence": "System design diagrams with trade-off notes", "resources": ["System Design Primer", "Designing Data-Intensive Applications"]},
        {"week": 3, "focus_skill": "Linux", "topics": ["Shell commands", "File permissions", "Process management"], "tasks": ["Complete Linux challenge set", "Write 5 shell scripts"], "completion_evidence": "Shell script repository", "resources": ["Linux Command Line book", "OverTheWire: Bandit"]},
    ],
    project_ideas=[
        {"title": "Task Management REST API", "skills_practiced": ["REST APIs","Object-Oriented Programming","SQL","Unit Testing"], "description": "Build a full-featured task management API with authentication, CRUD operations, and pagination.", "deliverables": ["GitHub repo","API documentation","Deployed endpoint","Test suite >80% coverage"]},
        {"title": "DevOps Pipeline Demo", "skills_practiced": ["Docker","CI/CD","Linux","Git"], "description": "Containerize a Python web app and set up automated CI/CD with GitHub Actions.", "deliverables": ["Dockerfile","GitHub Actions workflow","README with architecture diagram"]},
        {"title": "Data Dashboard", "skills_practiced": ["Python","SQL","System Design","Data Visualization"], "description": "Build a dashboard pulling live data from a public API, stored in SQLite, visualized with Plotly.", "deliverables": ["Source code","Live demo","Database schema diagram"]},
    ],
    generated_at=datetime(2026, 11, 20, 12, 30, 0)
)

# ── DEMO QUESTIONS ────────────────────────────────────────────────────────────
DEMO_QUESTIONS = [
    Question(number=1, category="Technical", topic="Python", difficulty="medium",
             question_text="Explain the difference between a list and a tuple in Python and when you'd use each.",
             key_points=["Lists are mutable, tuples are immutable","Tuples are faster for iteration","Use tuples for fixed data (coordinates, DB records)","Lists for dynamic collections"]),
    Question(number=2, category="Technical", topic="Data Structures", difficulty="medium",
             question_text="What is the time complexity of common operations on a hash map?",
             key_points=["Average O(1) for get/set","O(n) worst case due to collisions","Hash functions determine distribution","Load factor affects performance"]),
    Question(number=3, category="Behavioral", topic="Problem Solving", difficulty="medium",
             question_text="Describe a time you debugged a difficult production issue. What was your process?",
             key_points=["Use STAR method","Systematic approach (logs, monitoring)","Root cause analysis","Prevention measures after fix"]),
    Question(number=4, category="System Design", topic="Architecture", difficulty="medium",
             question_text="Design a simple URL shortener service. What components would you use?",
             key_points=["URL encoding (Base62)","Database design (key-value store)","Cache for hot URLs","Redirect handling (301 vs 302)","Scalability considerations"]),
    Question(number=5, category="Technical", topic="REST APIs", difficulty="easy",
             question_text="What are the HTTP methods and when should each be used in a REST API?",
             key_points=["GET — read, POST — create, PUT/PATCH — update, DELETE — remove","Idempotency for GET/PUT/DELETE","Status codes (200, 201, 400, 404, 500)","RESTful conventions"]),
]

# ── DEMO INTERVIEW ────────────────────────────────────────────────────────────
DEMO_INTERVIEW_ANSWERS = [
    InterviewAnswer(question_number=1, question_text=DEMO_QUESTIONS[0].question_text,
                    answer_text="Lists are mutable meaning you can change them after creation, while tuples are immutable. I use tuples when I want data to stay constant like a coordinate pair.",
                    correctness=8.0, clarity=9.0, depth=7.0, overall_score=8.0,
                    covered_points=["Lists are mutable, tuples are immutable","Use tuples for fixed data"],
                    missed_points=["Tuples are faster for iteration","Load factor affects performance"],
                    feedback="Good fundamental understanding. Add performance characteristics and practical examples to deepen your answer."),
    InterviewAnswer(question_number=2, question_text=DEMO_QUESTIONS[1].question_text,
                    answer_text="O(1) average for lookups, but worst case is O(n) if there are many collisions.",
                    correctness=7.0, clarity=8.0, depth=5.0, overall_score=6.75,
                    covered_points=["Average O(1) for get/set","O(n) worst case due to collisions"],
                    missed_points=["Hash functions determine distribution","Load factor affects performance"],
                    feedback="Covers the basics. Mention load factor and rehashing to show deeper knowledge."),
]

DEMO_SESSION = InterviewSession(
    role="Software Developer", difficulty="medium", mode="coaching",
    questions=DEMO_QUESTIONS[:2],
    answers=DEMO_INTERVIEW_ANSWERS,
    avg_score=7.375,
    category_scores={"Technical": 7.375},
    strengths=["Python basics","Hash map complexity"],
    weak_topics=["Data Structures depth","System Design"],
    practice_plan=["Review hash map internals","Practice system design problems","Study Python performance characteristics"],
    completed=True,
    started_at=datetime(2026, 11, 20, 14, 0, 0),
    completed_at=datetime(2026, 11, 20, 14, 45, 0)
)
