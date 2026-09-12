# DAS Student Lab — Starter Repository

> Working scaffold for David Lee. This is not a finished scientific package.

DAS Student Lab is a proposed beginner-facing Python package for learning how to inspect DAS arrays, use safely sized examples, preserve data provenance, and begin reproducible experiments with established DAS tools.

## What this starter already does

- Installs as a modern `src/`-layout Python package.
- Generates a deterministic, explicitly synthetic time-distance array.
- Summarizes array shape, duration, distance span, memory, and invalid values.
- Stores the official OOI dataset citation and project URL.
- Includes baseline unit tests and continuous-integration configuration.
- Includes persistent AI-assistant instructions and research/decision logs.

## What is deliberately not implemented

- Public OOI downloading or caching.
- DASCore/DAS4Whales adapters.
- Whale detection, matched filtering, moveout fitting, or localization.
- Claims that the synthetic generator is a validated acoustic-propagation model.
- A final package name, license, institutional affiliation, or publication claim.

David should design and implement those pieces incrementally after reviewing existing tools and consulting Dr. Park.

## Setup

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
```

Run the small command-line status report:

```bash
das-student-lab info
```

Run the first tutorial as a Python script:

```bash
python tutorials/01_inspect_synthetic_data.py
```

## Read before developing

1. `CLAUDE.md` or `AGENTS.md`
2. `docs/architecture.md`
3. `docs/related-work.md`
4. `docs/decision-log.md`
5. `docs/research-log.md`
6. `tests/TODO_TESTS.md`

## Required data citation

Wilcock, W., & Ocean Observatories Initiative. (2023). *Rapid: A Community Test of Distributed Acoustic Sensing on the Ocean Observatories Initiative Regional Cabled Array* [Data set]. Ocean Observatories Initiative. https://doi.org/10.58046/5J60-FJ89

This repository is not affiliated with or endorsed by OOI, the University of Washington, WHOI, DASCore, or DAS4Whales.

