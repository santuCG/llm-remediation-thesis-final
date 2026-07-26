# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-07-26

### Added
- `docs/methodology_evolution_record.md`: Formalized historical methodology shifts from manual local execution to the automated GitHub Actions pipeline.
- `results/scenarios/`: New structured JSON database for scenario tracking, segregating pre-registration metadata from post-experimental pipeline execution evidence.

### Changed
- **Terminology Sanitization**: Executed a global repository rewrite to enforce strict academic language. All informal pronouns ("we", "our") and subjective AI terminology ("The AI decided") were replaced with objective passive voice ("it was observed", "the autonomous workflow").
- **README.md**: Removed references to individual supervisor names to anonymize repository.
- **preregistration/PRE_REGISTRATION_AMENDMENT.md**: Sanitized documentation of approval processes.
- **docs/08-cicd-pipeline-poc.md**: Formalized pipeline proof-of-concept language.

### Removed
- **Legacy Methodology Files**: Relocated obsolete files to `archive/` to declutter active repository paths.

### Archived (Moved to `archive/`)
- `archive/legacy_methodology_docs/METHODOLOGY_SECURITY_AUDIT.md`
- `archive/legacy_methodology_docs/THESIS_LEGACY_RUN_INSIGHTS.md`
- `archive/legacy_methodology_docs/supervisor_demo.md`
- `archive/legacy_methodology_docs/pilot_data_trace.md`
- `archive/legacy_manual_scripts/gemini_remediation.py`
- `archive/legacy_manual_scripts/run_pilot_llm.py`
- `archive/legacy_manual_scripts/run_js_manual_validation.py`
- `archive/legacy_manual_scripts/run_af_manual_validation.py`
- `archive/legacy_manual_scripts/audit_scenarios.py`
- `archive/legacy_manual_scripts/finalize_repo.py`
- `archive/legacy_manual_scripts/run_18_scenarios_gh.py`
- `archive/legacy_manual_scripts/scratch.py`
