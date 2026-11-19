import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from audit_clarity import audit_text, main


class TestAuditClarity(unittest.TestCase):
    def test_detects_deictic_and_psycholinguistic_failures(self) -> None:
        messy = (
            "It started failing earlier after they deployed the retry queue buffer manager update above. "
            "This caused the worker to eat its memory budget, and the latter refused to drain it. "
            "We need to calendar a follow-up and sunset that soon."
        )
        report = audit_text(messy)
        rules = {f.rule for f in report.findings}

        self.assertLess(report.clarity_score, 60)
        self.assertIn("initial_unanchored_pronoun", rules)
        self.assertIn("broad_demonstrative", rules)
        self.assertIn("spatial_discourse_deixis", rules)
        self.assertIn("temporal_deixis", rules)
        self.assertIn("stacked_noun_chain", rules)
        self.assertIn("denominal_verb", rules)
        self.assertIn("inanimate_agency", rules)

    def test_clean_self_contained_text_scores_high(self) -> None:
        clean = (
            "The payments service began returning HTTP 503 errors on November 12, 2026, "
            "after the platform team deployed v2.8 of the manager that buffers the retry queue. "
            "That deployment caused the ingestion worker to exceed its 4 GB memory limit."
        )
        report = audit_text(clean)
        self.assertGreaterEqual(report.clarity_score, 90)
        self.assertEqual(report.deictic_flags, 0)

    def test_ignores_code_blocks_expletives_and_markdown_urls(self) -> None:
        text = (
            "# Overview\n\n"
            "It is clear that `this_above_now_calendar_eat()` works reliably in "
            "[Clark et al.](https://arxiv.org/abs/2610.29162).\n"
            "There are two integration tests in the repository.\n"
        )
        report = audit_text(text)
        self.assertEqual(report.deictic_flags, 0)
        self.assertEqual(report.psycholinguistic_flags, 0)

    def test_reduced_object_relative_clause_detection(self) -> None:
        text = "The migration script the engineer wrote failed during staging."
        report = audit_text(text)
        rules = {f.rule for f in report.findings}
        self.assertIn("reduced_object_relative", rules)

    def test_cli_min_score_gate(self) -> None:
        exit_fail = main(["--text", "This fails here now.", "--min-score", "95"])
        exit_pass = main(
            [
                "--text",
                "The billing worker validates every invoice.",
                "--min-score",
                "80",
            ]
        )
        self.assertEqual(exit_fail, 1)
        self.assertEqual(exit_pass, 0)

    def test_ignores_yaml_frontmatter_quoted_mentions_and_comma_lists(self) -> None:
        skill_doc = (
            "---\n"
            "name: demo-skill\n"
            "description: Audit, score, and rewrite text with stacked nouns, reduced clauses, and long spans.\n"
            "---\n\n"
            "# Demo Skill\n\n"
            'Avoid unanchored pointers like "here", "above", and "recently" across prose, documentation, prompts.\n'
            "Use the Clarity Scorecard, a concise table, to report results.\n"
        )
        report = audit_text(skill_doc)
        self.assertEqual(report.deictic_flags, 0)
        self.assertEqual(report.psycholinguistic_flags, 0)
        self.assertGreaterEqual(report.clarity_score, 90)


if __name__ == "__main__":
    unittest.main()
