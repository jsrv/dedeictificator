# Psycholinguistic & Deictic Clarity Rubric

## 1. Research Foundation: arXiv:2610.29162

Clark, Martin, and Mahowald (2026), *"Why is AI-generated language so hard to understand?"* (arXiv:2610.29162), demonstrate that frontier and near-frontier LLMs systematically overuse syntactic constructions linked to human reading difficulty. While human communication balances production ease with comprehension ease under **Uniform Information Density (UID)**, post-training objectives (RLHF and RLVR for math, code, and reasoning) reward high information density per token.

When LLMs compress information into fewer tokens, they shift away from human-aligned syntax toward dense nominalizations, omitted function words, and long-distance dependencies. When users copy or read those outputs without shared context, **deictic expressions** further break referent resolution.

## 2. The 10-Point Diagnostic Rubric

### Layer A: Deictic & Referential Ambiguity

1. **Broad Demonstrative Deixis (`this`, `that`, `these`, `those`)**
   - **Mechanism**: Using a demonstrative pronoun without a following head noun forces the reader to infer the scope of the antecedent (a single noun, a clause, or an entire preceding paragraph).
   - **Bad**: *"This causes timeouts under load."*
   - **Good**: *"This unindexed database lookup causes timeouts under load."*

2. **Unanchored Personal & Object Pronouns (`it`, `its`, `they`, `them`, `their`)**
   - **Mechanism**: When two or more plausible noun phrases appear in the preceding clause, pronouns trigger ambiguity or garden-path reanalysis.
   - **Bad**: *"When the worker sends the payload to the broker, it validates the schema."*
   - **Good**: *"When the worker sends the payload to the broker, the broker validates the schema."*

3. **Spatial & Discourse Deixis (`here`, `there`, `above`, `below`, `the former`, `the latter`)**
   - **Mechanism**: Spatial pointers depend on visual layout or turn order; `the former`/`the latter` require holding two entities in working memory and mentally reversing order.
   - **Bad**: *"See the configuration above and apply the latter to the staging cluster."*
   - **Good**: *"See Section 2 (TLS Configuration) and apply the mutual-TLS profile to the staging cluster."*

4. **Relative Temporal Deixis (`now`, `currently`, `recently`, `today`, `earlier`, `soon`)**
   - **Mechanism**: Time-relative adverbs decay as soon as text is saved to documentation, issues, or commit messages.
   - **Bad**: *"This endpoint is currently deprecated and will be removed soon."*
   - **Good**: *"The `/v1/users` endpoint is deprecated as of v2.4 and will be removed in v3.0."*

### Layer B: Psycholinguistic Difficulty Features (Clark et al., 2026)

5. **Stacked Noun Chains (Compound Noun Piles)**
   - **Mechanism**: Three or more consecutive nouns compress implicit prepositional or verbal relationships, forcing readers to parse structural hierarchy from scratch.
   - **Bad**: *"We installed a horror movie soundtrack generator in the notification pipeline."*
   - **Good**: *"We added a generator that produces horror-movie soundtracks for the notification pipeline."*

6. **Reduced Object Relative Clauses (Omitted `that` / `which`)**
   - **Mechanism**: English object relative clauses place the object before the subject-verb pair. Dropping `that` or `which` removes the syntactic boundary cue and causes temporary misparsing.
   - **Bad**: *"The migration script the engineer ran yesterday failed."*
   - **Good**: *"The migration script that the engineer ran yesterday failed."*

7. **Denominal Verbs**
   - **Mechanism**: Converting nouns into verbs saves one or two tokens but increases lexical surprisal and register friction.
   - **Bad**: *"Let's calendar that review and footnote the edge cases."*
   - **Good**: *"Let's schedule that review and add footnotes for the edge cases."*

8. **Inanimate Subjects with Animate-Requiring Verbs**
   - **Mechanism**: Assigning volitional or biological verbs (`eat`, `want`, `decide`, `refuse`, `struggle`) to abstract or mechanical subjects forces metaphorical coercion.
   - **Bad**: *"The sentence is quietly eating its own reader-patience budget."*
   - **Good**: *"Dense, convoluted sentences quickly exhaust a reader's patience."*

9. **Long-Distance Syntactic Dependencies**
   - **Mechanism**: Human working memory decays rapidly over intervening words between a subject and its main verb or between a verb and its object.
   - **Bad**: *"A service that retries failed upstream requests without exponential backoff under peak traffic crashes."*
   - **Good**: *"A service crashes under peak traffic if it retries failed upstream requests without exponential backoff."*

10. **Low-Frequency N-grams & Function-Word Omission**
    - **Mechanism**: Stripping predictable function words creates sharp surprisal spikes that slow reading speed.
    - **Bad**: *"Every behavioral test was verified red against original source."*
    - **Good**: *"Every behavioral test was verified as failing against the original source."*
