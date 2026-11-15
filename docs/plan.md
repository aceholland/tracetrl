# TraceTRL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a lightweight, evidence-grounded Stage 1 package and reviewable source for aceholland.

**Architecture:** Bounded page extraction and lexical retrieval feed explicit criterion rules. An optional offline MiniLM encoder reranks candidates; the default runs without torch. The adapter returns the supplied contract and the kit makes the ZIP.

**Tech Stack:** Python 3.12 target, pypdf 6.19.0, unittest; optional sentence-transformers 5.7.0.

**Spec:** docs/design.md

## Global Constraints

- CPU only; no network during inference.
- Kit 0.5.0; base_id apctt-base-9e7fe1324bb6; 180000 ms including cold load.
- MIT original code; no public model weights or environment in the ZIP.
- Default imports no torch; optional model is catalogue all-minilm-l6-v2 only.
- Preserve exact page-local quotations; do not hard-code criterion IDs.
- Native Windows validation is limited; final Linux base execution remains separate.

## Review Focus

- Future work and quoted TRL assertions cannot establish achieved maturity.
- Unrelated systems on the same page cannot establish target maturity.
- Negative and conflicting evidence must not become affirmative claims.
- Empty/scanned PDFs and deadline exhaustion must produce a valid abstention.
- Changed IDs, unknown criteria and multiple documents must retain exact contract coverage.

## Tasks

### Task 1: Evidence and assessment core
**Files:** participant_module/{adapter,evidence,reasoning}.py; tests/test_assessment.py; tests/pdf_fixture.py.
**Interfaces:** AssessmentModule.load(config, asset_root), assess(case, context), reset_case(), close(); extract_passages(case, context, settings) -> (list[Passage], complete); assess_passages(case, checklist, passages) -> result fields.
- [ ] Write tests for laboratory readiness, exact quotes/pages, future work, explicit failure, unrelated targets, operational deployment, unknown criteria, changed IDs, blank PDFs, multiple documents and exhausted budget.
- [ ] Run `python -m unittest discover -s tests -v`; observe missing implementation failures.
- [ ] Implement bounded PDF extraction, passage ranking, explicit evidence rules and adapter lifecycle.
- [ ] Run the full unittest suite until green.

### Task 2: Optional encoder and local CLI
**Files:** participant_module/semantic.py; tools/assess.py; tests/test_cli.py.
**Interfaces:** SemanticRanker(model_store: Path); rank(query: str, passages: list[Passage]) -> list[Passage]; CLI takes target, PDFs and checklist, outputs JSON.
- [ ] Add a subprocess CLI test using a generated PDF and literal target; require valid JSON and page references.
- [ ] Observe test failure, implement CLI and lazy offline reranking.
- [ ] Keep use_semantic=false by default; never silently download weights.
- [ ] Run the full suite. Real encoder inference is pending an actual model-store benchmark.

### Task 3: Official validation and delivery
**Files:** submission.json; declaration.json; README.md; participant_module/{LICENSE,THIRD_PARTY_NOTICES.md}; tools/validate.py; docs/validation.md; .github/workflows/test.yml.
**Interfaces:** tools/validate.py --kit PATH validates generated results using Checklist and validate_result from that exact kit.
- [ ] Add package metadata, licensing, truthful data provenance and Linux/Windows run instructions.
- [ ] Verify the downloaded kit manifest; run official result validation.
- [ ] Run official make_submission.py and --check; keep the package draft until registered team identity and final Linux verification are resolved.
- [ ] Review the source independently and fix material findings, then rerun verification.
- [ ] Prepare GitHub source and source archive; request Aceholland sign-in only when publication is ready.
