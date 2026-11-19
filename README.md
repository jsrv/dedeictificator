# Dedeictificator

[![CI](https://github.com/jsrv/dedeictificator/actions/workflows/ci.yml/badge.svg)](https://github.com/jsrv/dedeictificator/actions/workflows/ci.yml)

An agent skill and zero-dependency psycholinguistic linter that eliminates **deictic ambiguity** and **high-processing-cost LLM syntax**, grounded in Clark, Martin, and Mahowald (2026), *"Why is AI-generated language so hard to understand?"* ([arXiv:2610.29162](https://arxiv.org/abs/2610.29162)).

## Why This Exists

Modern frontier LLMs post-trained for math, code, and reasoning optimize for **maximum information density per token** rather than human **Uniform Information Density (UID)**. When compressed AI prose is pasted into documentation, tickets, or RAG chunks, unanchored deictic pointers (`this`, `it`, `here`, `above`, `recently`) sever referential links and force readers to backtrack.

Dedeictificator pairs a deterministic Python AST/token scanner (`scripts/audit_clarity.py`) with a structured agent workflow (`SKILL.md`) to measure clarity (0–100), flag exact failure spans, and rewrite text into self-contained prose.

## Repository Structure

```text
dedeictificator/
├── SKILL.md                              # Agent entrypoint (frontmatter + workflow + guardrails)
├── scripts/
│   └── audit_clarity.py                   # Zero-dependency CLI & JSON clarity linter
├── references/
│   └── psycholinguistic_rubric.md         # 10-point diagnostic rubric (Deixis + arXiv:2610.29162)
├── examples/
│   └── benchmarks.md                      # Before/after calibration fixtures
├── tests/
│   └── test_audit_clarity.py              # Unit tests for all detectors and CI gates
└── README.md
```

## Quick Start

Run the deterministic clarity auditor directly from the command line (Python 3.9+, no third-party dependencies):

```bash
python3 scripts/audit_clarity.py --text "It started failing earlier after they deployed the retry queue buffer manager update above."
```

Output structured JSON or enforce a minimum clarity score in CI:

```bash
python3 scripts/audit_clarity.py --file docs/architecture.md --json
python3 scripts/audit_clarity.py --file docs/architecture.md --min-score 85
```

## Running Tests

```bash
python3 -m unittest discover -s tests
```
