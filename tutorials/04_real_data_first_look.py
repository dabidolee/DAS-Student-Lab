"""Tutorial 04: a first look at real, measured DAS data.

Run from the repository root after downloading the example file (Week 3):

    python tutorials/04_real_data_first_look.py

This tutorial uses read_tdms_subset to load a small, bounded piece of a real
Silixa recording from the OOI Regional Cabled Array, the same file fetched by
fetch_ooi_example(). Everything here is MEASURED data, not simulated, and it
is a short instrument noise check, not a labeled whale detection.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt

from das_student_lab.datasets import OOI_DATASET, fetch_ooi_example
from das_student_lab.diagnostics import format_summary, summarize_array
from das_student_lab.tdms_reader import read_tdms_subset


def bandpass_filter(
    data: np.ndarray, sample_rate_hz: float, low_hz: float, high_hz: float
) -> np.ndarray:
    """Same filter approach as Tutorial 02, applied here to real data instead."""

    nyquist = sample_rate_hz / 2
    b, a = butter(4, [low_hz / nyquist, high_hz / nyquist], btype="band")
    return filtfilt(b, a, data, axis=1)


def plot_waterfall(data: np.ndarray, time_s: np.ndarray, distance_m: np.ndarray, title: str) -> None:
    plt.figure(figsize=(8, 5))
    plt.imshow(
        data,
        aspect="auto",
        extent=[time_s[0], time_s[-1], distance_m[-1], distance_m[0]],
        cmap="seismic",
        vmin=-np.max(np.abs(data)),
        vmax=np.max(np.abs(data)),
    )
    plt.xlabel("Time (s)")
    plt.ylabel("Distance along cable (m)")
    plt.title(title)
    plt.colorbar(label="Amplitude (raw instrument units, MEASURED)")
    plt.tight_layout()
    plt.show()


def main() -> None:
    print("Learning goal: see what REAL DAS data looks like, and compare it")
    print("honestly against the synthetic data from earlier tutorials.\n")

    print(
        "Prediction: this file is a short instrument noise check, not a whale "
        "recording. Do you expect the real noise to look the same as the "
        "synthetic noise from Tutorial 01 and 02, or different? If different, "
        "guess one specific way before continuing.\n"
    )

    cache_path = (
        Path.home()
        / ".cache"
        / "das_student_lab"
        / "ooi_examples"
        / "OOIPacCity_UTC_20211101_153340.764.tdms"
    )
    if not cache_path.exists():
        print("Real data file not found in cache. Downloading it now...")
        cache_path = fetch_ooi_example(confirm=True)

    subset = read_tdms_subset(cache_path, first_channel=0, last_channel=99)
    print(f"Loaded real channels {subset.first_channel}-{subset.last_channel} "
          f"from {Path(subset.source_path).name}")
    print("(This is MEASURED data: a real Silixa instrument noise check, "
          "not a whale detection.)\n")

    time_s = np.arange(subset.data.shape[1]) / subset.sample_rate_hz
    distance_m = np.arange(subset.data.shape[0]) * subset.channel_spacing_m

    summary = summarize_array(
        subset.data,
        sample_rate_hz=subset.sample_rate_hz,
        channel_spacing_m=subset.channel_spacing_m,
    )
    print(format_summary(summary))

    print("\nShowing the real, unfiltered data...")
    plot_waterfall(
        subset.data, time_s, distance_m,
        title="Real OOI data (MEASURED, unfiltered, 100 channels)",
    )

    filtered = bandpass_filter(subset.data, subset.sample_rate_hz, low_hz=15, high_hz=25)
    print("Now the same real data, bandpass filtered 15-25 Hz...")
    plot_waterfall(
        filtered, time_s, distance_m,
        title="Real OOI data (MEASURED, bandpass filtered 15-25 Hz)",
    )

    print(f"\nDataset citation: {OOI_DATASET.citation}")
    print("Software: das_student_lab (this project), nptdms, NumPy, SciPy, Matplotlib")

    print("\nQuestions to answer in your own words:")
    print("1. Was your prediction correct? How does real noise compare to")
    print("   the synthetic noise from earlier tutorials, in shape or scale?")
    print("2. The synthetic data's amplitude ranged roughly -1 to 1.5. Check")
    print("   this summary's minimum and maximum. Why might real instrument")
    print("   units be so different in scale?")
    print("3. This file is labeled a 'noise check', not a whale detection.")
    print("   What claims would be inappropriate to make about this data?")
    print("4. Why does this tutorial only load 100 of the file's 32,448")
    print("   channels? What would happen if you asked for all of them?")


if __name__ == "__main__":
    main()