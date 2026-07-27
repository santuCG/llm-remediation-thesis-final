# What This Research Is About

**Master's Thesis — Santosh Nagaraj**  
**SRH University Berlin — MSc Computer Science (Cybersecurity)**  

---

## The Problem in One Paragraph

Modern software applications depend on hundreds or thousands of open-source packages. When a security vulnerability is found in one of those packages, a vulnerability scanner tells you which package is affected and what version fixes it. The problem is that simply installing the recommended fix version often does not work — the package manager rejects it because of conflicting version requirements elsewhere in the dependency tree. Developers are left with a scanner telling them what to fix but no practical way to apply the fix automatically. This research asks whether a Large Language Model can bridge that gap by reasoning about the constraints and suggesting a fix strategy that actually works.

---

## The Scientific Contribution

Traditional Software Composition Analysis (SCA) tools treat dependencies as isolated versions, ignoring the holistic dependency graph constraints. This leads to a persistent gap between vulnerability detection and practical remediation, often resulting in a 0% deterministic success rate when applying basic scanner recommendations to strictly pinned graphs.

This Master's thesis introduces a novel, constraint-aware remediation workflow that isolates Large Language Model (LLM) reasoning as a decision-support layer. The scientific contribution of this research is demonstrating whether an LLM can bridge the gap between static vulnerability detection and deterministic topological constraint satisfaction, effectively transforming vulnerability management from a basic suggestion engine into a graph-aware remediation protocol.

---

## The Core Question

> Can an LLM generate dependency remediation strategies that resolve software supply chain vulnerabilities in cases where applying the scanner's recommendation directly fails?

---

## How the Experiment Works

The experiment follows the same sequence of steps for every scenario tested.

1. Take a real application at a pinned version
2. Generate a Software Bill of Materials (SBOM) listing every package and version the app depends on
3. Scan the SBOM with a vulnerability scanner (Grype) to find known vulnerabilities
4. Try to fix the vulnerability the basic way — just install the scanner's recommended version. This fails. Record the failure as the baseline.
5. Collect enrichment signals about the vulnerability (CVSS severity score, EPSS exploitation probability, KEV status)
6. Send all of this context to Gemini 2.5 Flash and ask it to recommend a remediation strategy
7. Apply the LLM's recommendation manually and check whether the package manager accepts it
8. If it works, regenerate the SBOM and rescan with Grype to confirm the vulnerability is gone
9. Compare before and after

---

## The Two Applications Being Tested

| Application | Language | Package Manager | Why Selected |
|-------------|----------|-----------------|--------------|
| OWASP Juice Shop v15.3.0 | JavaScript | npm | Deliberately vulnerable, widely used in security research, large dependency graph |
| Apache Airflow v2.9.2 | Python | pip | Real-world production platform, tightly constrained dependency tree, different ecosystem |

---

## The 18 Scenarios

18 specific vulnerability scenarios were pre-registered before any experiment ran. 9 come from Juice Shop and 9 from Airflow. Each scenario is one CVE in one package.

Pre-registration means the scenarios were locked and documented before the LLM was ever called. This prevents cherry-picking results after the fact.

| Application | Scenarios | Ecosystem |
|-------------|-----------|-----------|
| Juice Shop | JS-01 to JS-09 | npm |
| Airflow | AF-01 to AF-09 | PyPI |

All 18 scenarios returned the same baseline result: the scanner's recommended version could not be applied directly.

- **npm failures:** `ERESOLVE` — peer dependency conflict, package manager rejects the installation
- **PyPI failures:** `ResolutionImpossible` — strict version bounds in the constraints file prevent the upgrade

---

## The Tools Used

| Tool | Version | What It Does |
|------|---------|--------------|
| Syft | 1.44.0 | Generates the SBOM from the application |
| Grype | 0.112.0 | Scans the SBOM for known vulnerabilities |
| Gemini 2.5 Flash | — | Generates the remediation recommendation |
| FIRST EPSS API | v1 | Provides exploitation probability score |
| CISA KEV feed | — | Lists vulnerabilities actively exploited in the wild |
| NVD API | — | Provides CVSS severity scores |

Trivy was excluded — it had a confirmed supply chain compromise in March 2026.

---

## What the LLM Receives

For each scenario the LLM receives a structured prompt containing:

- The vulnerable package name and version
- The CVE identifier and description
- The CVSS severity score
- The EPSS exploitation probability score
- The KEV status (whether it is actively exploited)
- What the scanner recommended
- What error the package manager produced when that recommendation was applied
- The dependency path (whether the package is direct or transitive)

The LLM does not browse the internet. It reasons only over the information provided in the prompt.

---

## What the LLM Returns

The LLM returns a structured JSON object:

```json
{
  "action_type": "OVERRIDE | CONSTRAINT_RELAXATION | DIRECT_BUMP | PACKAGE_REPLACEMENT | DEFER",
  "recommended_version": "exact version string",
  "fix_target": "package name to modify",
  "rationale": "why this strategy was chosen",
  "prioritisation_reasoning": "how CVSS and EPSS influenced the decision"
}
```

This output is treated as a hypothesis, not a result. It only becomes a result after deterministic validation.

---

## How Validation Works

The LLM output goes through four gates before it counts as a successful remediation.

| Gate | What Is Checked | Pass Condition |
|------|----------------|----------------|
| Gate 0 | Does the recommended version actually exist in npm or PyPI? | HTTP 200 from registry API |
| Gate 1 | Does the package manager accept the fix? | Exit code 0 from npm or pip |
| Gate 2 | Does the application build? | No build errors |
| Gate 3 | Does the dependency graph confirm the fix? | npm ls or pip check shows correct version |
| Gate 4 | Is the CVE gone? | Grype no longer reports the CVE in the rescanned SBOM |

A scenario is only counted as successfully remediated if it passes all gates.

---

## What Makes This Different From Just Running the Scanner

The scanner tells you what is wrong and suggests a fix version. It does not understand your dependency graph. It does not know that your version of Airflow pins a constraint that makes the fix version impossible to install. It does not know that vm2 has been abandoned and the real answer is to replace it. It just outputs a version string.

The LLM receives all of that context — the error the package manager produced, the CVSS and EPSS scores, the dependency path — and reasons about what strategy is likely to work given those constraints.

The research question is whether that reasoning produces better outcomes than the scanner's one-dimensional recommendation.

---

## The Three Enrichment Signals

Three signals are provided to the LLM beyond what the scanner gives.

**CVSS** — A score from 0 to 10 measuring how severe the vulnerability is in theory. A CVSS of 9.8 is critical.

**EPSS** — A probability score estimating how likely the vulnerability is to be exploited in the next 30 days. A vulnerability can have CVSS 9.8 but EPSS at the 20th percentile, meaning it is severe in theory but rarely exploited in practice.

**KEV** — The CISA Known Exploited Vulnerabilities catalogue. If a CVE is on this list, it is actively being exploited in real attacks right now.

The research sub-question is whether the LLM weighs these signals differently from a CVSS-only approach, and whether that changes its remediation strategy.

**Known limitation:** All 18 scenarios in this experiment have KEV=FALSE. The CISA catalogue does not contain any of the selected CVEs. This means the KEV signal cannot be tested empirically in this dataset. The thesis acknowledges this as a limitation.

---

## What Has Already Been Done

| Phase | Status |
|-------|--------|
| Application selection and pinning | Complete |
| SBOM generation (lockfile-based) | Complete |
| Grype vulnerability scanning | Complete |
| Pre-registration of 18 scenarios | Complete |
| Baseline experiment (deterministic) | Complete — 18/18 failures |
| LLM remediation generation | Complete for pilot scenarios |
| Manual validation of LLM recommendations | In progress |
| Full 18-scenario analysis | In progress |

---

## What the Baseline Found

Every single scenario failed when the scanner's recommended version was applied directly.

| Ecosystem | Failure Type | Failure Rate |
|-----------|-------------|--------------|
| npm (Juice Shop) | ERESOLVE peer dependency conflict | 9/9 |
| PyPI (Airflow) | ResolutionImpossible constraint collapse | 9/9 |

This 0% baseline success rate is the control group. Any improvement from the LLM approach is measured against this.

---

## What the Thesis Is Not Claiming

This research does not claim that:

- LLMs should replace vulnerability scanners
- LLMs can discover new vulnerabilities
- The approach works for all applications or all ecosystems
- 18 scenarios is enough to generalise broadly
- The results will hold as LLM models change over time

The thesis claims only that within this controlled experiment, with these specific applications and scenarios, contextual LLM reasoning was evaluated as a decision-support layer on top of deterministic scanning.

---

## Ghost CMS — Why It Was Removed

Ghost CMS was originally included as a third application. It was removed mid-experiment when the CI pipeline revealed that Ghost uses yarn as its package manager while the experiment was built around npm for Node.js applications. Mixing yarn and npm would introduce an uncontrolled variable — failures or successes could be attributed to the package manager difference rather than the LLM's reasoning. Ghost was formally disqualified and documented in a pre-registration amendment. This was documented before the experiment continued.

---

## Key Documents in This Repository

| Document / Folder | What It Contains |
|----------|----------------|
| `applications/` | The frozen source code snapshots (Juice Shop v15.3.0 and Airflow v2.9.2), plus raw pre-registration Grype/Syft scans (`applications/evidence/`). |
| `archive/` | Legacy results, temporary files, and historical debug scripts. |
| `docs/` | Comprehensive methodology documentation (`02-experimental-environment.md`, `03-llm-configuration.md`, `04-experimental-methodology.md`, `05-results-and-discussion.md`). |
| `preregistration/MASTER_METHODOLOGY_RECORD.md` | All 18 scenarios, selection methodology, enrichment data. |
| `preregistration/PRE_REGISTRATION_AMENDMENT.md` | Ghost disqualification, scenario changes, baseline results. |
| `progress-reports/` | Status updates and draft records created during the thesis execution (e.g. `27-07-2026/Thesis_Update.md`). |
| `results/scenarios/` | The canonical JSON database. Contains `pre_registered/scenarios.json` and `final_18_scenarios.json`. |
| `results/execution_evidence/` | The golden execution evidence containing raw pipeline logs, extracted LLM traces, and pre/post SBOM scans proving the automated POC succeeded. |
| `scripts/` | Python and bash scripts driving the core automation pipeline and experiment methodology. |
| `tools/` | Core analysis engines and evaluation utilities. |
