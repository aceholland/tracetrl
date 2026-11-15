# Assessment workflow repair plan

> Use parallel implementation for independent core, UI and runtime tasks; verify the integrated result before delivery.

**Goal:** Run user-uploaded PDFs through the official local kit API and show each criterion's actual evidence beside its PDF page.

**Architecture:** Preserve the existing CPU assessor and editorial website. Add general scientific-language coverage, criterion disclosures, official input limits, and a standard-library bridge to the existing WSL development worker. Package identity is checked before and after every job.

**Constraints:** Offline inference; three PDFs; 50 MiB/file; 80 MiB encoded request; 300 aggregate pages; 180-second worker budget. No model downloads, reference-label inference or forced TRLs. Local development execution is distinct from the full frozen CPU base.

- [ ] Extend analytical/model evidence rules with positive and adversarial tests; retain subject, negation, environment and future-work safeguards.
- [ ] Show all evidence, missing evidence and rationale per criterion, with working source-page buttons.
- [ ] Validate official upload limits and encrypted/unreadable PDFs. Reject 301 aggregate pages, accept 300.
- [ ] Rebuild the Stage 1 ZIP using the untouched official tool and verify its hash.
- [ ] Run actual official API jobs and verify package/result identity; run real and synthetic browser uploads.
- [ ] Push reviewed core changes and run hosted frozen-base checks. Preserve the licence review item honestly.
- [ ] Leave the working result open and provide a local launcher. Record remaining accuracy and deployment limits.
