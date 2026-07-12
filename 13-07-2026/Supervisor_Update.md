# Research Update and Methodological Refinements

Dear Professor,

This document outlines the recent methodological refinements applied to the thesis experiment, the rationale behind these decisions, and the roadmap for the final execution phase. These updates ensure the highest level of data integrity while satisfying the core architectural requirements of the research proposal.

## 1. Major Methodological Changes and Rationale

We have made a strategic adjustment to how the 18 core scenarios are validated. Originally, the plan was to validate all scenarios using fully autonomous CI/CD pipelines. However, we have transitioned to a systematic, manual execution protocol for the core 18 scenarios.

The rationale for this change is data integrity and experimental control. Automating the LLM execution across 18 complex dependency graphs introduced significant risks of API rate-limiting, arbitrary CI runner timeouts, and hidden package registry network failures. By executing the scenarios manually using a strict step-by-step protocol, we ensure that every LLM recommendation is perfectly recorded and validated without interference from general software engineering or network pipeline errors.

To preserve the architectural requirement of the thesis, which focuses on SBOM-Driven CI/CD Pipelines, we will develop a fully automated, end-to-end CI/CD workflow for exactly two representative Proof of Concept scenarios (one from the NPM ecosystem and one from PyPI). This proves enterprise integration feasibility while keeping the core evaluation focused on the LLM reasoning capabilities.

Furthermore, we executed a repository migration. All previous exploratory CI/CD scripts have been safely archived in an archive branch. The main workspace has been rebuilt into a pristine, defense-ready state that contains only the finalized methodology documentation, pre-registered datasets, and strict validation logs.

## 2. Experimental Findings to Date

Our baseline experiments have definitively proven the limitation of deterministic scanners. Across our initial testing, blindly applying the vulnerability scanner's recommended version resulted in a 100 percent failure rate. The package managers rejected the updates due to strict peer dependency conflicts (ERESOLVE in npm) or constraint collapse (ResolutionImpossible in PyPI).

Conversely, when the Large Language Model was supplied with the dependency graph context and the baseline error trace, it successfully reasoned about the topological constraints. For example, rather than attempting a failing direct installation for a transitive vulnerability, the LLM correctly generated manifest overrides (as validated in our test scenarios like vm2 and body-parser) that successfully patched the vulnerability without breaking the build.

Evidence for these baseline failures and LLM recommendations can be found in the repository under:

- `experiment/deterministic_baseline_results.json`
- `experiment/llm_remediation_results.json`

## 3. Roadmap for Remaining Scenarios

Moving forward, the validation of the remaining scenarios will follow the exact same manual logging protocol established during our initial tests.

For each of the remaining pre-registered scenarios, we will:

- Restore the environment to the clean baseline.
- Inject the LLM's recommended strategy from the results JSON.
- Execute the package manager resolution and pipe the output to a permanent log file in the `results/remediated/` directory.
- Verify the dependency tree manually and log the output.
- Regenerate the SBOM and rescan using Syft and Grype, saving the cryptographic proof of remediation to the `results/reports/` directory.

Once the manual validation of all 18 scenarios is complete, we will construct the final automated Proof of Concept pipeline for the two selected CVEs to finalize the practical engineering component of the thesis.
