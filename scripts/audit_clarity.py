#!/usr/bin/env python3
"""Deterministic analyzer for deictic ambiguity and psycholinguistic processing cost.

Implements heuristic detectors for:
1. Referential & deictic ambiguity (broad demonstratives, unanchored pronouns,
   spatial/discourse pointers, and relative temporal markers).
2. Psycholinguistic processing difficulty features studied in Clark, Martin, &
   Mahowald (2026), "Why is AI-generated language so hard to understand?"
   (arXiv:2610.29162): stacked noun phrases, reduced object relative clauses,
   denominal verbs, inanimate-subject + animate-verb pairings, long subject-verb
   dependency distances, and telegraphic information compression.

Zero external dependencies (Python 3.9+ standard library only).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

DEMONSTRATIVES = {"this", "that", "these", "those"}
PRONOUNS = {"it", "its", "they", "them", "their", "theirs"}
SPATIAL_DISCOURSE = {
    "here",
    "there",
    "above",
    "below",
    "aforementioned",
    "former",
    "latter",
    "elsewhere",
}
TEMPORAL_DEIXIS = {
    "now",
    "currently",
    "recently",
    "today",
    "yesterday",
    "tomorrow",
    "soon",
    "earlier",
    "later",
}

DENOMINAL_VERBS = {
    "calendar",
    "calendared",
    "calendaring",
    "footnote",
    "footnoted",
    "footnoting",
    "action",
    "actioned",
    "actioning",
    "sunset",
    "sunsetted",
    "sunsetting",
    "architect",
    "architected",
    "architecting",
    "bucket",
    "bucketed",
    "bucketing",
    "message",
    "messaged",
    "messaging",
    "surface",
    "surfaced",
    "surfacing",
    "leverage",
    "leveraged",
    "leveraging",
    "impact",
    "impacted",
    "impacting",
}

ANIMATE_VERBS = {
    "eat",
    "eats",
    "eating",
    "ate",
    "want",
    "wants",
    "wanted",
    "think",
    "thinks",
    "thought",
    "decide",
    "decides",
    "decided",
    "refuse",
    "refuses",
    "refused",
    "struggle",
    "struggles",
    "struggled",
    "demand",
    "demands",
    "demanded",
    "sleep",
    "sleeps",
    "slept",
    "care",
    "cares",
    "cared",
    "learn",
    "learns",
    "learned",
}

INANIMATE_HEADS = {
    "sentence",
    "conversation",
    "code",
    "codebase",
    "system",
    "model",
    "pipeline",
    "server",
    "database",
    "query",
    "function",
    "module",
    "architecture",
    "document",
    "paper",
    "metric",
    "budget",
    "process",
    "service",
    "api",
    "request",
    "response",
    "error",
    "bug",
}

FUNCTION_WORDS = {
    "the",
    "a",
    "an",
    "of",
    "to",
    "in",
    "for",
    "on",
    "with",
    "at",
    "by",
    "from",
    "as",
    "into",
    "like",
    "through",
    "after",
    "over",
    "between",
    "out",
    "against",
    "during",
    "without",
    "before",
    "under",
    "around",
    "among",
    "that",
    "which",
    "who",
    "whom",
    "whose",
    "and",
    "but",
    "or",
    "so",
    "yet",
    "if",
    "because",
    "while",
    "although",
    "though",
    "when",
    "where",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "shall",
    "should",
    "can",
    "could",
    "may",
    "might",
    "must",
}

COMMON_VERBS_AFTER_DEMO = {
    "is",
    "was",
    "are",
    "were",
    "means",
    "shows",
    "proves",
    "causes",
    "creates",
    "leads",
    "makes",
    "helps",
    "allows",
    "prevents",
    "requires",
    "suggests",
    "indicates",
    "highlights",
    "matters",
    "works",
    "fails",
    "breaks",
    "happens",
    "occurs",
    "can",
    "could",
    "will",
    "would",
    "should",
    "may",
    "might",
    "must",
    "has",
    "have",
    "had",
}

TOKEN_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*|\d+(?:\.\d+)?|[^\w\s]")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])")
CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```|`[^`\n]+`")


@dataclass
class Finding:
    sentence_index: int
    category: str
    rule: str
    severity: str
    span: str
    explanation: str
    suggestion: str


@dataclass
class AuditReport:
    clarity_score: int
    deictic_flags: int
    psycholinguistic_flags: int
    sentence_count: int
    word_count: int
    lexical_density: float
    avg_sentence_length: float
    findings: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "clarity_score": self.clarity_score,
            "deictic_flags": self.deictic_flags,
            "psycholinguistic_flags": self.psycholinguistic_flags,
            "sentence_count": self.sentence_count,
            "word_count": self.word_count,
            "lexical_density": round(self.lexical_density, 3),
            "avg_sentence_length": round(self.avg_sentence_length, 1),
            "findings": [asdict(f) for f in self.findings],
        }


def strip_protected_spans(text: str) -> str:
    """Replace fenced/inline code with neutral placeholders so code syntax is ignored."""
    return CODE_BLOCK_RE.sub(" CODE_SPAN ", text)


def split_sentences(text: str) -> list[str]:
    cleaned = text.strip()
    if not cleaned:
        return []
    return [p.strip() for p in SENTENCE_SPLIT_RE.split(cleaned) if p.strip()]


def tokenize_words(sentence: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(sentence) if re.match(r"^[A-Za-z]", t)]


def is_likely_noun(word: str) -> bool:
    lw = word.lower()
    if lw in FUNCTION_WORDS or lw in DEMONSTRATIVES or lw in PRONOUNS:
        return False
    if lw in SPATIAL_DISCOURSE or lw in TEMPORAL_DEIXIS:
        return False
    if lw.endswith(("ly", "ed", "ing", "ous", "ive", "able", "ible", "ful", "less")):
        return False
    return len(lw) >= 3


def analyze_sentence(idx: int, sentence: str) -> list[Finding]:
    findings: list[Finding] = []
    words = tokenize_words(sentence)
    lower_words = [w.lower() for w in words]
    n = len(lower_words)
    if n == 0:
        return findings

    # 1. Broad demonstrative deixis ("This causes...", "That is why...")
    for i, w in enumerate(lower_words):
        if w in DEMONSTRATIVES:
            next_w = lower_words[i + 1] if i + 1 < n else ""
            if i == 0 and (next_w in COMMON_VERBS_AFTER_DEMO or next_w == ""):
                findings.append(
                    Finding(
                        sentence_index=idx,
                        category="deixis",
                        rule="broad_demonstrative",
                        severity="high",
                        span=f"{words[i]} {words[i + 1]}".strip()
                        if i + 1 < n
                        else words[i],
                        explanation="Sentence-initial demonstrative lacks a concrete head noun.",
                        suggestion=f"Add an explicit noun phrase after '{words[i]}' (e.g., '{words[i]} behavior').",
                    )
                )
            elif next_w in {"is", "was", "means", "proves", "shows"} and i > 0:
                prev_w = lower_words[i - 1]
                if prev_w in {"and", "but", "so", "which"}:
                    findings.append(
                        Finding(
                            sentence_index=idx,
                            category="deixis",
                            rule="broad_demonstrative",
                            severity="medium",
                            span=f"{words[i]} {words[i + 1]}",
                            explanation="Clause-level demonstrative refers to an entire prior proposition.",
                            suggestion="Name the specific outcome or mechanism instead of using a bare demonstrative.",
                        )
                    )

    # 2. Unanchored third-person pronouns (especially sentence-initial or multi-entity)
    capitalized_entities = [
        w
        for i, w in enumerate(words)
        if i > 0 and w[0].isupper() and w.lower() not in FUNCTION_WORDS
    ]
    for i, w in enumerate(lower_words):
        if w in PRONOUNS:
            # Skip dummy/expletive "It is/was <adj/verb>" at sentence start
            if (
                i == 0
                and w == "it"
                and i + 1 < n
                and lower_words[i + 1] in {"is", "was", "seems", "appears"}
            ):
                continue
            if i == 0:
                findings.append(
                    Finding(
                        sentence_index=idx,
                        category="deixis",
                        rule="initial_unanchored_pronoun",
                        severity="high",
                        span=words[i],
                        explanation="Sentence opens with a pronoun whose referent depends on an earlier sentence.",
                        suggestion=f"Replace '{words[i]}' with the explicit entity name.",
                    )
                )
            elif len(set(capitalized_entities)) >= 2:
                findings.append(
                    Finding(
                        sentence_index=idx,
                        category="deixis",
                        rule="competing_antecedent_pronoun",
                        severity="medium",
                        span=words[i],
                        explanation="Multiple named entities appear in the sentence, creating antecedent ambiguity.",
                        suggestion=f"Replace '{words[i]}' with the exact entity name.",
                    )
                )

    # 3. Spatial & discourse deixis
    for i, w in enumerate(lower_words):
        if w in SPATIAL_DISCOURSE:
            if (
                w == "there"
                and i + 1 < n
                and lower_words[i + 1] in {"is", "are", "was", "were"}
            ):
                continue
            findings.append(
                Finding(
                    sentence_index=idx,
                    category="deixis",
                    rule="spatial_discourse_deixis",
                    severity="medium",
                    span=words[i],
                    explanation=f"'{words[i]}' relies on document layout or conversational position that breaks when quoted or moved.",
                    suggestion="Replace with an explicit section title, file path, or entity label.",
                )
            )

    # 4. Relative temporal deixis
    for i, w in enumerate(lower_words):
        if w in TEMPORAL_DEIXIS:
            findings.append(
                Finding(
                    sentence_index=idx,
                    category="deixis",
                    rule="temporal_deixis",
                    severity="medium",
                    span=words[i],
                    explanation=f"'{words[i]}' is relative to utterance time and becomes stale or ambiguous later.",
                    suggestion="Anchor to an explicit date, release version, or system condition.",
                )
            )

    # 5. Stacked noun chains (Clark et al. 2026: dense nominal compounds)
    run: list[str] = []
    for i, orig in enumerate(words):
        if orig == "CODE_SPAN":
            if len(run) >= 3:
                findings.append(
                    Finding(
                        sentence_index=idx,
                        category="psycholinguistic",
                        rule="stacked_noun_chain",
                        severity="medium",
                        span=" ".join(run),
                        explanation="3+ consecutive nouns/modifiers compress relations and increase working-memory load.",
                        suggestion="Unpack the noun stack using prepositions ('of', 'for') or a clarifying clause.",
                    )
                )
            run = []
            continue
        if is_likely_noun(orig) and (i == 0 or not orig[0].isupper()):
            run.append(orig)
        else:
            if len(run) >= 3:
                findings.append(
                    Finding(
                        sentence_index=idx,
                        category="psycholinguistic",
                        rule="stacked_noun_chain",
                        severity="medium",
                        span=" ".join(run),
                        explanation="3+ consecutive nouns/modifiers compress relations and increase working-memory load.",
                        suggestion="Unpack the noun stack using prepositions ('of', 'for') or a clarifying clause.",
                    )
                )
            run = []
    if len(run) >= 3:
        findings.append(
            Finding(
                sentence_index=idx,
                category="psycholinguistic",
                rule="stacked_noun_chain",
                severity="medium",
                span=" ".join(run),
                explanation="3+ consecutive nouns/modifiers compress relations and increase working-memory load.",
                suggestion="Unpack the noun stack using prepositions ('of', 'for') or a clarifying clause.",
            )
        )

    # 6. Denominal verbs (Clark et al. 2026: "calendar it", "footnote it")
    for i, w in enumerate(lower_words):
        if w in DENOMINAL_VERBS:
            prev_w = lower_words[i - 1] if i > 0 else ""
            if prev_w not in {
                "the",
                "a",
                "an",
                "this",
                "that",
                "my",
                "our",
                "your",
                "their",
            }:
                findings.append(
                    Finding(
                        sentence_index=idx,
                        category="psycholinguistic",
                        rule="denominal_verb",
                        severity="low",
                        span=words[i],
                        explanation=f"'{words[i]}' appears used as a compressed denominal verb.",
                        suggestion="Prefer a standard verb phrase (e.g., 'schedule', 'add a footnote', 'deprecate').",
                    )
                )

    # 7. Inanimate subject + animate verb (Clark et al. 2026)
    for i in range(n - 1):
        if lower_words[i] in INANIMATE_HEADS:
            window = lower_words[i + 1 : min(n, i + 5)]
            for vw in window:
                if vw in ANIMATE_VERBS:
                    findings.append(
                        Finding(
                            sentence_index=idx,
                            category="psycholinguistic",
                            rule="inanimate_agency",
                            severity="medium",
                            span=f"{words[i]} ... {vw}",
                            explanation="Inanimate subject paired with a volitional/biological verb increases semantic processing effort.",
                            suggestion="Attribute the action to an explicit actor or describe the literal mechanism.",
                        )
                    )
                    break

    # 8. Reduced object relative clause heuristic: [Det] [Noun] [Pronoun (he/she/they/we/you/I)] [Verb]
    rel_pronouns = {"he", "she", "they", "we", "you", "i"}
    for i in range(n - 3):
        if (
            lower_words[i] in {"a", "an", "the"}
            and is_likely_noun(words[i + 1])
            and lower_words[i + 2] in rel_pronouns
            and lower_words[i + 3] not in FUNCTION_WORDS
        ):
            findings.append(
                Finding(
                    sentence_index=idx,
                    category="psycholinguistic",
                    rule="reduced_object_relative",
                    severity="medium",
                    span=" ".join(words[i : i + 4]),
                    explanation="Possible object relative clause omitting overt relativizer 'that' or 'which'.",
                    suggestion=f"Insert 'that' before '{words[i + 2]}' to prevent garden-path misreading.",
                )
            )

    # 9. Long sentence / dependency span proxy (> 28 words or heavy parenthetical embedding)
    if n > 28 or sentence.count(",") >= 3 or sentence.count("--") >= 2:
        findings.append(
            Finding(
                sentence_index=idx,
                category="psycholinguistic",
                rule="long_dependency_span",
                severity="medium",
                span=f"{words[0]} {words[1]} ... ({n} words)",
                explanation="High token span or multi-clause embedding strains human working memory.",
                suggestion="Split into two shorter sentences or move subordinate clauses after the main verb.",
            )
        )

    return findings


def audit_text(text: str) -> AuditReport:
    clean_text = strip_protected_spans(text)
    sentences = split_sentences(clean_text)
    all_words = tokenize_words(clean_text)
    word_count = len(all_words)

    if word_count == 0:
        return AuditReport(
            clarity_score=100,
            deictic_flags=0,
            psycholinguistic_flags=0,
            sentence_count=0,
            word_count=0,
            lexical_density=0.0,
            avg_sentence_length=0.0,
            findings=[],
        )

    findings: list[Finding] = []
    for idx, sent in enumerate(sentences, start=1):
        findings.extend(analyze_sentence(idx, sent))

    content_words = [w for w in all_words if w.lower() not in FUNCTION_WORDS]
    lexical_density = len(content_words) / word_count
    avg_sentence_length = word_count / max(1, len(sentences))

    deictic_flags = sum(1 for f in findings if f.category == "deixis")
    psych_flags = sum(1 for f in findings if f.category == "psycholinguistic")

    # Penalty weighted by severity and normalized gently by text length
    severity_weights = {"high": 9.0, "medium": 5.0, "low": 2.5}
    raw_penalty = sum(severity_weights.get(f.severity, 4.0) for f in findings)
    norm_factor = max(1.0, len(sentences) / 2.5)
    density_penalty = max(0.0, (lexical_density - 0.62) * 45.0)
    score = round(
        max(0.0, min(100.0, 100.0 - (raw_penalty / norm_factor) - density_penalty))
    )

    return AuditReport(
        clarity_score=score,
        deictic_flags=deictic_flags,
        psycholinguistic_flags=psych_flags,
        sentence_count=len(sentences),
        word_count=word_count,
        lexical_density=lexical_density,
        avg_sentence_length=avg_sentence_length,
        findings=findings,
    )


def format_markdown(report: AuditReport) -> str:
    lines = [
        f"### Clarity Score: {report.clarity_score}/100",
        f"- Sentences: {report.sentence_count} | Words: {report.word_count} | Avg Length: {report.avg_sentence_length:.1f} words",
        f"- Lexical Density: {report.lexical_density:.2f} | Deictic Flags: {report.deictic_flags} | Psycholinguistic Flags: {report.psycholinguistic_flags}",
        "",
    ]
    if not report.findings:
        lines.append("No referential or syntactic clarity issues detected.")
        return "\n".join(lines)

    lines.append("| Sent | Category | Rule | Severity | Span | Fix |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for f in report.findings:
        lines.append(
            f"| {f.sentence_index} | {f.category} | {f.rule} | {f.severity} | `{f.span}` | {f.suggestion} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit text for deictic and psycholinguistic clarity."
    )
    parser.add_argument("--text", type=str, help="Inline text to analyze.")
    parser.add_argument(
        "--file", type=Path, help="Path to a UTF-8 text or Markdown file."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON instead of Markdown.",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=0,
        help="Optional CI gate: exit with code 1 if clarity_score < min-score.",
    )
    args = parser.parse_args(argv)

    if args.text is not None:
        source_text = args.text
    elif args.file is not None:
        source_text = args.file.read_text(encoding="utf-8")
    else:
        source_text = sys.stdin.read()

    report = audit_text(source_text)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(format_markdown(report))

    if report.clarity_score < args.min_score:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
