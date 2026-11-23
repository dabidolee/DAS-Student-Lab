"""Tutorial 06: how to read a spectrogram, and why one window is never enough.

Run from the repository root after installation (needs the science extras):

    python tutorials/06_read_a_spectrogram.py

Part 1 uses SIMULATED data, where we know exactly what is in the signal.
Part 2 uses MEASURED data from the OOI noise check recording used in Tutorial 04,
where we do not. Part 2 is skipped if that file cannot be loaded.
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import spectrogram

from das_student_lab import make_synthetic_whale
from das_student_lab.datasets import fetch_ooi_example
from das_student_lab.tdms_reader import read_tdms_subset

WINDOWS_S = [0.1, 0.5, 2.0]
MAX_FREQUENCY_HZ = 80.0


def average_spectrogram_db(data: np.ndarray, sample_rate_hz: float, window_s: float):
    """Spectrogram in decibels, averaged over channels if there are several."""

    nperseg = int(round(window_s * sample_rate_hz))
    noverlap = int(nperseg * 0.9)
    data = data - data.mean(axis=-1, keepdims=True)
    freqs, times, power = spectrogram(
        data, fs=sample_rate_hz, nperseg=nperseg, noverlap=noverlap, axis=-1
    )
    if power.ndim == 3:
        power = power.mean(axis=0)
    return freqs, times, 10 * np.log10(np.maximum(power, 1e-20))


def draw(ax, freqs: np.ndarray, times: np.ndarray, db: np.ndarray, title: str):
    """Draw one spectrogram, with colors set from the plotted band only."""

    keep = freqs <= MAX_FREQUENCY_HZ
    vmin, vmax = np.percentile(db[keep], [5, 99.5])
    mesh = ax.pcolormesh(
        times, freqs[keep], db[keep], shading="auto", cmap="magma", vmin=vmin, vmax=vmax
    )
    ax.set_title(title)
    ax.set_ylabel("Frequency (Hz)")
    return mesh


def load_real_subset():
    """Load 100 real channels, or return None if the file is unavailable."""

    try:
        path = fetch_ooi_example(confirm=True)
    except OSError as exc:
        print(f"Real data unavailable, so Part 2 is skipped. Reason: {exc}")
        return None
    return read_tdms_subset(path, first_channel=0, last_channel=99)


def main() -> None:
    print("Learning goal: read a spectrogram, and see why no single window length")
    print("shows both WHEN something happened and exactly WHICH frequency it had.\n")

    print(
        "Prediction: we will look at the same 8 second signal three times, using "
        "windows of 0.1 s, 0.5 s and 2 s. The signal holds a short 20 Hz pulse, a "
        "steady 26 Hz tone and one sharp click. Which window shows the click as the "
        "thinnest vertical line? Which separates the 20 Hz pulse from the 26 Hz tone "
        "most cleanly? Write your guesses down before continuing.\n"
    )

    example = make_synthetic_whale(seed=7, noise_std=0.2)
    fs = example.sample_rate_hz
    signal = example.data[48].copy()
    signal += 0.4 * np.sin(2 * np.pi * 26.0 * example.time_s)
    signal[int(6.0 * fs)] += 10.0
    print(example.description)
    print("The 20 Hz pulse comes from make_synthetic_whale. The 26 Hz tone and the click")
    print("were added by hand. All of it is SIMULATED, not measured.\n")

    print(f"{'Window (s)':<12}{'Samples':<10}{'Frequency resolution (Hz)':<28}")
    for window_s in WINDOWS_S:
        samples = int(round(window_s * fs))
        print(f"{window_s:<12g}{samples:<10}{fs / samples:<28.2f}")

    fig, axes = plt.subplots(len(WINDOWS_S), 1, figsize=(9, 9), sharex=True)
    for ax, window_s in zip(axes, WINDOWS_S, strict=True):
        freqs, times, db = average_spectrogram_db(signal, fs, window_s)
        mesh = draw(ax, freqs, times, db, f"{window_s:g} s window (SIMULATED)")
        fig.colorbar(mesh, ax=ax, label="dB")
    axes[-1].set_xlabel("Time (s)")
    fig.tight_layout()
    plt.show()

    print("\nReading guide: a horizontal band is a steady tone. A vertical stripe is a")
    print("brief broadband impulse. A short bright blob is a pulse at one frequency.\n")

    real = load_real_subset()
    if real is not None:
        print("Part 2: MEASURED data, 100 channels of a real instrument noise check,")
        print("averaged together. This is not a whale recording.")
        freqs, times, db = average_spectrogram_db(real.data, real.sample_rate_hz, 0.5)
        fig, ax = plt.subplots(figsize=(9, 4))
        mesh = draw(ax, freqs, times, db, "0.5 s window (MEASURED, noise check)")
        fig.colorbar(mesh, ax=ax, label="dB (raw instrument units)")
        ax.set_xlabel("Time (s)")
        fig.tight_layout()
        plt.show()

    print("\nSoftware: das_student_lab (this project), nptdms, NumPy, SciPy, Matplotlib")
    print("Real data citation, if Part 2 ran: see Tutorial 04 or the saved manifest.")

    print("\nQuestions to answer in your own words:")
    print("1. Which window made the click thinnest, and which window separated the")
    print("   20 Hz pulse from the 26 Hz tone best? Why can one window not do both?")
    print("2. The 20 Hz pulse lasts about a third of a second. What happens to its")
    print("   shape in the 2 s window, and why?")
    print("3. Compare Part 2 with the simulated plots. Where is most of the energy?")
    print("   What would you need to see before calling anything a whale?")
    print("4. Name one feature in the real spectrogram you cannot explain yet, and")
    print("   one way you could find out what it is.")


if __name__ == "__main__":
    main()