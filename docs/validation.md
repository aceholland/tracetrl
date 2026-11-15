# Validation record

Date: 2026-11-15. Registered team: AceSentry. Package: tracetrl-cpu 0.1.0.

## Completed Windows direct checks

- Official CPU kit 0.5.0: all 129 manifest entries matched SHA-256.
- Python 3.13.3, pypdf 6.19.0. 24 unittest cases passed, including real generated PDFs and CLI subprocess execution. The suite includes nine regressions addressing the independent review findings.
- The untouched kit's result validator accepted its example and the three public diagnostic reports with zero output issues.
- The default path did not import torch. Optional semantic ranking has not been run with real weights.
- Final package check: VALID_WITH_REVIEW, zero errors; the declared USGS public-domain data source is a licence review item under the kit policy. This is retained transparently rather than removed or relabelled.

## Public-report smoke results

Measurements from docs/benchmark.json, including Python startup and direct contract validation. Sampled process RSS is not a hard peak guarantee or total system memory.

| Case | Wall time | Sampled peak RSS | Result | Met criteria | Contract issues |
|---|---:|---:|---|---:|---:|
| USGS-SDG-012 | 2.774 s | 47.11 MiB | abstained | 0 | 0 |
| USGS-SDG-040 | 3.219 s | 52.91 MiB | abstained | 0 | 0 |
| USGS-SDG-061 | 4.631 s | 73.00 MiB | abstained | 1 | 0 |

These are execution and format checks, not an accuracy benchmark. The baseline abstained on every real smoke case; **coverage is limited and competition quality is unproven**. Synthetic tests demonstrate some supported maturity paths, not real-world accuracy. No hidden-set score, expert criterion labels or calibrated confidence is available. Do not present this as a high-performing final assessor.

## Independent review and corrections

A separate reviewer reproduced issues with adjacent unrelated subjects, negated successful operation, missing measured results, scheduled future tests, wrong operational environment, image-only reports, custom criteria containing a TRL number, comparison reports that describe failure, and missing conflict citations. Regression tests were observed failing before the corrections, then the complete 24-test suite passed.

Target evidence is now restricted to target-bearing sentences plus immediate anaphoric results. Known criterion descriptions are matched in full, with IDs always supplied by load(). Partial image-only extraction causes abstention. Conflict results retain both supporting and contradictory excerpts. These remain heuristic safeguards rather than a general natural-language understanding guarantee.

## Linux worker checks

Ubuntu with Python 3.12.3 and the kit's exact requirements-dev.lock: all 24 tests passed. The official kit HTTP server verified the package hash and ran a fresh worker for its example and all three public smoke cases. All four results came from the module, abstained without errors, and had no output issues. See linux-worker-validation.json. This used the server development environment, not the complete frozen CPU base.

## Remaining checks

- The [complete hosted workflow passed](https://github.com/aceholland/tracetrl/actions/runs/43728636767) on code commit 34ca75b89db73fb5a75592d1e8d25748d95a680b: official CPU base build/inventory check, 24 tests, official result validation, and packing. See hosted-base-check.json, hosted-example-validation.json and hosted-package-check.json. The checked hosted-built ZIP is the user-facing AceSentry_submission.zip.
- Optional encoder cold-start runtime, memory and usefulness require a real-weight benchmark before it is enabled.
- No submission form has been sent. GitHub publication and portal submission are separate actions.

## Final artifact

- ZIP SHA-256: `94ccff49d3d6ec9f8cc07f18de1eaba08409bd9c32577284bfe1f8d0d0490844`
- Package SHA-256: `04062e3d1c4b9884c78d348775367c2842424bf6d81e36fbc82e4c20d69db2cb`
- Size: 15,657 bytes. Official intake checker: VALID_WITH_REVIEW, zero errors, one declared USGS source licence review item.
- A Git archive exported into a separate directory also packed with the same package hash. .gitattributes preserves hash-sensitive files across Windows and Linux; assets/.gitkeep preserves the required directory in checkouts.
