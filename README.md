# TraceTRL

**Offline technology readiness assessment with quotations you can check.**

TraceTRL is an experimental CPU-first Assessment Package for the APCTT Hackathon 2026 Stage 1 contract. It reads technical PDFs, assesses the supplied checklist and returns a readiness estimate with document IDs, 1-based PDF page numbers, exact extracted excerpts and missing-evidence explanations.

The default uses lexical retrieval and explicit evidence rules. It does not use an LLM, train a model, call a remote API or require a GPU. An optional catalogue MiniLM encoder reranks candidate passages. **That encoder is disabled by default and has not yet been benchmarked with real weights.**

## Run locally

Python 3.12 is the competition target. A small direct smoke runner also works on Windows; it is separate from the official Linux/WSL2 worker.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m unittest discover -s tests -v
.venv\Scripts\python tools/assess.py --target "optical water-quality sensor" --application "coastal monitoring" --environment "coastal seawater" --checklist tests/fixtures/checklist.json report.pdf --output assessment.json
```

On Linux, use `.venv/bin/python` instead. The checklist fixture is the official checklist from kit 0.5.0; the module always uses the checklist supplied to `load`, including its IDs. Unknown criterion meanings are left as insufficient evidence.

The CLI writes JSON to stdout or `--output`; timing goes to stderr. Cite PDF page indices, not printed report page labels. Provide the actual assessment target rather than the whole parent project.

## What it checks

- Extract PDF text a page at a time; keep excerpts on their original page.
- Retrieve passages using lexical relevance and target-term overlap.
- Apply separate rules for scientific principles, concept, experiments, laboratory/relevant/operational environments, qualification and sustained operations.
- Reject planned work and unsupported self-reported TRL labels as achieved maturity.
- Keep explicit failed conditions distinct from absent evidence; abstain on contradictory maturity evidence.
- Select at most three distinct evidence pages per criterion. Never generate quotations.
- Return the highest directly supported maturity milestone without automatically marking lower criteria met.

This is a heuristic estimate, not an official TRL certification or calibrated probability. Keyword overlap cannot guarantee correct scope or distinguish every contextual negation. Semantic ranking, when enabled, does not itself prove a claim.

## APCTT package

Obtain the [CPU participant kit](https://drive.google.com/drive/folders/16P-0Jj9mr_vPFGMMATaku8-noS6E7rTo) and follow its README to create the official Python 3.12 base on Linux or WSL2. Do not install extra packages into the frozen base. Local system Python smoke checks are not frozen-base verification.

From this repository, with the kit's environment:

```bash
python tools/validate.py --kit /path/to/apctt-participant-kit-0.5.0-cpu
python /path/to/kit/tools/make_submission.py . --output /path/to/dist
python /path/to/kit/tools/make_submission.py --check /path/to/dist/AceSentry_submission.zip
```

`make_submission.py` selects only `participant_module/`, `assets/`, `submission.json`, `declaration.json` and this README. Source tests, documentation, tools and GitHub workflows stay in the source repository. Public model weights and dependencies never belong in the submission ZIP. The tool computes the package hash.

**Before final submission:** replace `AceSentry` in both metadata files with the registered team name; finish the official Linux worker/base checks; review representative real-report results; run pack and check again. Upload the resulting ZIP through the [submission form](https://forms.gle/sU21rDGVDULzWExY9). Pushing to GitHub does not submit an entry. No portal submission has been made by this project.

## Optional semantic retrieval

The only supported encoder is catalogue `all-minilm-l6-v2`, pinned revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41` (about 92 MB download). Download using the kit's `tools/get_models.py all-minilm-l6-v2 --store /path/to/models`, then set `APCTT_MODEL_STORE` to that store. Use the official base's sentence-transformers installation, not the small smoke-test environment above.

For local experiments, add `--semantic`. For a semantic competition package, set `submission.json.settings.use_semantic` to `true` and `models` to `[{"catalog_id": "all-minilm-l6-v2"}]`, then regenerate the ZIP. Load is offline only, CPU only, with two torch threads and batch size four. Benchmark cold loading plus assessment against the 180-second budget before selecting this configuration. The default package has `models: []` and imports no torch.

## Limits and validation

No OCR is included: scanned or poorly extracted pages may not supply usable evidence. Default caps are 60,000 extracted characters per page and 6,000 passages per case. If a cap or time guard interrupts assessment, the module abstains rather than silently claiming a complete assessment. These caps bound retained text, not every allocation inside the PDF parser. No hidden-set accuracy has been measured.

See [validation](docs/validation.md), [design](docs/design.md) and [implementation plan](docs/plan.md). Source is MIT. See `participant_module/THIRD_PARTY_NOTICES.md` for dependencies and checklist attribution.
