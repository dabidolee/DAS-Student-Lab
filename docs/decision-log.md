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
- **Status:** Superseded by D-008.
- **Decision:** Defer the public code license until ownership, mentor code, dependency, and GPL adaptation questions are settled.
- **Consequence:** Do not publicly release version 0.1.0 until the decision is complete.

## D-004 — Use Python 3.11 for development

- **Date:** 2026-09-13
- **Status:** Accepted.
- **Decision:** Develop and test using Python 3.11, installed via Homebrew, rather than the system Python 3.8 or Anaconda's base environment.
- **Alternatives:** Continue using Python 3.8; use Anaconda's base Python directly.
- **Reason:** numpy>=1.26, required by pyproject.toml, has no available distribution for Python 3.8. Anaconda's base environment also has PATH conflicts with venv.
- **Consequences:** Contributors must have Python 3.10 or newer installed; README setup instructions may need a note about this.

## D-005 — Use nptdms to read Silixa TDMS files

- **Date:** 2026-09-20
- **Status:** Accepted.
- **Decision:** Use the nptdms library to read the downloaded Silixa TDMS example file, rather than writing a custom binary parser or requiring MATLAB.
- **Alternatives:** Write a custom TDMS parser; require the Silixa MATLAB reader.
- **Reason:** nptdms is a lightweight, actively maintained, pure-Python library built specifically for this file format, avoiding both a MATLAB dependency and the risk of a custom parser getting the binary format wrong.
- **Consequences:** nptdms becomes a new optional dependency under the science extra; reading the file becomes possible but is not yet implemented.

## D-006 — Read TDMS files as bounded channel subsets only

- **Date:** 2026-09-23
- **Status:** Accepted.
- **Decision:** read_tdms_subset only ever loads an explicit, bounded range of channels, never a full TDMS file.
- **Reason:** The full OOI example file has 32,448 channels; loading all as float64 would use ~780 MiB, exceeding this project's 500 MiB safety limit.
- **Consequences:** Students must explicitly choose a channel range; a future adapter could add a "give me a sensible default subset" convenience wrapper.

## D-007 — Build a thin DASCore Patch adapter

- **Date:** 2026-09-25
- **Status:** Accepted.
- **Decision:** Add to_dascore_patch, converting this project's (channels, time) arrays into DASCore Patch objects, so students can use DASCore's own established processing tools (e.g. pass_filter) instead of only scipy.
- **Reason:** DASCore requires a real datetime64 time coordinate, which this project's own data structures don't carry; the adapter bridges that gap without reimplementing any DASCore functionality.
- **Consequences:** For real data, callers should pass the file's actual recording timestamp (e.g. from TDMS GPSTimeStamp) as start_time; synthetic data uses an arbitrary placeholder timestamp that must not be treated as real.

## D-008 — Adopt the MIT License

- **Date:** 2026-09-27
- **Status:** Accepted.
- **Decision:** License the project under MIT.
- **Reason:** Dr. Park confirmed MIT after being consulted about the GPL-3.0 question raised by the related Goestchel et al. repository; no GPL code has been used, so a permissive license is appropriate.
- **Consequences:** LICENSE, LICENSE_DECISION.md, and pyproject.toml all updated to reflect MIT.


## Template

### D-XXX — Short title

- **Date:** YYYY-MM-DD
- **Status:** Proposed / accepted / superseded.
- **Decision:**
- **Alternatives:**
- **Evidence:**
- **Reason:**
- **Consequences:**

