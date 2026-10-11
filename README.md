## Install

Requires Python 3.10 or newer.

```bash
git clone https://github.com/dabidolee/DAS-Student-Lab.git
cd DAS-Student-Lab
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,science]"
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead.

Run the tests:

```bash
python -m pytest
```

Run the first tutorial:

```bash
python tutorials/01_inspect_synthetic_data.py
```

## How this project was built

I wrote the package, tutorials, tests, and logs, and used AI coding assistants (Claude Code and ChatGPT) for explanations, scaffolding, debugging, and review. `AGENTS.md` holds the rules those tools followed. Design choices are recorded in `docs/decision-log.md` and `docs/research-log.md`.

## Required data citation

Wilcock, W., & Ocean Observatories Initiative. (2023). *Rapid: A Community Test of Distributed Acoustic Sensing on the Ocean Observatories Initiative Regional Cabled Array* [Data set]. Ocean Observatories Initiative. https://doi.org/10.58046/5J60-FJ89

This repository is not affiliated with or endorsed by OOI, the University of Washington, WHOI, DASCore, or DAS4Whales.
