# Third-party notices

No third-party Python source or weights are vendored in participant_module/ or assets/.

- pypdf 6.19.0: BSD-3-Clause, https://github.com/py-pdf/pypdf; imported from the organizer's common base for PDF extraction. The local smoke dependency is the same version.
- Optional sentence-transformers 5.7.0: Apache-2.0; torch 2.11.0: BSD-3-Clause; numpy 2.5.3: BSD-3-Clause; supplied by the common base. Used only when use_semantic=true.
- Optional sentence-transformers/all-MiniLM-L6-v2 at revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41: Apache-2.0, catalogue ID all-minilm-l6-v2. Not shipped, declared or loaded in the default package. A semantic submission must declare it in models[].
- APCTT Participant Kit 0.5.0: MIT, Copyright (c) 2026 APCTT (Asian and Pacific Centre for Transfer of Technology). Its official checklist is copied in source tests/fixtures/checklist.json, and criterion descriptions are used in participant_module/criterion_meanings.json. Its MIT notice is retained at participant_module/licenses/APCTT-KIT-LICENSE and docs/licenses/APCTT-KIT-LICENSE. The adapter implements the published protocol. No kit Python source is copied into participant_module/.

All other runtime imports in the default path are Python standard-library modules. The submitted original rules and code are MIT licensed.
