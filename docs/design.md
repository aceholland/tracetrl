# TraceTRL design

Approved direction: evidence-focused hybrid assessment; adapted for the user's 16 GB HP Pavilion.

Build a Stage 1 Python AssessmentModule for APCTT kit 0.5.0. Read case PDFs, assess the supplied checklist, cite exact page-local spans, and estimate readiness relative to the target and intended use. CPU only. No network during inference, public weights in the organizer store only, no training. Use MIT for original work.

The primary constraint is presently free memory, not installed RAM: approximately 0.6 GiB was available during discovery, and C: had approximately 3.6 GiB free. The default must import only stdlib and pypdf. Process pages incrementally, bound retained text/passages, and retain the top three distinct evidence pages. A small optional all-minilm-l6-v2 encoder can rerank retrieved candidates; leave it disabled until measured with more free RAM. Never interpret embedding similarity alone as proof.

Approaches considered: lexical rules (fast but limited language coverage); hybrid retrieval with a catalogue encoder and explicit evidence rules (selected); whole-report LLM reasoning (too much runtime and memory uncertainty for this laptop). The delivered baseline is lexical; the optional hybrid path requires real-weight benchmarking before enabling in a final submission.

Files: participant_module/adapter.py implements the four lifecycle methods; evidence.py handles bounded PDF extraction and passage ranking; reasoning.py assesses criteria and maturity; semantic.py contains the lazy offline encoder. tools/assess.py provides a local CLI, tools/validate.py checks against the untouched kit, tests/ covers adversarial and contract cases. No Stage 2 website in this package.

Criterion IDs come only from the supplied checklist. Recognize supported meanings by description; unknown descriptions receive insufficient evidence. Missing evidence differs from explicit failure. Future plans and self-reported TRL numbers cannot establish maturity. Check target overlap and explicit operational/laboratory setting. Do not infer every lower criterion is met from a higher maturity finding. Preserve positive and negative evidence; conflicting evidence for maturity causes abstention. Incomplete extraction and deadline exhaustion cause abstention with no unsupported completed result.

The optional encoder is pinned to the kit's all-minilm-l6-v2 revision and loads with local_files_only=True. No LLM, CUDA requirement, external API, or automatic weight download. Its availability is not required for the default package.

Verification: unit tests with real generated PDFs, the official result validator and official pack/check tools, public USGS smoke cases if downloadable, measured time/memory for the default path. Windows direct checks are not the official Linux/WSL2 runner. The local Python is 3.13.3, not the frozen 3.12 base; report this limitation. No claims of hidden-set accuracy or calibrated confidence. The team identity must be confirmed before portal submission. Source can be prepared for aceholland; never push under the currently connected AyushPaul26 account by mistake.
