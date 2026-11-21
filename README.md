# DAS Student Lab

A beginner friendly Python package for learning distributed acoustic sensing (DAS). It takes a student from an unfamiliar DAS array to a documented, reproducible first experiment, using synthetic data and a real ocean cable example from the Ocean Observatories Initiative.

Status: early release (v0.1.0). The tools and tutorials below work. Whale detection and localization are not part of this package yet.

## What it does

- Installs as a modern `src` layout Python package.
- Generates a deterministic, explicitly synthetic time and distance array.
- Summarizes array shape, duration, distance span, memory, data type, mean, standard deviation, frequency resolution, and invalid values.
- Downloads a small, real, checksum verified OOI example file, with size limits, caching, and a provenance manifest.
- Reads a bounded subset of channels from a real Silixa TDMS file into a NumPy array (`read_tdms_subset`, with a 500 MiB safety limit).
- Converts arrays into DASCore Patch objects, so DASCore tools like `pass_filter` work on this project's data.
- Includes five tutorials: what DAS data is, waterfall visualization and filtering on synthetic data, recording a reproducible project, a first look at real measured data, and measuring filter performance instead of judging it by eye.

## Tutorials

1. `01_inspect_synthetic_data.py`: what DAS data is and how to read an array summary.
2. `02_from_array_to_visible_signal.py`: waterfall plots and filtering on synthetic data.
3. `03_design_a_small_project.py`: recording a reproducible project.
4. `04_real_data_first_look.py`: a first look at real measured OOI data (an instrument noise check, not a
