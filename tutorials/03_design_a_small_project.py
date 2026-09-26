"""Tutorial 03: designing and recording a small, reproducible experiment.

Run from the repository root after installation:

    python tutorials/03_design_a_small_project.py

This tutorial uses only the synthetic example, since a real-data reading
pipeline (opening a downloaded TDMS file into an array) is not implemented yet
(see docs/architecture.md, "Protected TODOs"). The project-record concept
demonstrated here is the same one that would apply to real data later.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.signal import butter, filtfilt

from das_student_lab import format_summary, make_synthetic_whale, summarize_array


def bandpass_filter(
    data: np.ndarray, sample_rate_hz: float, low_hz: float, high_hz: float
) -> np.ndarray:
    """Apply a zero-phase Butterworth bandpass filter. Same approach as Tutorial 02."""

    nyquist = sample_rate_hz / 2
    b, a = butter(4, [low_hz / nyquist, high_hz / nyquist], btype="band")
    return filtfilt(b, a, data, axis=1)


def main() -> None:
    print("Learning goal: build a project record that would let someone else")
    print("reproduce this exact experiment without asking you any questions.\n")

    print(
        "Prediction: if you only saved the output plot from an experiment, "
        "with no other file, what specific things would a stranger be unable "
        "to figure out just by looking at that plot? Write down at least two "
        "before continuing.\n"
    )

    # These are the experiment's actual parameters. Recording them explicitly,
    # rather than leaving them buried in code, is the core idea of this tutorial.
    parameters = {
        "seed": 7,
        "channels": 96,
        "duration_s": 8.0,
        "sample_rate_hz": 200.0,
        "channel_spacing_m": 2.0,
        "filter_low_hz": 15.0,
        "filter_high_hz": 25.0,
    }

    example = make_synthetic_whale(
        seed=parameters["seed"],
        channels=parameters["channels"],
        duration_s=parameters["duration_s"],
        sample_rate_hz=parameters["sample_rate_hz"],
        channel_spacing_m=parameters["channel_spacing_m"],
    )
    print(example.description)
    print("(All data in this tutorial is SIMULATED, not measured.)\n")

    filtered = bandpass_filter(
        example.data,
        example.sample_rate_hz,
        parameters["filter_low_hz"],
        parameters["filter_high_hz"],
    )

    summary = summarize_array(
        filtered,
        sample_rate_hz=example.sample_rate_hz,
        channel_spacing_m=example.channel_spacing_m,
    )
    print(format_summary(summary))

    # Assemble the actual project record. This is the reproducibility artifact:
    # anyone with this file could regenerate the exact same result.
    record = {
        "project_name": "my_first_das_project",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "data_source": (
            "Synthetic data only (make_synthetic_whale). No external dataset "
            "was used in this run; a real-data version of this tutorial "
            "requires a TDMS reading adapter that does not exist yet."
        ),
        "dataset_citation": None,
        "parameters": parameters,
        "processing_steps": [
            f"Butterworth bandpass filter, order 4, "
            f"{parameters['filter_low_hz']}-{parameters['filter_high_hz']} Hz "
            "(scipy.signal.butter + filtfilt)"
        ],
        "software": {
            "das_student_lab": "0.0.1",
            "numpy": np.__version__,
        },
        "output_summary": {
            "shape": f"{summary.channels} channels x {summary.samples} samples",
            "duration_s": summary.duration_s,
            "distance_span_m": summary.distance_span_m,
            "mean": summary.mean,
            "standard_deviation": summary.standard_deviation,
        },
        "labels": {
            "data_type": "SIMULATED",
            "warning": (
                "This record describes a synthetic, pedagogical example. It is "
                "not measured data and must not be cited as a real acoustic "
                "observation."
            ),
        },
    }

    output_dir = Path("projects") / record["project_name"]
    output_dir.mkdir(parents=True, exist_ok=True)
    record_path = output_dir / "project_record.json"
    record_path.write_text(json.dumps(record, indent=2))

    print(f"\nProject record saved to: {record_path}")
    print(
        "\nSoftware: das_student_lab (this project), NumPy, SciPy"
    )
    print(
        "Note: this run used only synthetic data, so dataset_citation is null "
        "in the saved record. A real-data run would set it to the OOI citation."
    )

    print("\nQuestions to answer in your own words:")
    print("1. Open projects/my_first_das_project/project_record.json. Could you")
    print("   regenerate this exact array from what's recorded there alone?")
    print("2. Why is dataset_citation set to null here instead of just omitted")
    print("   from the record entirely?")
    print("3. If you changed filter_low_hz and reran this tutorial, would the")
    print("   old record be overwritten or lost? Is that a problem, and why?")
    print("4. What would need to be added to this record before it could")
    print("   describe a real OOI download instead of synthetic data?")


if __name__ == "__main__":
    main()
