# DAS Student Lab

A Python package and tutorial set that takes a student from an unfamiliar distributed acoustic sensing (DAS) file to a documented, reproducible first experiment, without downloading or understanding a 26 TB archive first.

**Status:** version 0.1.0, pre alpha, built as a learning project. It is a teaching tool, not a validated scientific instrument, and it does not detect or locate whales.

```bash
pip install das-student-lab
```

The tutorials also need the science extras (DASCore, SciPy, Matplotlib, nptdms) and are run from a clone of this repository. See Setup below.

## What this package does

- Generates a deterministic, explicitly synthetic time and distance array.
- Summarizes any channels by time array: shape, duration, distance span, memory, dtype, mean, standard deviation, frequency resolution, and invalid values, with input validation and a 500 MiB size guard.
- Downloads one small real OOI recording with a size check, explicit confirmation, a pinned SHA-256 checksum, an interruption safe download, quarantine of bad files, a disk space check, and a provenance manifest that includes the dataset citation and retrieval time.
- Reads a bounded subset of channels from a Silixa TDMS file, using the sample rate and channel spacing stored in the file itself.
- Converts arrays into DASCore Patch objects so DASCore's own tools, such as `pass_filter`, work on this project's data.
- Measures signal to noise in a chosen window pair, and refuses overlapping, empty, or non finite windows.
- Includes eight tutorials: what DAS data is, waterfall plots and filtering on synthetic data, recording a reproducible project, a first look at real measured data, measuring filter performance instead of judging it by eye, reading spectrograms, sampling and aliasing, and separating signals by speed with frequency wavenumber filtering.
- Includes unit tests and continuous integration on Python 3.10, 3.12, and 3.13.

## What it does not do

- Whale detection, matched filtering, moveout fitting, or localization.
- Claim that the synthetic generator is a validated acoustic propagation model.
- Provide a DAS4Whales adapter, or read Optasense HDF5 files.
- Include a recording that contains an actual whale call. The one real example is a short instrument noise check.

## License and affiliation

MIT licensed, see `LICENSE`. This is an independent student project with no institutional affiliation or publication claim.