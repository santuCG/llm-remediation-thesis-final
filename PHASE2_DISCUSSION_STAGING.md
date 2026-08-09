# Phase 2 — Discussion Staging

Working document only. Not thesis content. Tracks interpretive material removed from
Chapter 4 during the incremental Findings/Discussion restructuring, pending assembly
into a coherent Chapter 5 narrative once enough units have been processed (especially
§4.7 Research Question Analysis and §4.8 Discussion, which most of this will merge into).

Format per entry: source unit, original location, the relocated sentence(s) verbatim,
and a placement note.

---

## Unit 1 — §4.1–§4.2

**Source:** §4.2 Deterministic Baseline Outcomes, closing sentence (removed from Chapter 4 on this pass).

**Relocated text (verbatim):**
> Within the evaluated workflows, the deterministic baseline's recorded outcome differs by ecosystem: it reaches a validated result for the pip scenarios and does not reach one for the npm scenarios, for the reasons given in §3.8.

**Placement note:** Natural opening for a future Chapter 5 subsection on baseline comparison
(likely "Comparison with the deterministic baseline" or similar, final heading TBD). Expected
to merge with related interpretive content still pending from §4.7's Comparison paragraph and
§4.8's Discussion section (both later units in this same restructuring pass). Not written into
the thesis yet — deliberately not padded into a standalone stub per the user's Phase 2 instruction.

---

## Unit 2 — §4.3 (AF-01) and §4.4 (JS-01)

### AF-01

**Source:** §4.3 Case Study — AF-01, closing INTERPRETATION sentences (removed from Chapter 4 on this pass).

**Relocated text (verbatim):**
> AF-01 shows the pipeline working end to end but does not show an LLM advantage, because the deterministic baseline also succeeded (Table 5). For a direct pip dependency the LLM reaches the same answer a rule-based bump would, consistent with the strength of Dependabot/Renovate on the direct-upgrade case [9], [10].

**Placement note:** Coherent and substantial as-is — not thin, not padded. Ready to become a real
Chapter 5 paragraph (AF-01's interpretation section) once Chapter 5 is assembled. Citations [9],[10]
preserved. Table 5 cross-reference stays valid (Table 5 remains in Chapter 4).

### JS-01

**Source:** §4.4 Case Study — JS-01, closing INTERPRETATION sentence, plus the entire standalone
"sensitivity of strategy selection to prompt formulation" LIMITATION paragraph (removed from
Chapter 4 on this pass — judgment call: labeled LIMITATION but functionally interpretive/methodological,
approved by user for relocation to Discussion).

**Relocated text (verbatim):**
> JS-01 demonstrates correct graph reasoning: the model located the transitive path and selected an appropriate remediation strategy, a transitive override, because `vm2` was not a direct dependency, reaching a validated vulnerability-removed state.
>
> **LIMITATION — sensitivity of strategy selection to prompt formulation.** Under an earlier prompt formulation, the same model on this same scenario recommended `manual_review` on its retry, reasoning that the override would "trigger transitive updates to `@types` packages… unsupported by the project's legacy TypeScript compiler… automated remediation is unsafe." That hedged reasoning does not appear in either attempt reported above; both attempts selected `transitive_override` with no mention of `@types` conflicts. The formulation used in the evaluation reported in this thesis constrains `strategy` and `remediation_type` through schema `enum` values and uses aligned system-prompt wording, which differs from the earlier formulation. This difference in prompt formulation is the most likely explanation for the divergence, though it was not isolated as a controlled ablation and is not claimed as proven. The observation bears on the reliability of single-configuration evaluations rather than on remediation capability. Within this study, strategy selection — not merely explanatory wording — changed between prompt formulations.

**Placement note:** First paragraph merges naturally with AF-01's interpretation (both are
"what does correct/incorrect graph reasoning demonstrate" content). Second paragraph
(prompt-formulation sensitivity) is a distinct methodological-limitations point for Chapter 5,
per the template's explicit inclusion of "methodological limitations of your research" in
Discussion. Not merged with other units' content yet — flagged as its own coherent block.

**Explicitly not relocated in this unit (per user instruction, point 7):** the lockfile/stale-resolution
pipeline explanation for why JS-01's retry was needed despite an unchanged recommendation. That
explanation belongs to §4.10.5 (a later, not-yet-processed unit) and was deliberately not pulled
forward into this case study to avoid introducing content ahead of its proper unit.

---

## Unit 3 — §4.3a (AF-06)

**Source:** §4.3a Case Study — AF-06, INTERPRETATION content (removed from Chapter 4 on this pass).

**Relocated text — REVISED, not the original wording.** The original thesis text made an
unsupported generalization ("This is a real, general phenomenon... NVD and GHSA increasingly
publish both v3.1 and v4.0 scores for the same CVE") with no citation anywhere in the thesis
backing that trend claim; traced to its source, that sentence was itself an unsourced assertion
in `docs/FINDING_CVE_DETECTION_GAPS.md`, not an independently evidenced finding. User-directed
revision scopes the claim strictly to what AF-06 itself demonstrates:

> **INTERPRETATION.** AF-06 illustrates a methodological risk when severity-gated discovery depends on a scanner-reported severity label while vulnerability selection is based on a different scoring standard. For this advisory, the same vulnerability carried a CVSS v3.1 score of 7.8 ("High") and a CVSS v4.0 score of 5.4 ("Medium"). Because the discovery filter in `prioritize.py` requires `severity in ["high","critical"]`, the scanner's v4.0-derived "Medium" label placed the advisory below the automatic-discovery threshold. Thus, the scenario demonstrates that the scoring standard represented in upstream vulnerability metadata can affect whether a vulnerability passes a severity-gated discovery rule, even when the researcher has deliberately selected that vulnerability for evaluation.

**Provenance verified before relocation:** GitHub's severity-field v4.0 derivation and Grype's
"Medium" label reaching `prioritize.py`'s filter are both confirmed by primary evidence quoted in
`docs/FINDING_CVE_DETECTION_GAPS.md` (actual `gh api advisories/GHSA-q2x7-8rv6-6q7h` output and
actual Grype JSON output) — kept as FACT in Chapter 4. The broader "increasingly publish both"
trend claim is dropped entirely, not merely softened, since no source in the thesis substantiates it.

**Placement note:** Coherent, self-contained, appropriately scoped. Ready for Chapter 5 as-is.

---

## Unit 4 — §4.3b (JS-06)

**Source:** §4.3b Case Study — JS-06, INTERPRETATION paragraph (removed from Chapter 4 on this pass).
Both LIMITATION paragraphs stay in Chapter 4 verbatim, per the established precedent that
evidence-based diagnostic/root-cause content belongs in Findings, not Discussion.

**Relocated text (verbatim):**
> Unlike AF-06, this has nothing to do with severity thresholds, CVSS versions, or Grype's matching. This scenario illustrates the target-selection policy described in §3.7 in practice: the run produces no evidence and a logged failure rather than substituting a different vulnerability for the preregistered target that cannot be found. JS-06 is reported as a confirmed, investigated detection gap, not as a failed or successful remediation, because no remediation attempt was possible.

**Preserved claim-level distinction (per user instruction, not to be weakened):** Chapter 4 keeps
"This isolates the fault to Syft's package-cataloging stage" at full strength — this is the
*established* claim (package absent from SBOM → Grype cannot match it → detection gap occurs at
cataloguing). The second LIMITATION paragraph's "precise mechanism is not fully characterized"
is a separate, *not-established* claim (exactly why Syft v1.44.0 excludes this particular
dev-only package). These are two different levels of claim and neither should be used to soften
the other.

**Placement note:** Coherent, self-contained. Natural companion to AF-06's interpretation once
Chapter 5 is assembled — the two are explicitly contrasted ("Unlike AF-06...") and read well
placed near each other.

---

## Unit 5 — §4.3c (JS-07)

**Source:** §4.3c Case Study — JS-07, INTERPRETATION paragraph (removed from Chapter 4 on this pass).
FACT and root-caused LIMITATION paragraphs stay in Chapter 4 verbatim, same precedent as JS-06:
evidence-based root-cause diagnosis belongs in Findings, not Discussion.

**Relocated text (verbatim):**
> This is a genuine limitation of the pipeline's current manifest-editing scope, not of the LLM's reasoning — the LLM correctly diagnosed the transitive path and chose the applicable strategy on both attempts; the strategy simply could not reach every copy of the vulnerable package in this application's particular build layout. Retrying further would not have helped, since the failure is deterministic given the current manifest editor, not transient — no further attempts were made.

**Preserved claim-level distinction:** the pipeline-applicability-limitation vs. LLM-remediation-failure
distinction is the core content of this relocated paragraph — attribution stays exactly as written
("not of the LLM's reasoning"), not softened or strengthened in relocation.

**Placement note:** Coherent, self-contained. Natural companion to JS-06's interpretation — both are
Failure Category case studies (A and B respectively) whose Discussion content will likely sit near
each other once Chapter 5 is assembled.

---

## Unit 6 — §4.5 (JS-09)

**Source:** §4.5 Case Study — JS-09, INTERPRETATION sentence (removed from Chapter 4 on this pass).
Scenario context, FACT, and OBSERVATION content (including the finding that the retry re-confirmed
the identical LLM recommendation after pipeline lockfile regeneration, not a changed answer) stays
in Chapter 4 verbatim.

**Relocated text (verbatim):**
> JS-09 is the direct-dependency counterpart to AF-01: for a package the manifest already names directly, the LLM's value is confirming and re-applying the correct version once the package manager's own installation state is fixed, not graph reasoning — the graph-reasoning cases in this dataset are the transitive ones (JS-01).

**Checked and confirmed absent:** no training-data or knowledge-cutoff claim appears in this
relocated text or was introduced during relocation. The claim is about reasoning *type*
(confirm-and-reapply vs. graph reasoning), not about what the model knew or when.

**Scoping instruction for final Chapter 5 assembly (per user, apply when this is merged into real
Discussion prose):** keep this interpretation explicitly scoped to the observed direct-dependency
case — do not generalize it into a broader claim about direct-dependency scenarios as a class
without additional support.

**Placement note:** Natural companion to AF-01's interpretation (explicitly cross-referenced,
"the direct-dependency counterpart to AF-01") and to JS-01's interpretation (named as the
contrasting graph-reasoning case) — these three will likely need to be assembled together or in
sequence in Chapter 5.

---

## Unit 7 — §4.6 (JS-05)

**Source:** §4.6 Case Study — JS-05, INTERPRETATION sentence (removed from Chapter 4 on this pass).
Scenario context, both FACT paragraphs, OBSERVATION, and the LIMITATION paragraph (including its
scope-caveat about the deterministic baseline comparison) all stay in Chapter 4 verbatim.

**Relocated text — REVISED per user correction, not the original wording.** The original thesis
text used causal framing ("context-in-prompt retry changing the recommended strategy," "supplied
with that build-error context — recommended a direct upgrade instead") that implied the build-error
context caused the strategy change. Revised to describe the observed sequence as an association,
with an explicit single-case caveat:

> **INTERPRETATION.** Within the LLM pipeline's own two attempts, JS-05 shows an observed sequence: the first attempt's `overrides` entry produced the `EOVERRIDE` conflict, and the retry — supplied with that build-error context — was associated with a different recommended strategy, a direct upgrade rather than an override. This sequence is consistent with the LLM breaking-update literature's finding that build-error context in the prompt is associated with higher remediation success [31], but the single JS-05 case does not establish that the supplied context alone caused the strategy change.

**Flagged, not resolved now:** citation `[31]` (Byam / LLM breaking-update literature) is carried
over unchanged in this revision. Per user instruction, flagging it for the final citation-scope
audit (Phase 3 / later citation pass) rather than independently re-evaluating its fit here.

**Placement note:** Coherent, self-contained, appropriately scoped (no unsupported causal claim
from a single case).

---

## Unit 8 — §4.7 Research Question Analysis (highest-stakes unit)

**Source:** §4.7, two blocks removed from Chapter 4 on this pass: the Comparison INTERPRETATION
paragraph (RQ answer) and the complete Build Stability (SQ3, H₀) paragraph, moved as one
undivided unit per explicit user instruction — the H₀ verdict must never be textually separated
from its §3.8 workflow-stopping-point qualification. Generation/Validation/Comparison OBSERVATION
material, the npm validation LIMITATION, the Failure Category A/B attribution, and the SQ1/SQ2/SQ4
pointer paragraph all stay in Chapter 4, unchanged.

**Relocated text (verbatim, both blocks, unmodified from the original file):**

> **INTERPRETATION (answer to the RQ, within the scope stated in §1.3 and §3.8).** For the flat pip class the deterministic baseline reached a validated result, so no comparative advantage is claimed for the LLM pipeline there. For the transitive npm class, within the evaluated workflows, the LLM pipeline reached a validated dependency-level remediation on seven of nine scenarios; the deterministic baseline's workflow did not reach a rescan-based result on any npm scenario, for the reason given in §3.8; a direct end-to-end comparison is not possible because the workflows terminate at different evaluation points. The two npm scenarios that did not reach a validated result are bounded by two disclosed, independently-diagnosed limits of the LLM pipeline's own reach rather than of the model's reasoning: SBOM cataloging coverage (JS-06) and manifest-editing scope in multi-manifest applications (JS-07).
>
> **Build stability (SQ3, H₀).** **OBSERVATION.** Table 4 (§4.1) and Table 5 (§4.2) report `build_success` as identical between the two arms within each ecosystem: `false` for both the deterministic baseline and the LLM pipeline across all nine npm scenarios, and `true` for both across all nine pip scenarios. No scenario in either ecosystem shows a different `build_success` value between the two arms. This is the evidence against which H₀'s build-success-rate outcome (§1.4) is evaluated; the remediation-success-rate outcome is addressed separately above, subject to the scope stated in §3.8. **On this basis, H₀ is not rejected for build success rate** (no scenario differs between arms) **and is rejected for remediation success rate on the npm scenarios** (seven of nine reach a validated state under the LLM pipeline against zero under the baseline), a difference this thesis attributes, per §3.8, to the two workflows' differing stopping points rather than to remediation capability considered in isolation.

**Verified against §1.3/§1.4 before relocation:** the H₀ wording, the per-outcome verdict split, and
the §3.8 attribution clause are all verbatim carry-overs from the existing file, cross-checked
word-for-word against §1.4's own framing ("attributable, per §3.8, to the two workflows' differing
stopping points rather than to remediation capability in isolation") — not a new or strengthened
claim. Both blocks preserved as one undivided unit; the verdict is never separated from its
qualification anywhere in this document.

**Placement note:** These two blocks are the core of Chapter 5's RQ/H₀ answer — likely the most
central paragraphs in the whole Discussion chapter once assembled. Should probably sit early in
Chapter 5, directly following the "short summary of findings" opening (per the template's own
guidance and the material already staged from §4.11's Chapter Summary, not yet processed).

---

## Unit 9 — §4.8 Discussion (moved in full, no Chapter 4 remainder)

**Source:** §4.8, entire section. Unlike every case-study unit, §4.8 contained zero FACT/OBSERVATION
content — all five argument blocks were already INTERPRETATION- or LIMITATION-labeled. Inventoried
against §4.7's now-relocated content (Unit 8) before moving: no verbatim or near-verbatim overlap
found with the RQ-answer or H₀-verdict blocks; all five arguments are analytically distinct
(construct-validity discipline; where generation added observable value; tool-by-tool literature
comparison; APR-literature comparison; reproducibility limitation). Confirmed genuinely new content,
not redundant after the split.

**Relocated text (verbatim, five argument blocks, unmodified from the original file):**

> **Installation, remediation, and compilation are three different properties.** **INTERPRETATION.** The npm scenarios make this concrete: a package installed, the target vulnerability was removed from the scan, and the application still did not compile for a reason unrelated to the fix. Collapsing these into one flag would misrepresent the result; the pipeline records them separately and the analysis reads them together. This discipline is what keeps the study honest, and it answers the construct-validity threat directly.
>
> **Within the evaluated pipeline, generation added observable value in constraint-handling scenarios more than in direct-version-lookup ones.** **INTERPRETATION.** For a direct dependency a scanner already recommends the fixed version, so the LLM's recommendation matches it without additional graph reasoning being observable in the record (AF-01). The scenarios where the LLM's reasoning trace shows it identifying a graph constraint — a shadowed transitive package (JS-01) or a version/constraint reconciliation after a failed attempt (JS-09, JS-05) — are the ones where its output differs from what a direct version lookup alone would produce. This is consistent with, though not proof of, the literature's picture of LLMs as most useful for judgement under context and least useful where a deterministic rule suffices [5], [9]; §3.8 states what this comparison does not establish about the deterministic baseline specifically.
>
> **Comparison with existing tools, in detail.** **INTERPRETATION.** Dependabot and Renovate are strong on the direct-upgrade case the pip scenarios represent [9], [10]; the study's pip results show no LLM advantage there, which is the honest and expected outcome. Commercial SCA adds reachability and larger databases but still recommends versions rather than reasoning about graph constraints [30]. Recent LLM systems such as Byam repair *client code* broken by an update using build context [31], [32]; the present study is adjacent but distinct, targeting the *manifest* strategy for a transitive vulnerability rather than client-code repair. Against this landscape, the study's contribution is a precise one: within the scope stated in §3.8, it identifies, with evidence archived per scenario, the specific cases in this dataset where a manifest-level LLM strategy differs observably from a direct version lookup.
>
> **Comparison with the LLM-repair literature.** **INTERPRETATION.** Code-level APR generates a fix and validates with tests [7], [28]; this study generates a manifest fix and validates with supply-chain checks. The npm compilation failures echo a caution common in that literature — an LLM change can pass one check (vulnerability removal) while another property (compilation) stays broken — and the correct response, followed here, is to report both.
>
> **Reproducibility of the evidence.** **LIMITATION.** Exact scanner match counts are not expected to reproduce bit-for-bit because vulnerability matching depends on a live advisory database whose contents evolve over time. In contrast, the field-level experimental outcomes reported in Table 4 reproduced consistently across repeated independent executions of the LLM-assisted workflow [33]. These two forms of reproducibility should therefore be interpreted separately; the deterministic baseline arm was executed once per scenario and its field-level outcomes were not subjected to repeated execution.

**Placement note:** Follows the Unit 8 RQ-answer/H₀-verdict blocks in Chapter 5's assembly order —
these five arguments elaborate on and contextualize that answer (construct validity, where value
was observed, literature positioning, reproducibility) rather than restating it.

---

## Unit 10 — §4.9 Comparison Summary (NO CONTENT RELOCATED — stays entirely in Chapter 4)

**Decision, not an oversight:** §4.9 is Table 6 plus one footnote — a factual comparison table with
no separable INTERPRETATION-labeled paragraph anywhere in the section (unlike every other unit
processed so far). The footnote — *"The two workflows record their npm outcome at different points
in the remediation sequence (§3.8); this row does not represent a matched comparison of remediation
capability"* — is itself the exact §3.8 safeguard against a "clean end-to-end comparison" misreading
that this unit's instructions asked to verify. It must stay physically attached to the table it
qualifies, in Chapter 4, or a reader encountering the table alone would risk exactly that
misreading. Verified: the pip row's "no comparative advantage claimed" and the npm-row asterisk
pointing to the footnote are both scope-limiting captions on the data itself, not RQ-level
interpretation — consistent with how Table 4/Table 5 and their footnotes were treated in Unit 1.

**Verification performed:** table values (9/9 pip both columns, 7/9 npm LLM / 9/9 npm baseline,
1/9 JS-06, 1/9 JS-07, 6/9 `override_added`, 3 `direct_replacement`) all confirmed unchanged in
Chapter 4 — no edit was made, so there is nothing to diff. No content added to this staging file
for Unit 10.

---

## Unit 11 — §4.10 Explanatory Ablation Study (3-way split: Ch3/Ch4/Ch5)

**Finding, documented before editing:** §4.10.1 (Motivation) and §4.10.2 (Method) were found to be
near-total duplicates of content already present in §3.9 "Explanatory Ablation Study — Methodology"
— same facts, in places near-identical wording (e.g. both state outcomes are reported "at the first
attempt and, where a retry occurred, at the final attempt"). This is pre-existing redundancy
(§3.9 and §4.10 were written in different chapters, so it read fine before restructuring), not
something introduced by this restructuring. Per "preserve meaning, avoid duplication," §3.9 was
**not** modified — it already contains everything §4.10.1/§4.10.2 said, usually in more detail.
Chapter 4 now opens this section with two newly-written orienting sentences (pure navigation,
no new claims, no facts not already stated in §3.9) pointing to §3.9 for methodology, replacing the
literal duplicate text. No fact from §4.10.1/§4.10.2 is lost — every claim in them already exists,
verified word-by-word against §3.9's Motivation, Experimental design, Scenario selection, and
Evaluation protocol paragraphs.

**Chapter 4 retains (unchanged from original):** Table 7, and the Results OBSERVATION paragraph
("Strategy selection... matched the hinted baseline in all four scenarios...").

**Chapter 5 receives (relocated verbatim, §4.10.4 Discussion + §4.10.5 Pipeline Observation, both
in full):**

> **JS-05.** The unhinted first attempt misdiagnosed `jsonwebtoken` as a transitive dependency of `express-jwt`, when it is in fact direct — the identical misdiagnosis the hinted run's own first attempt made. **INTERPRETATION.** Because the same error appears with and without the hint, it reflects a pre-existing tendency in how this specific dependency structure is read, not something the hint removal introduced or masked.
>
> **JS-01.** The unhinted first attempt correctly identified `vm2` as transitive via `juicy-chat-bot` and correctly chose a transitive override — a diagnosis requiring no information the hint would have supplied. Its failure to validate on the first attempt is addressed separately below, since it is a pipeline mechanism, not a reasoning outcome. **INTERPRETATION.** This is the cleanest evidence in the set that hint removal does not, by itself, degrade dependency-graph reasoning: the correct diagnosis was reached without being told the fix version.
>
> **JS-09.** The unhinted first attempt identified `2.0.0-rc.1` as the version at which a fix becomes available, and explicitly recommended manual review rather than an automated bump, citing the risk of breaking changes in a major pre-release. **INTERPRETATION.** This is a version-boundary identification paired with an appropriately cautious strategy choice, not a failure to reason about the fix. The subsequent broken dependency state (see below) followed from applying that recommendation, not from the recommendation's content. The retry's reasoning referenced the resulting broken package state directly, despite the retry prompt never being told what the first attempt recommended — indicating the model can recover diagnostic context from the live dependency state it is shown, not only from an explicit restatement of its own prior output.
>
> **AF-01.** The unhinted attempt succeeded on the first try, recommending a smaller version increment (2.1.2, the release immediately above the vulnerable version) than the hinted run's 2.1.14. **INTERPRETATION.** Both are independently verified as valid fixes; the difference illustrates that "correct" does not mean "identical to the scanner's recorded value," and that the model's own selection, when confident, need not converge on the same specific release the scanner's advisory data names.
>
> **Across all four scenarios**, the pattern is consistent: hint removal changed *which* version was recommended in every case without changing *which strategy* was selected in any case, and every unhinted recommendation independently validated. Three of the four scenarios needed a retry, the same three that needed one in the hinted baseline; only AF-01 succeeded on the first attempt in both conditions. Within those three, the retry requirement is not uniformly attributable to hint removal: JS-05 and JS-01 fail via the identical mechanism in both conditions (a wrong dependency-type diagnosis for JS-05; a pipeline-level lockfile issue for JS-01, see below), but JS-09 fails differently in each — the hinted first attempt fails at the same generic build stage common to most npm scenarios in the primary evaluation (§4.1), while the unhinted first attempt fails specifically because the pre-release version it identified (`2.0.0-rc.1`, absent the hint) resolves to a different, broken installed version. JS-09 is therefore the one scenario in this set where the retry requirement itself, not just the recommended version, plausibly differs because of hint removal.
>
> **Pipeline Observation.** **OBSERVATION.** In JS-01, both the hinted and unhinted first attempts recommended `vm2@3.9.18`, installed it without error, and were still reported vulnerable by the deterministic rescan; both retries recommended the identical version, with no change to the recommendation, and passed. **INTERPRETATION.** Since the identical version fails then succeeds with no change to what was recommended, the cause is not attributable to the version choice. Investigation traced it to the pipeline's lockfile handling: only the retry path performs a full dependency re-resolution, and a prior lockfile can retain a stale resolution despite a syntactically correct manifest change on the first attempt. **LIMITATION.** This is a property of the evaluation pipeline's retry mechanics, observed identically in both the hinted and unhinted conditions, and is outside the scope of the primary research question. It suggests that a clean dependency re-resolution after applying an override, performed before rescan rather than only after a full retry cycle, is worth investigating as a pipeline improvement; this is not evaluated further here (`KNOWN_PIPELINE_LIMITATIONS.md`).

**Note on internal cross-references:** two "§4.10.5" references inside the JS-01/JS-09/"Across all
four scenarios" paragraphs were changed to "below"/"see below" since the Pipeline Observation
content is now part of the same continuous Discussion passage rather than a separately numbered
subsection — this is a navigation update, not a content change, and will be revisited during final
Chapter 5 heading assembly.

**Primary-vs-ablation distinction check:** confirmed this relocated content never states or implies
the ablation replaces or extends the primary 18-scenario evaluation — "does not replace or extend
the primary eighteen-scenario evaluation" remains explicitly stated in §3.9 (untouched). All figures
here (N=4, purposive sampling) stay attributed only to the ablation.

**Placement note:** Follows §4.8's five arguments in Chapter 5's assembly order — this is
explanatory/supplementary material about the primary findings' robustness to hint removal, read
after the primary RQ/H₀ answer and discussion, not before.

---

## Unit 12 — §4.11 Chapter Summary (renamed "Findings Summary" in Chapter 4)

**Source:** §4.11, INTERPRETATION sentence only. OBSERVATION + LIMITATION content stays in Chapter 4
as its closing "Findings Summary" (heading renamed from "Chapter Summary" to reflect its narrowed,
factual-only scope — a heading edit tracking the content change, not a new claim).

**Relocated text (verbatim):**
> Within the evaluated pipeline, the LLM's contribution is observable specifically where a fix must satisfy a dependency-graph constraint (§4.8), bounded by what the surrounding pipeline can actually observe (SBOM completeness) and reach (single- vs. multi-manifest applications); §3.8 states the scope within which this contribution is claimed relative to the deterministic baseline. The explanatory ablation (§4.10) indicates this dependency-graph reasoning does not depend on being supplied the scanner's fixed version: strategy selection was unchanged by hint removal in all four scenarios examined, while the specific version recommended was not, suggesting the model's contribution lies more in identifying *how* to apply a fix than in reproducing the scanner's own recorded value for *which* version to apply.

**Placement note — this is the natural opening of Chapter 5.** It's the shortest, most synthesis-level
statement in the whole staged set, referencing both the case-study findings (§4.8's argument) and
the ablation (§4.10) as supporting context — matches the template's explicit guidance that Discussion
should "start... with a short summary of your findings, just in maximum three sentences." Recommend
this sentence opens Chapter 5, ahead of the Unit 8 RQ-answer/H₀ blocks.

**Primary-vs-ablation check:** the ablation is named explicitly ("The explanatory ablation (§4.10)
indicates...") and its finding is stated as *supporting/consistent with* the primary finding, not
as independent proof or a replacement for it — no drift into treating ablation evidence as primary.
