# Decision Log

Record each important decision, alternatives, evidence, and consequences. David should write the final wording.

## D-001 — Use a thin educational layer

- **Date:** 2026-08-19
- **Status:** Proposed; David must confirm.
- **Decision:** Focus on student onboarding, diagnostics, bounded examples, provenance, and reproducible project templates.
- **Alternatives:** General DAS library; whale-localization library; complete research pipeline.
- **Reason:** DASCore, DAS4Whales, and published OOI localization software already cover substantial general and bioacoustic functionality.
- **Consequence:** Version 0.1 should be judged on learning and reproducibility rather than algorithm count.

## D-002 — Keep scientific dependencies optional initially

- **Date:** 2026-08-19
- **Status:** Proposed; David must confirm.
- **Decision:** Baseline package depends only on NumPy; DASCore, DAS4Whales, SciPy, and Matplotlib are optional science dependencies.
- **Reason:** The offline synthetic tutorial and diagnostics should install quickly. Add mandatory dependencies only when required by a reviewed feature.
- **Consequence:** Integration tests will be needed when adapters are added.

## D-003 — No final license in the starter

- **Date:** 2026-08-19
- **Status:** Temporary.
- **Decision:** Defer the public code license until ownership, mentor code, dependency, and GPL adaptation questions are settled.
- **Consequence:** Do not publicly release version 0.1.0 until the decision is complete.

## Template

### D-XXX — Short title

- **Date:** YYYY-MM-DD
- **Status:** Proposed / accepted / superseded.
- **Decision:**
- **Alternatives:**
- **Evidence:**
- **Reason:**
- **Consequences:**

