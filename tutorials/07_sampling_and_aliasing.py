"""Tutorial 07: sampling, aliasing, and what decimation can and cannot undo.

Run from the repository root after installation (needs the science extras):

    python tutorials/07_sampling_and_aliasing.py

Everything here is SIMULATED, so it works offline. We know the true frequencies
because we built the signals ourselves.
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import decimate

CALL_HZ = 20.0
DURATION_S = 4.0
REFERENCE_RATE_HZ = 2000.0
SAMPLE_RATES_HZ = [200, 50, 25]


def peak_frequency_hz(signal: np.ndarray, sample_rate_hz: float) -> float:
    """Frequency of the strongest component, found with a windowed FFT."""

    spectrum = np.abs(np.fft.rfft(signal * np.hanning(len(signal))))
    freqs = np.fft.rfftfreq(len(signal), d=1.0 / sample_rate_hz)
    return float(freqs[np.argmax(spectrum)])


def amplitude_at(signal: np.ndarray, sample_rate_hz: float, frequency_hz: float) -> float:
    """Amplitude of a sine at one frequency. Exact when it fits the recording evenly."""

    spectrum = 2 * np.abs(np.fft.rfft(signal)) / len(signal)
    index = int(round(frequency_hz * len(signal) / sample_rate_hz))
    return float(spectrum[index])


def main() -> None:
    print("Learning goal: see what happens when a recording is too slow for the")
    print("signal in it, and why the damage cannot be repaired afterwards.\n")

    print(
        f"Prediction: a clean {CALL_HZ:g} Hz sine is recorded at 200 Hz, 50 Hz and "
        "25 Hz. For each, predict the frequency you will measure from the "
        "recording. One of them will be wrong. Which one, and what will it say "
        "instead? Write your guesses down before continuing.\n"
    )

    t_ref = np.arange(int(DURATION_S * REFERENCE_RATE_HZ)) / REFERENCE_RATE_HZ
    reference = np.sin(2 * np.pi * CALL_HZ * t_ref)
    print("(All data in this tutorial is SIMULATED, not measured.)\n")

    print(f"{'Rate (Hz)':<11}{'Nyquist':<10}{'Samples/cycle':<15}{'Measured peak (Hz)':<20}Verdict")
    sampled = {}
    for rate in SAMPLE_RATES_HZ:
        step = int(REFERENCE_RATE_HZ // rate)
        samples = reference[::step]
        sampled[rate] = samples
        peak = peak_frequency_hz(samples, rate)
        ok = abs(peak - CALL_HZ) < 0.5
        verdict = "correct" if ok else f"ALIAS (true frequency is {CALL_HZ:g} Hz)"
        print(f"{rate:<11}{rate / 2:<10g}{rate / CALL_HZ:<15.2f}{peak:<20.2f}{verdict}")

    fig, axes = plt.subplots(len(SAMPLE_RATES_HZ), 1, figsize=(9, 8), sharex=True)
    window = t_ref < 0.5
    for ax, rate in zip(axes, SAMPLE_RATES_HZ, strict=True):
        samples = sampled[rate]
        t = np.arange(len(samples)) / rate
        ax.plot(t_ref[window], reference[window], color="lightgray", label="true signal")
        ax.plot(t[t < 0.5], samples[t < 0.5], "o-", label=f"sampled at {rate} Hz")
        ax.set_ylabel("Amplitude")
        ax.set_title(f"{rate} Hz sampling, Nyquist {rate / 2:g} Hz (SIMULATED)")
        ax.legend(loc="upper right")
    axes[-1].set_xlabel("Time (s)")
    fig.tight_layout()
    plt.show()

    print("\nPart 2: decimation. A 200 Hz recording holds a 20 Hz call and a 70 Hz tone.")
    print("We keep every second sample, which gives 100 Hz and a Nyquist limit of 50 Hz.\n")

    fs = 200.0
    t = np.arange(int(DURATION_S * fs)) / fs
    recording = np.sin(2 * np.pi * 20.0 * t) + 0.5 * np.sin(2 * np.pi * 70.0 * t)
    naive = recording[::2]
    filtered = decimate(recording, 2)

    print(f"{'Method':<32}{'Amplitude at 20 Hz':<22}{'Amplitude at 30 Hz'}")
    methods = [
        ("keep every 2nd sample", naive),
        ("scipy decimate (filters first)", filtered),
    ]
    for label, result in methods:
        print(
            f"{label:<32}{amplitude_at(result, 100.0, 20.0):<22.3f}"
            f"{amplitude_at(result, 100.0, 30.0):.3f}"
        )
    print("\nThe 70 Hz tone folds down to |70 - 100| = 30 Hz when samples are simply dropped.")
    print("decimate removes everything above the new Nyquist limit before dropping samples.")

    print("\nIn the real file used in Tutorial 04, the instrument metadata records a")
    print("1000 Hz sampling frequency and a time decimation factor of 5, which gives the")
    print("200 Hz data you have been using.")

    print("\nSoftware: NumPy, SciPy, Matplotlib. No external dataset was used.")

    print("\nQuestions to answer in your own words:")
    print("1. At 25 Hz the 20 Hz sine looks like a clean 5 Hz sine. Why can you not")
    print("   tell from the 25 Hz data alone that it is wrong?")
    print("2. Change SAMPLE_RATES_HZ to include 40, so Nyquist is exactly 20 Hz.")
    print("   What do you get, and why is that case especially treacherous?")
    print("3. Why did the 70 Hz tone appear at 30 Hz, and what does decimate do")
    print("   before it drops samples that keeping every 2nd sample does not?")
    print("4. The real instrument keeps every 5th sample of a 1000 Hz stream. What")
    print("   can nobody ever learn about frequencies above 100 Hz from the 200 Hz")
    print("   data, and what must the instrument have done first?")


if __name__ == "__main__":
    main()