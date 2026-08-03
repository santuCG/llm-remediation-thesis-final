# Prompt Changelog

Versioned record of every change to the LLM prompt used by
`scripts/remediation/llm_reasoner.py`. Each scenario's evidence bundle
records its own `prompt_version` (in `llm-request.json`/`llm-response.json`
and the user-prompt text itself), so any regenerated scenario can be traced
back to the exact prompt that produced it via this file plus `v1.1.md`/`v1.2.md`.

Prior to this changelog, the prompt had never been revised since the
original 18-scenario dataset — v1.1 is the version used for every historical
scenario and every Pipeline v2.0 engineering-verification run performed this
session (Fixes #1–#9, all committed on `pipeline-v2-phase1`).

## v1.1 → v1.2

Preceded by a structured scientific review against 8 criteria (clarity,
completeness, hallucination risk, determinism, scientific neutrality, retry
prompt adequacy, output schema constraint, methodology impact), explicitly
scoped to scientific validity/reproducibility/fairness, not benchmark
performance. Full review findings and classification table are in the
conversation record; only the items classified as safe to change without
altering the experiment's methodology, or with a *confirmed* (not
hypothetical) defect, were acted on. Everything else was deliberately
postponed — see "Deferred" below.

| Change | Why | Expected improvement (to be validated by results) | Classification |
|---|---|---|---|
| Added `enum` constraints to `strategy`, `remediation_type`, and `manifest_patch.operation` in the response schema | These were free-text strings, compliance with the prose description was advisory only. `manifest_editor.py`'s own handling logic already confirms the model has produced at least 5 distinct literal operation strings across historical runs — not hypothetical, an observed vocabulary-drift gap | Every regenerated scenario's `strategy`/`remediation_type`/`manifest_patch.operation` should come from a fixed, closed vocabulary — no new/unexpected literal values should appear in `metrics.json` across the 18 scenarios. If a scenario's evidence shows an operation outside the enum, that would indicate the enum was constructed incorrectly (missing a legitimately-needed value), not a model failure | A — pure engineering constraint, doesn't change what the model is asked to decide |
| Aligned system prompt's strategy list wording with the schema's exact 5 canonical terms (was previously a separately-worded description: "native upgrades, dependency overrides, dependency resolutions, package replacement, or manual intervention") | Two different vocabularies describing the same 5 concepts in two places the model reads | Should have no observable effect under `enum` constraints (the schema will constrain the output regardless of system-prompt wording) — this change is about readability/maintainability for future prompt revisions, not expected to shift results | A |
| Retry context now reads different evidence depending on whether `build_success` or `rescan_success` is what actually failed, instead of always tail-truncating `build.log`'s last 2000 characters | **Confirmed, not hypothetical**: this exact mechanism produced a wrong-signal retry on JS-01, documented in `CHANGELOG_V2.md`'s Phase 2 finding — the model reasoned about an unrelated `ELSPROBLEMS` npm message instead of the real compiler error. Verified during implementation that build.log's tail *currently* happens to contain the relevant error (post Fixes #1/#1a/#6), but the mechanism was still blind/fragile — and, more importantly, confirmed that when the retry trigger is "the CVE is still present after rescan" (the dominant retry trigger observed for JS-01 across every verification run this session), `build.log` contains **no information about that at all** — the model was retrying blind on the single most common failure mode | Retries triggered by a persisting CVE should now show the model *why* — which package, which version, which scanner-known fix versions — rather than unrelated compile-time noise or nothing. Hypothesis: retry reasoning should more consistently reference the actual rescan finding (visible by reading `reasoning` in `llm-response.json` for any scenario with `retry_count: 1`), and retries should have a better chance of landing on a genuinely different, more targeted strategy when the first attempt's approach didn't clear the scanner — though whether recommendations actually diversify is an open question this data will help answer, not something engineered to happen | B — changes what information reaches the model, therefore a minor methodology change |
| Bumped `prompt_version` from `v1.1` to `v1.2` (both in the user-prompt text and `llm-request.json`'s evidence metadata) | Every future scenario's evidence must be traceable to the exact prompt version that produced it | N/A — pure provenance bookkeeping | A |

## Deferred (from the structured review — not acted on this pass)

Recorded here so they aren't lost, and so any future prompt revision starts
from a known, deliberate baseline rather than rediscovering the same review:

- Retry prompt doesn't explicitly instruct the model to consider a
  materially different strategy category if the same one just failed
  (structural reconvergence under strict determinism was separately
  confirmed: JS-01's attempt 1 and retry independently produced the same
  `add_override, vm2, 3.9.18` via different reasoning paths).
- `context` given to the model for transitive-dependency candidates doesn't
  include the broader dependency subgraph, only the target package's own
  `npm_ls`/`npm_explain` output — narrower than what the system prompt's
  "critically evaluate the topological subgraph" language implies.
- "Do not hallucinate package versions" is a negative instruction with no
  programmatic downstream check; could be reframed as a positive constraint
  ("choose only from `Fixed Versions` unless none resolves the CVE").
- "Recommend the **safest** strategy" — undefined rubric; could implicitly
  bias toward low-disruption fixes over more correct-but-disruptive ones.
- System prompt's opening framing ("Your objective is to **eradicate**...")
  could subtly prime the model away from honestly recommending
  `manual_review` when that's the correct answer.
- No structured field captures whether a retry deliberately changed strategy
  vs. repeated it (would require adding a new schema field — a methodology
  change, Classification C, not something to fold into an engineering pass).

None of these were acted on because none had a *confirmed* defect behind
them (unlike the retry-context fix above) — each is a real, wording-level
scientific-neutrality or completeness question that deserves its own
deliberate review, not a change made under regeneration-day time pressure.
