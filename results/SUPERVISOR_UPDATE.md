# Thesis Progress & Methodology Update
**Date:** July 26, 2026

## 1. Executive Summary
The primary objective of my thesis is to evaluate whether Large Language Models (LLMs) can safely remediate software supply chain vulnerabilities (via SBOMs) better than deterministic, static version bumps.

I have successfully built a closed-loop DevSecOps pipeline that automates this entire process: from vulnerability discovery (Grype) to LLM reasoning (Gemini 2.5 Flash), manifest patching, and finally, strict validation (building the app and running tests). 

The initial prototype phase successfully proved that the LLM is highly deterministic and capable of applying complex patches. However, I recently overhauled my methodology to ensure the final dataset is scientifically rigorous, completely unbiased, and defensible for an academic defense.

## 2. Completed Milestones (Methodology Overhaul)
To ensure the integrity of the experiment, I have instituted the following critical corrections to the protocol (documented in my formal Pre-Registration Amendment):

1. **Structured LLM Output:** I migrated the LLM from outputting raw, ecosystem-specific strings (which failed on PyPI) to a structured, ecosystem-agnostic JSON schema (`{"operation", "package", "constraint"}`). This guarantees the pipeline can seamlessly repair both npm (JavaScript) and PyPI (Python) applications.
2. **Dual-Metrics Tracking:** A vulnerability disappearing from a scanner does not mean the application still works. I enhanced my telemetry to track two metrics simultaneously: 
   - `failure_stage`: Where did the pipeline break?
   - `validation_stage_reached`: How far did the application successfully get? (e.g., did it pass the build phase but fail the unit tests?)
3. **Pure Manual Baseline:** I realized that allowing the LLM to "assist" the human control group would contaminate the results. The manual baseline will now be strictly 100% human, starting from the exact same vulnerable commit as the LLM pipeline.
4. **Data Governance & Auditability:** Every single execution now strictly archives its inputs, reasoning (LLM Request/Response), and metrics into a flat directory structure. This ensures I have a permanent, cryptographic trail of evidence for every scenario, even if CI/CD servers delete old logs.

## 3. Remaining Roadmap to Completion

With the methodology fully hardened, the slate has been wiped clean of my initial prototype runs. The remaining steps to complete the experiment and generate the final dataset are:

### Step 1: Re-validate JS-01 & JS-08
I will run fresh executions of my initial test cases (`vm2` and `body-parser`) through the newly hardened pipeline. This ensures 100% of my data uses the exact same protocol.

### Step 2: The 18-Scenario Execution Loop
I will automatically push all 18 pre-registered scenarios through the GitHub Actions pipeline. For each scenario, the pipeline will attempt to apply the LLM's fix, build the app, and re-scan it. I will pull down the complete evidence trail (logs, metrics, LLM reasoning) for all 18 runs.

### Step 3: The Manual Control Group
I will perform a pure, unassisted human remediation for the same 18 scenarios to establish a strict comparison baseline.

### Step 4: Thesis Synthesis & Analysis
With the data collected, I will aggregate the metrics, compare the LLM's success rate against the human baseline, analyze the failure stages (e.g., why did a patch break a build?), and synthesize the findings directly into the final thesis documentation.
