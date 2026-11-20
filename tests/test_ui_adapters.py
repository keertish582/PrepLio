"""
tests/test_ui_adapters.py — Unit tests for UI backend adapters and error handling.
"""
import pytest
from core.schemas import Question, ParsedResume
import ui.adapters as A


def test_ollama_status_adapter():
    status = A.get_ollama_status()
    assert isinstance(status, dict)
    assert "available" in status
    assert "model_ready" in status
    assert "message" in status


def test_parse_document_adapter_empty():
    parsed, err = A.parse_document(b"", "empty.pdf")
    assert parsed is None
    assert "short" in err.lower() or "empty" in err.lower() or "failed" in err.lower() or "invalid" in err.lower()


def test_parse_document_adapter_valid_text():
    sample_text = (
        "John Doe\n"
        "john.doe@email.com | 555-0199\n\n"
        "EDUCATION\n"
        "B.S. in Computer Science, State University, 2024\n\n"
        "SKILLS\n"
        "Python, SQL, Git, Docker, REST APIs\n\n"
        "EXPERIENCE\n"
        "Software Engineer Intern\n"
        "Developed backend REST services in Python with FastAPI.\n"
        "Optimized SQL database queries reducing latency by 20%.\n"
    )
    # Test via parser directly with bytes
    import core.parser as P
    parsed = P.extract_resume(sample_text)
    assert parsed.contact.get("email") == "john.doe@email.com"
    assert "Python" in parsed.skills
    assert "SQL" in parsed.skills


def test_run_rule_checks_adapter():
    sample_text = (
        "Jane Smith\n"
        "jane@example.com | 123-456-7890\n\n"
        "PROFESSIONAL SUMMARY\n"
        "Motivated developer with expertise in cloud and distributed systems.\n\n"
        "EXPERIENCE\n"
        "Software Engineer\n"
        "- Built microservices handling 1000 requests per second.\n"
        "- Designed PostgreSQL schema and automated deployments.\n"
        "- Developed automated CI/CD pipeline improving release cadence by 40%.\n\n"
        "EDUCATION\n"
        "B.S. Software Engineering, 2023\n\n"
        "SKILLS\n"
        "Python, Docker, Kubernetes, SQL, Git\n"
    )
    from core.parser import extract_resume
    parsed = extract_resume(sample_text)
    bundle = A.run_rule_checks(parsed)
    assert bundle is not None
    assert bundle.rule_score > 50.0
    assert bundle.max_rule_score == 85.0
    assert len(bundle.checks) > 5


def test_compute_gap_adapter():
    skills = ["Python", "SQL", "Git", "Docker"]
    gap, err = A.compute_gap(skills, "Software Developer")
    assert err == ""
    assert gap is not None
    assert gap.match_pct > 0.0
    assert len(gap.must_haves) > 0
    assert len(gap.roadmap) > 0
    assert len(gap.project_ideas) == 3


def test_generate_questions_fallback():
    # Calling with offline/missing model falls back safely without raising
    qs, err = A.generate_questions("Software Developer", "medium", 3, ["Technical", "Behavioral"])
    assert len(qs) == 3
    for q in qs:
        assert isinstance(q, Question)
        assert q.question_text != ""
        assert len(q.key_points) > 0


def test_evaluate_answer_fallback():
    q = Question(
        number=1,
        category="Technical",
        topic="Python",
        difficulty="medium",
        question_text="Explain Python list comprehension.",
        key_points=["Concise syntax", "Returns new list", "Supports conditions"],
    )
    ans, err = A.evaluate_answer(q, "List comprehension provides a concise way to create lists using a for loop.")
    assert ans is not None
    assert ans.question_number == 1
    assert ans.overall_score >= 0.0
