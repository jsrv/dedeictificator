import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from audit_clarity import audit_text, main


def test_detects_deictic_and_psycholinguistic_failures():
    messy = (
        "It started failing earlier after they deployed the retry queue buffer manager update above. "
        "This caused the worker to eat its memory budget, and the latter refused to drain it. "
        "We need to calendar a follow-up and sunset that soon."
    )
    report = audit_text(messy)
    rules = {f.rule for f in report.findings}

    assert report.clarity_score < 60
    assert "initial_unanchored_pronoun" in rules
    assert "broad_demonstrative" in rules
    assert "spatial_discourse_deixis" in rules
    assert "temporal_deixis" in rules
    assert "stacked_noun_chain" in rules
    assert "denominal_verb" in rules
    assert "inanimate_agency" in rules


def test_clean_self_contained_text_scores_high():
    clean = (
        "The payments service began returning HTTP 503 errors on November 12, 2026, "
        "after the platform team deployed v2.8 of the manager that buffers the retry queue. "
        "That deployment caused the ingestion worker to exceed its 4 GB memory limit."
    )
    report = audit_text(clean)
    assert report.clarity_score >= 90
    assert report.deictic_flags == 0


def test_ignores_code_blocks_and_expletive_it():
    text = (
        "It is clear that the function `this_above_now_calendar_eat()` works reliably. "
        "There are two integration tests in the repository."
    )
    report = audit_text(text)
    assert report.deictic_flags == 0
    assert report.psycholinguistic_flags == 0


def test_reduced_object_relative_clause_detection():
    text = "The migration script the engineer wrote failed during staging."
    report = audit_text(text)
    rules = {f.rule for f in report.findings}
    assert "reduced_object_relative" in rules


def test_cli_min_score_gate():
    exit_fail = main(["--text", "This fails here now.", "--min-score", "95"])
    exit_pass = main(
        ["--text", "The billing worker validates every invoice.", "--min-score", "80"]
    )
    assert exit_fail == 1
    assert exit_pass == 0
