# Changelog

All notable changes should be documented here.

## [Unreleased]

### Added

- Starter package structure.
- Deterministic synthetic DAS-like example.
- Basic array diagnostics.
- OOI citation metadata.
- Baseline tests and CI.

## [0.0.1] — 2026-08-19

## Unreleased

### Added
- Tutorial 07: sampling, aliasing, and what decimation can and cannot undo.

- Tutorial 08: frequency wavenumber filtering, separating signals by apparent speed.

## 0.1.1 (2026-11-23)

### Added
- `metrics.window_snr_db`: a window power ratio in decibels, with validation of overlapping, empty and non finite windows.
- Tutorials 05 (measuring filter width against SNR) and 06 (reading spectrograms), in the repository.

### Changed
- `fetch_ooi_example` now verifies downloads against a pinned SHA-256, downloads to a temporary file, quarantines bad files as `.corrupt`, checks free disk space first, gives an actionable offline error, records the retrieval time in the manifest, and reuses a verified cache without touching the network.
- Package description and README rewritten for the published package.
- Continuous integration installs the science extras; lint line length is 100.
- Tutorial 03 records the installed package version instead of a hardcoded one.

Internal scaffold only. Not a public scientific release.

