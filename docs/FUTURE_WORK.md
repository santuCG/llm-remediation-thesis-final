# Future Work

> **Superseded (2026-08-02):** the consolidated, thesis-facing future-work list is now `../THESIS_FUTURE_WORK.md` at the repository root, with the full 4-category classification in `THESIS_IMPROVEMENTS.md`. This file is retained as the original audit-time record.

Research Enhancements identified during the pre-freeze reproducibility audit (see `docs/audit/`). Each was deliberately **not** implemented before freeze because it changes what the LLM is asked to produce, what information it has access to, or how the experiment's success criteria are defined — implementing any of them would mean evaluating a different experiment than the one this thesis reports.

---

## 1. LLM Confidence Score

**Motivation:** The current pipeline records whether the LLM's remediation succeeded or failed, but not how confident the model was in its own recommendation. A confidence signal could distinguish "the LLM was right and knew it" from "the LLM got lucky."

**Expected benefits:** Enables correlation analysis between stated confidence and actual remediation success — a calibration study.

**Research question enabled:** *Is an LLM's self-reported confidence in a dependency-remediation strategy predictive of its actual correctness?*

**Estimated implementation effort:** Medium — requires a prompt-template change (asking the model to emit a confidence value in a structured field) and a corresponding response-parsing/metrics change.

**Would existing experiments need to be rerun?** Yes, for all 18 scenarios — confidence scores are meaningless if only a subset of remediation attempts were asked to produce them.

**Suitability:**
- MSc extension: Strong fit — a bounded, well-defined follow-up study.
- Journal paper: Suitable as part of a broader "LLM calibration for security remediation" paper.
- PhD research: Could be one chapter/experiment among several on LLM self-assessment reliability.
- Production system: High value — a low-confidence flag could route recommendations to human review.

---

## 2. Improved Prompt Engineering

**Motivation:** The current prompt (`context_builder.py`) provides a fixed structure of vulnerability/package/CVSS/EPSS context. Richer prompting (e.g., more remediation examples, structured reasoning steps, explicit constraint statements) is a plausible lever for improving remediation quality.

**Expected benefits:** Potentially higher remediation success rate; potentially more consistent `remediation_type`/`strategy` classification.

**Research question enabled:** *Does prompt structure materially affect an LLM's dependency-remediation success rate, independent of model choice?*

**Estimated implementation effort:** Medium-high — prompt redesign, plus re-establishing a new baseline across all 18 scenarios to make any comparison meaningful (comparing new-prompt results against old-prompt results only tells you something if both are run under otherwise identical conditions).

**Would existing experiments need to be rerun?** Yes, all 18 — a new prompt on a subset of scenarios can't be fairly compared to the old prompt on the rest.

**Suitability:**
- MSc extension: Good fit if scoped as "prompt A vs. prompt B" ablation.
- Journal paper: Suitable as a full standalone contribution (prompt engineering for security remediation).
- PhD research: Could anchor a full chapter on prompt sensitivity in security-critical LLM tasks.
- Production system: High relevance — this is exactly the kind of tuning a production deployment would need.

---

## 3. Improved Retry Prompt Using Failure Logs — CORRECTED, this item was already implemented

**Correction (added during documentation synchronisation, 2026-08-02):** this item originally described failure-log-informed retry as unimplemented future work. That was a classification error in the original Phase 9.5 assessment. The mechanism was implemented on 2026-07-24 (`scripts/remediation/retry_remediation.py`, `scripts/remediation/llm_reasoner.py`), well before this document was written, and is exercised in the frozen dataset: `results/execution_evidence/JS-05/llm-request.json` and `JS-08/llm-request.json` both contain a "Previous Attempt Failure Logs" section with the actual prior-attempt build/validation log tail, fed to the retry. This is documented as part of the current methodology in `docs/03-llm-configuration.md` ("Retry Prompt Augmentation") and `docs/04-experimental-methodology.md` (Stage 6). There is no remaining future-work item here; the original text below is struck through and retained only for the audit record.

~~**Motivation:** Currently, the one-retry mechanism (AGENTS.md rule 5) re-invokes the LLM without feeding back *why* the first attempt failed (build error, test failure, etc.). Giving the model its own failure diagnostics on retry is a natural next step.~~

~~**Expected benefits:** Could improve the retry's success rate meaningfully, since the model would have concrete, specific information about the failure mode rather than repeating a similar attempt blind.~~

~~**Research question enabled:** Does providing failure diagnostics on retry improve an LLM's ability to correct a failed remediation attempt, compared to a blind retry?~~

~~**Estimated implementation effort:** Medium — extend `retry_remediation.py` / the retry prompt-construction path to include captured `build.log`/`test.log` content, with appropriate truncation/sanitization.~~

---

## Note on scope discipline

Items 1 and 2 above were evaluated against the same criterion: *does this change what the LLM sees, produces, or how the experiment measures success?* Where the answer was yes, the item was deferred here rather than implemented, regardless of how small the code change would be — the distinction that matters for scientific integrity is not effort, but whether the frozen 18-scenario dataset would still be evaluating the same experiment afterward. Item 3 was removed from this list per the correction above: it describes a mechanism that was already implemented before this document was written.
