# Comparative Case Study: Manual vs. Automated Pipeline Remediation (`vm2`)

## Overview
This document explores the fundamental differences between an autonomous SBOM-based LLM remediation (the pipeline's approach) and a holistic manual remediation (a human developer's approach) for the `vm2` vulnerability (CVE-2023-32314).

## 1. Automated Pipeline Remediation (Our Experiment)

**The Approach (Tunnel Vision):**
The LLM operates under a strict, localized constraint: it only has access to the dependency graph (SBOM), the vulnerability context, and the `package.json` file. 

**The Result:**
- The LLM correctly identified that `vm2` was vulnerable as a transitive dependency via `juicy-chat-bot`.
- It generated a valid JSON payload specifying a `transitive_override` strategy: `{"overrides": {"vm2": "3.9.18"}}`.
- The pipeline injected this into `package.json` and ran `npm install`.
- **The Failure:** Overriding `vm2` forced `npm` to re-evaluate the dependency tree, inadvertently fetching newer minor/patch versions of unrelated transitive types (e.g., `@types/lodash`, `@types/babel__traverse`). These newer types utilize modern TypeScript syntax (TS 4.7+). Juice Shop v15.3.0 relies on TypeScript `~4.6.0`. The outdated `tsc` compiler failed to parse the modern syntax, throwing `error TS1005: '?' expected`, and the pipeline correctly blocked the deployment.

**What went "wrong":** 
The LLM lacks holistic codebase autonomy. It cannot read the build failure logs and perform iterative secondary fixes (such as upgrading the `typescript` version in `package.json` to match the newly installed types). It is a "single-file agent" trapped in the context of the manifest.

## 2. Manual Remediation (Human Developer)

**The Approach (Holistic Context):**
A human security engineer has codebase-wide autonomy, historical context, and the ability to iteratively diagnose build failures.

**The Result:**
- **Step 1:** The human might initially try the exact same override strategy.
- **Step 2 (Iterative Debugging):** Upon seeing the `tsc` compiler error, the human would immediately recognize the TS version mismatch. They would execute a secondary command: `npm install typescript@latest` or manually downgrade/lock `@types/lodash` to a compatible version, thereby fixing the build.
- **Step 3 (Architectural Insight):** Furthermore, a human reading the CVE advisories would realize that `vm2` is fundamentally broken, abandoned by its author, and inherently unpatchable (even `3.9.19` was later proven vulnerable). Instead of a band-aid override, the human would likely refactor the integration entirely, migrating away from `juicy-chat-bot` or forking it to use a secure sandbox like `isolated-vm`.

## 3. Conclusion for the Thesis

The divergent results between the automated pipeline and manual remediation perfectly illustrate a core limitation of localized, AI-driven dependency remediation: **Cascading Codebase Breakage**.

We did not necessarily build the pipeline "wrong"—the pipeline's build phase worked exactly as designed by catching and blocking the application-breaking side effects. However, the paradigm of relying purely on SBOM-level dependency manipulation is insufficient. Real-world vulnerability remediation often requires cascading, multi-file codebase refactoring (e.g., updating compiler versions, altering import statements, or migrating sandbox APIs) which simple manifest surgery cannot accomplish.
