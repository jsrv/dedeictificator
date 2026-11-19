---
name: dedeictificator
description: Audit, score, and rewrite text to eliminate ambiguous deictic expressions (unanchored pronouns, spatial/temporal/discourse deixis) and high-processing-cost AI syntax (stacked nouns, reduced object relative clauses, denominal verbs, inanimate agency, and long dependency chains) based on Clark et al. (arXiv:2610.29162). Use whenever the user asks to dedeictify, clarify, de-jargon, humanize, audit readability, resolve ambiguous pronouns or references, or improve LLM-generated prose, documentation, prompts, or technical writing.
---

# Dedeictificator

Eliminate referential ambiguity and post-trained LLM compression artifacts so every sentence is self-contained, unambiguous, and effortless for humans to process.

Grounded in psycholinguistic findings from Clark, Martin, and Mahowald (arXiv:2610.29162), modern LLMs optimized for math, code, and reasoning tend to maximize information density at the expense of human working memory. When dense syntax combines with unanchored deictic words ("this", "it", "here", "above", "recently"), readers must backtrack and guess referents. This skill diagnoses both failure modes and rewrites text toward Uniform Information Density (UID).

## When to Use

- The user asks to "dedeictify", "clarify", "disambiguate", or "make self-contained" a passage, prompt, ticket, or document.
- AI-generated output feels dense, robotic, jargon-heavy, or hard to parse on a first read.
- Text will be moved out of its original context (e.g., chat snippets moved into docs, PR descriptions, RAG chunks, or standup notes) where spatial, temporal, or conversational pointers break.
- The user wants a quantitative readability and referential-clarity audit before publishing technical writing.

## Diagnostic Taxonomy

Evaluate text across two layers (see `references/psycholinguistic_rubric.md` for full rules):

| Layer | Feature | Failure Pattern | Repair Strategy |
| --- | --- | --- | --- |
| Deixis | Broad Demonstratives | Standalone "this", "that", "these", "those" referring to a whole prior idea | Add a specific head noun ("This latency spike..." instead of "This...") |
| Deixis | Unanchored Pronouns | "It", "they", "them", "its" with multiple competing antecedents | Name the concrete entity; use pronouns only for the single salient subject |
| Deixis | Spatial & Discourse Pointers | "Here", "there", "above", "below", "the former", "the latter" | Replace with explicit section names, file paths, or entity labels |
| Deixis | Relative Time Pointers | "Now", "currently", "recently", "today", "soon" | Anchor to explicit dates, versions, or system states |
| Syntax (2610.29162) | Stacked Noun Chains | 3+ consecutive nouns compressing complex relations ("reader-patience budget") | Unpack with prepositions or finite clauses ("the reader's patience") |
| Syntax (2610.29162) | Reduced Object Relatives | Missing "that" or "which" in object relative clauses | Insert overt relativizers ("the name that he heard") to prevent garden paths |
| Syntax (2610.29162) | Denominal Verbs | Nouns compressed into verbs ("calendar it", "footnote it", "sunset this") | Restore standard verbs ("schedule it", "add a footnote", "deprecate this service") |
| Syntax (2610.29162) | Inanimate Agency | Non-human subjects paired with volitional verbs ("the pipeline wants") | Attribute agency to people or describe the concrete mechanism |
| Syntax (2610.29162) | Long Dependencies | Subject and main verb separated by heavy intervening clauses | Move subordinate clauses after the main verb or split the sentence |
| Syntax (2610.29162) | High Surprisal / Compression | Omitted function words and rare bigram jumps | Smooth information density with explicit connective words |

## Workflow

1. **Preserve Protected Spans**: Identify code blocks, inline code identifiers, direct quotations, and proper titles. Do not alter syntax inside protected spans.
2. **Run Deterministic Audit**: Execute `scripts/audit_clarity.py` on the input text (via `--text` or `--file`) to obtain baseline clarity scores, sentence-level flags, and psycholinguistic density metrics.
3. **Resolve Deictic Anchors**: For every flagged deictic token, trace backward to find its true referent. If the referent is ambiguous or missing from the passage, either disambiguate using context or mark it with `[CLARIFY: <missing referent>]` rather than hallucinating facts.
4. **Decompress Difficult Syntax**: Rewrite flagged sentences to eliminate stacked nouns, restore omitted relativizers ("that"/"which"), replace denominal verbs, fix inanimate agency, and shorten subject-verb dependency distances.
5. **Verify Improvement**: Re-run `scripts/audit_clarity.py` on the rewritten text to confirm that the clarity score improved and zero high-severity ambiguities remain.
6. **Present Structured Output**: Return the Clarity Scorecard, a concise table of key fixes, and the final self-contained text.

## Output Format

Structure responses using these three sections:

1. **Clarity Scorecard**: Show `Before -> After` composite score (0-100), deictic flag count, and psycholinguistic complexity flag count.
2. **Key Transformations**: List the highest-impact edits in a 3-column table (`Original Span`, `Issue Type`, `Rewritten Span`).
3. **Dedeictified Text**: Provide the clean, drop-in replacement text ready for immediate use.

## Gotchas

- **Do not create robotic repetition**: Replacing every pronoun with a full 5-word noun phrase makes prose clunky. Use the full noun phrase on first mention in a paragraph, a short canonical noun on second mention, and a pronoun only when no competing noun intervenes.
- **Keep legitimate dummy subjects**: Constructions like "It is raining" or "There are three edge cases" are expletive/existential constructions, not referential deixis. Do not rewrite them unless they hide missing agency.
- **Never invent missing facts**: If a user writes "Fix that before Friday" with no context for "that", flag `[CLARIFY: target bug or task]` instead of guessing.
- **Respect domain terminology**: Established multi-word technical terms (e.g., "continuous integration pipeline", "abstract syntax tree") are lexicalized concepts, not ad-hoc LLM noun stacks. Leave established domain terms intact.
