# Claude Code Instructions

Read this file before acting. These instructions apply throughout the repository.

## Mission

Support David in building a beginner-facing, reproducible learning layer for Distributed Acoustic Sensing data. Do not turn the repository into a duplicate of DASCore, DAS4Whales, or published OOI fin-whale localization code.

## Existing work that must be respected

- DASCore: https://dascore.org/
- DAS4Whales: https://das4whales.readthedocs.io/en/latest/
- GPL-3.0 OOI localization repository: https://github.com/Ocean-Data-Lab/Goestchel_JASA_2025b
- OOI dataset DOI: https://doi.org/10.58046/5J60-FJ89

Never characterize their functionality as David's invention. Do not copy code without checking and complying with its license. Prefer public APIs and citations.

## Authorship protocol

- For scientific algorithms, first ask David for a method note, equations or pseudocode, units, assumptions, and planned tests.
- Work in small, reviewable patches.
- Explain a proposed change before implementing it.
- Do not fabricate results, citations, user feedback, dataset URLs, file sizes, approval, or novelty.
- If David cannot explain a core function, recommend that he not merge it.
- Prompt David to update `docs/decision-log.md` and `docs/research-log.md` in his own words.

## Engineering rules

- Preserve the `src/` layout and modern `pyproject.toml` packaging.
- Public functions require type hints, shapes, units, assumptions, and actionable errors.
- Tests must be deterministic and include failure cases.
- Never silently infer units or dimension order.
- The default path must not download more than 500 MB.
- Any real-data operation must preserve DOI, source path/URL, subset, checksum, parameters, and software versions.
- Synthetic data must always be labeled synthetic and pedagogically simplified.
- Do not add WHOI branding or imply institutional endorsement.
- Do not implement the R package until Python version 0.1 is stable.

## Required checks

Before saying a coding task is complete, run:

```bash
python -m pytest
python -m ruff check .
python -m build
```

Report the actual results. If a command cannot run, state why.

## Current protected TODOs

Do not implement these in the first session:

- OOI downloader/caching.
- DASCore or DAS4Whales adapters.
- Detection, matched filtering, moveout fitting, or localization.
- A public release license.

Begin by orienting David, running baseline checks, and proposing one small learning task.

