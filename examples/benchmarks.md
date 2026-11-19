# Dedeictificator Calibration Benchmarks

## Benchmark 1: Incident Postmortem Snippet

### Before (Clarity Score: 41/100)
> It started failing earlier after they deployed the retry queue buffer manager update above. This caused the ingestion worker to eat its memory budget, and the latter refused to drain it. We need to calendar a follow-up and sunset that soon.

### Flagged Issues
- `It` (initial_unanchored_pronoun) -> unclear which service failed
- `earlier` (temporal_deixis) -> relative timestamp
- `they` (unanchored_pronoun) -> unspecified team or automation
- `retry queue buffer manager update` (stacked_noun_chain) -> 5-noun compound stack
- `above` (spatial_discourse_deixis) -> broken layout pointer
- `This` (broad_demonstrative) -> unanchored reference to entire prior event
- `worker ... eat` / `latter refused` (inanimate_agency + discourse_deixis) -> animate verbs on software components + `the latter`
- `calendar` / `sunset` (denominal_verb) -> compressed noun-verbs
- `that` / `soon` (broad_demonstrative + temporal_deixis) -> vague target and deadline

### After (Clarity Score: 96/100)
> The `payments-api` service began returning HTTP 503 errors at 14:20 UTC on November 12, 2026, immediately after the platform team deployed v2.8 of the manager that buffers the retry queue. That deployment caused the ingestion worker to exceed its 4 GB memory limit, which prevented the worker from draining pending events. The on-call team will schedule a postmortem review by November 20, 2026, and deprecate the legacy buffer manager in release v2.9.

---

## Benchmark 2: LLM-Generated Code Review Summary

### Before (Clarity Score: 54/100)
> The parser the author wrote handles edge cases well, though this impacts throughput here. Every validation check was verified green against fixtures, so actioning the remaining items below should unblock it.

### Flagged Issues
- `The parser the author wrote` (reduced_object_relative) -> missing overt relativizer `that`
- `this impacts` (broad_demonstrative + denominal_verb) -> vague referent + noun-verb
- `here` (spatial_discourse_deixis) -> unanchored location
- `verified green against fixtures` (high_surprisal_compression) -> telegraphic phrasing
- `actioning` (denominal_verb) -> corporate noun-verb
- `below` / `it` (spatial_discourse_deixis + unanchored_pronoun) -> unanchored pointers

### After (Clarity Score: 95/100)
> The parser that the author wrote handles malformed UTF-8 edge cases reliably, although the extra validation pass reduces throughput by 12% in the batch ingestion path. Every validation check passed against the test fixtures, so completing the three remaining tasks in Section 4 will unblock the pull request.
