"""Tutorial 05: measure what a filter does instead of judging it by eye.

Run from the repository root after installation (needs the science extras):

    python tutorials/05_measure_dont_eyeball.py

Everything here is SIMULATED. We can measure signal to noise only because we
made the data ourselves and know when the call arrives.
"""

import matplotlib.pyplot as plt

from das_student_lab import make_synthetic_whale
from das_student_lab.dascore_adapter import to_dascore_patch
from das_student_lab.metrics import window_snr_db

# Ground truth from the generator: the call arrives near 45 percent of the
# recording (3.6 s of 8 s). Real data does not come with this knowledge.
SIGNAL_WINDOW_S = (3.3, 3.95)
NOISE_WINDOW_S = (1.0, 3.0)

CENTERED_BANDS_HZ = [
    (19.5, 20.5),
    (19, 21),
    (18, 22),
    (15, 25),
    (10, 30),
    (5, 35),
    (1, 39),
]
CONTROL_BAND_HZ = (40, 60)


def main() -> None:
    print("Learning goal: replace 'this looks cleaner' with a measured number,")
    print("and learn where that number stops being trustworthy.\n")

    print(
        "Prediction: the call is centered at 20 Hz. As we narrow the passband "
        "around 20 Hz, from very wide down to about 1 Hz wide, will the "
        "measured signal to noise ratio keep rising, level off, or fall at "
        "some point? Sketch the curve you expect before continuing.\n"
    )

    example = make_synthetic_whale(seed=7, noise_std=0.4)
    print(example.description)
    print("(All data in this tutorial is SIMULATED, not measured.)\n")

    print(
        "The metric: average power in a signal window "
        f"{SIGNAL_WINDOW_S} s divided by average power in a noise window "
        f"{NOISE_WINDOW_S} s, in decibels. The signal window still contains "
        "noise, so this is a window power ratio, not a perfect separation.\n"
    )

    patch = to_dascore_patch(
        example.data,
        sample_rate_hz=example.sample_rate_hz,
        channel_spacing_m=example.channel_spacing_m,
    )

    def measure(array) -> float:
        return window_snr_db(
            array,
            example.time_s,
            signal_window_s=SIGNAL_WINDOW_S,
            noise_window_s=NOISE_WINDOW_S,
        )

    raw_snr = measure(example.data)
    print(f"{'Band (Hz)':<14}{'Width (Hz)':<12}{'SNR (dB)':<12}{'Change vs raw (dB)'}")
    print(f"{'unfiltered':<14}{'-':<12}{raw_snr:<12.2f}{'-'}")

    widths = []
    snrs = []
    for low, high in CENTERED_BANDS_HZ:
        snr = measure(patch.pass_filter(time=(low, high)).data)
        widths.append(high - low)
        snrs.append(snr)
        label = f"{low:g}-{high:g}"
        print(f"{label:<14}{high - low:<12g}{snr:<12.2f}{snr - raw_snr:+.2f}")

    control_snr = measure(patch.pass_filter(time=CONTROL_BAND_HZ).data)
    low, high = CONTROL_BAND_HZ
    label = f"{low:g}-{high:g}"
    print(f"{label:<14}{'(control)':<12}{control_snr:<12.2f}{control_snr - raw_snr:+.2f}")

    plt.figure(figsize=(7, 4.5))
    plt.plot(widths, snrs, marker="o", label="bandpass centered on 20 Hz")
    plt.axhline(raw_snr, linestyle="--", color="gray", label="unfiltered")
    plt.xscale("log")
    plt.xlabel("Passband width (Hz)")
    plt.ylabel("Window SNR (dB, SIMULATED data)")
    plt.title("Measured effect of filter width")
    plt.legend()
    plt.tight_layout()
    plt.show()

    print("\nSoftware: das_student_lab (this project), DASCore, NumPy, Matplotlib")
    print("Data: simulated only, so no external dataset citation applies.")

    print("\nQuestions to answer in your own words:")
    print("1. Compare your sketch to the plot. Where is the peak? Why can the")
    print("   number fall again when the band gets narrower than the call?")
    print("   (Hint: a short pulse is spread over a range of frequencies.)")
    print("2. The 40-60 Hz control band is far from the call. What does its")
    print("   result tell you, and why is a control like this useful?")
    print("3. We placed the windows using knowledge that only exists because")
    print("   the data is simulated. What goes wrong if you choose windows")
    print("   after looking at the filtered result?")
    print("4. This used one noise seed. Change seed=7 and rerun. Is the pattern")
    print("   a property of filtering, or a fluke of one random draw?")


if __name__ == "__main__":
    main()