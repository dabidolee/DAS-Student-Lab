"""Tutorial 02: from a raw array to a visible signal.

Run from the repository root after installation:

    python tutorials/02_from_array_to_visible_signal.py

This tutorial uses scipy for bandpass filtering, an established signal-
processing library, rather than reimplementing filtering from scratch. It does
not use a DASCore or DAS4Whales adapter, since that adapter does not exist yet
in this project (see README.md, "What is deliberately not implemented").
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt

from das_student_lab import make_synthetic_whale


def bandpass_filter(
    data: np.ndarray,
    sample_rate_hz: float,
    low_hz: float,
    high_hz: float,
) -> np.ndarray:
    """Apply a zero-phase Butterworth bandpass filter to each channel.

    This is standard scipy usage, not a custom filter implementation.
    """

    nyquist = sample_rate_hz / 2
    b, a = butter(4, [low_hz / nyquist, high_hz / nyquist], btype="band")
    return filtfilt(b, a, data, axis=1)


def plot_waterfall(
    data: np.ndarray, time_s: np.ndarray, distance_m: np.ndarray, title: str
) -> None:
    """Plot a time-distance waterfall, the standard way to look at DAS data."""

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
    plt.colorbar(label="Amplitude (arbitrary units, simulated)")
    plt.tight_layout()
    plt.show()


def main() -> None:
    print("Learning goal: see how a bandpass filter choice changes what's visible ")
    print("in a DAS waterfall plot.\n")

    print(
        "Prediction: this synthetic signal's call is centered at 20 Hz. If we "
        "bandpass filter the noisy raw data to keep only 15-25 Hz, do you expect "
        "the V-shaped arrival to become MORE or LESS visible against the "
        "background noise? Write down your guess before continuing.\n"
    )

    example = make_synthetic_whale(seed=7, noise_std=0.4)
    print(example.description)
    print("(All data in this tutorial is SIMULATED, not measured.)\n")

    print("Showing the raw, unfiltered array first...")
    plot_waterfall(
        example.data,
        example.time_s,
        example.distance_m,
        title="Raw synthetic array (SIMULATED, unfiltered)",
    )

    narrow = bandpass_filter(
        example.data, example.sample_rate_hz, low_hz=15, high_hz=25
    )
    print("Now showing the same array after a 15-25 Hz bandpass filter...")
    plot_waterfall(
        narrow,
        example.time_s,
        example.distance_m,
        title="Same array, bandpass filtered 15-25 Hz (SIMULATED)",
    )

    wide = bandpass_filter(
        example.data, example.sample_rate_hz, low_hz=1, high_hz=90
    )
    print("For comparison, here is a much wider 1-90 Hz filter...")
    plot_waterfall(
        wide,
        example.time_s,
        example.distance_m,
        title="Same array, wide bandpass filtered 1-90 Hz (SIMULATED)",
    )
    print("\nSoftware: das_student_lab (this project), NumPy, SciPy, Matplotlib")
    print("Note: this tutorial uses only synthetic data, no external dataset citation applies.")
    print("\nQuestions to answer in your own words:")
    print("1. Was your prediction correct? Why does narrowing the filter around")
    print("   the call frequency change what you can see?")
    print("2. What would happen if you filtered to a band that excluded 20 Hz")
    print("   entirely, like 40-60 Hz? Try it by changing low_hz and high_hz.")
    print("3. This filtering used scipy, an established signal-processing")
    print("   library. Why is that preferable to writing a custom filter here?")
    print("4. Every plot in this tutorial is labeled SIMULATED. What would need")
    print("   to be true before you could apply this same code to real,")
    print("   measured OOI data and trust the result?")


if __name__ == "__main__":
    main()