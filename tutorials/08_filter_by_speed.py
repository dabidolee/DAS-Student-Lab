"""Tutorial 08: frequency wavenumber filtering, separating signals by speed.

Run from the repository root after installation (needs the science extras):

    python tutorials/08_filter_by_speed.py

Everything here is SIMULATED. The slow noise is something we invented so that this
idea has a fair test. Real noise decides whether it works on real data.
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, sosfiltfilt

from das_student_lab import make_synthetic_whale
from das_student_lab.metrics import window_snr_db

CHANNELS = 512
SOUND_SPEED_M_S = 1500.0  # the generator's default propagation speed
NOISE_WINDOW_S = (0.8, 3.0)
SPEED_THRESHOLDS_M_S = [500.0, 1000.0]


def add_slow_noise(shape, spacing_m, time_s, seed, waves=25, amplitude=0.35):
    """Add slow travelling waves in the same frequency band as the call."""

    rng = np.random.default_rng(seed)
    x = np.arange(shape[0]) * spacing_m
    noise = np.zeros(shape)
    for _ in range(waves):
        frequency = rng.uniform(5.0, 30.0)
        # Keep wavenumber below the spatial Nyquist limit, or the wave aliases.
        speed = rng.uniform(4.5 * frequency, 400.0)
        direction = rng.choice([-1.0, 1.0])
        phase = rng.uniform(0.0, 2 * np.pi)
        delay = time_s[None, :] - direction * x[:, None] / speed
        noise += amplitude * np.sin(2 * np.pi * frequency * delay + phase)
    return noise


def bandpass(data, sample_rate_hz, low_hz, high_hz):
    sos = butter(4, [low_hz, high_hz], btype="band", fs=sample_rate_hz, output="sos")
    return sosfiltfilt(sos, data, axis=1)


def fk_speed_filter(data, sample_rate_hz, spacing_m, min_speed_m_s, sharpness=0.15):
    """Keep only signals whose apparent speed along the cable is at least min_speed_m_s.

    Apparent speed is frequency divided by wavenumber. A wave crossing the cable
    quickly sits near the frequency axis of the f-k plane, and a slow wave sits
    far out to the side. The mask is smooth so it does not ring.
    """

    channels, samples = data.shape
    wavenumber = np.fft.fftfreq(channels, d=spacing_m)[:, None]
    frequency = np.fft.fftfreq(samples, d=1.0 / sample_rate_hz)[None, :]
    speed = np.abs(frequency) / np.maximum(np.abs(wavenumber), 1e-12)
    ratio = np.log(np.maximum(speed, 1e-9) / min_speed_m_s)
    mask = 0.5 * (1 + np.tanh(ratio / sharpness))
    return np.real(np.fft.ifft2(np.fft.fft2(data) * mask))


def main() -> None:
    print("Learning goal: separate a signal from noise by how fast it travels along")
    print("the cable, when a frequency filter alone cannot.\n")

    print(
        "Prediction: a call is buried under slow travelling waves that sit in the "
        "same 15 to 25 Hz band. A bandpass filter at 15 to 25 Hz keeps both. A "
        "second filter keeps only signals that travel fast along the cable. How "
        "much will each improve the signal to noise ratio? Write down a number "
        "in dB for each before continuing.\n"
    )

    example = make_synthetic_whale(channels=CHANNELS, noise_std=0.3, seed=7)
    fs = example.sample_rate_hz
    spacing = example.channel_spacing_m
    time_s = example.time_s
    data = example.data + add_slow_noise(example.data.shape, spacing, time_s, seed=107)
    print(example.description)
    print("The call is from make_synthetic_whale. The slow waves were added by hand.")
    print("All of it is SIMULATED, not measured.\n")

    # Ground truth that only exists because the data is simulated: the call arrives
    # near 3.6 s at the middle of the array and later at the ends.
    max_delay = (CHANNELS / 2) * spacing / SOUND_SPEED_M_S
    signal_window = (3.3, 3.6 + max_delay + 0.35)

    fk_1000 = fk_speed_filter(data, fs, spacing, 1000.0)
    results = [
        ("unfiltered", data),
        ("bandpass 15-25 Hz", bandpass(data, fs, 15.0, 25.0)),
    ]
    for speed in SPEED_THRESHOLDS_M_S:
        label = f"f-k filter, speeds >= {speed:g} m/s"
        results.append((label, fk_speed_filter(data, fs, spacing, speed)))
    results.append(("f-k >= 1000 m/s, then bandpass", bandpass(fk_1000, fs, 15.0, 25.0)))

    def measure(array):
        return window_snr_db(
            array, time_s, signal_window_s=signal_window, noise_window_s=NOISE_WINDOW_S
        )

    raw_snr = measure(data)
    print(f"{'Method':<34}{'SNR (dB)':<12}{'Change vs raw (dB)'}")
    for label, array in results:
        snr = measure(array)
        print(f"{label:<34}{snr:<12.2f}{snr - raw_snr:+.2f}")

    spectrum = np.fft.fftshift(np.abs(np.fft.fft2(data)), axes=0)
    columns = int(60 * data.shape[1] / fs)
    freqs = np.fft.rfftfreq(data.shape[1], d=1.0 / fs)[:columns]
    wavenumbers = np.fft.fftshift(np.fft.fftfreq(CHANNELS, d=spacing))
    extent = [time_s[0], time_s[-1], CHANNELS * spacing, 0]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    limit = np.percentile(np.abs(data), 99)
    axes[0].imshow(data, aspect="auto", cmap="seismic", vmin=-limit, vmax=limit, extent=extent)
    axes[0].set_title("Raw: call plus slow noise (SIMULATED)")
    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("Distance along cable (m)")

    db = 20 * np.log10(spectrum[:, :columns].T + 1e-9)
    mesh = axes[1].pcolormesh(wavenumbers, freqs, db, shading="auto", cmap="magma")
    for sign in (1, -1):
        axes[1].plot([0, sign * 60 / 1000.0], [0, 60], "c--", linewidth=1)
    axes[1].set_xlim(-0.12, 0.12)
    axes[1].set_ylim(0, 60)
    axes[1].set_title("f-k spectrum, dashed = 1000 m/s (SIMULATED)")
    axes[1].set_xlabel("Wavenumber (cycles per meter)")
    axes[1].set_ylabel("Frequency (Hz)")
    fig.colorbar(mesh, ax=axes[1], label="dB")

    limit = np.percentile(np.abs(fk_1000), 99)
    axes[2].imshow(fk_1000, aspect="auto", cmap="seismic", vmin=-limit, vmax=limit, extent=extent)
    axes[2].set_title("After f-k filter, speeds >= 1000 m/s (SIMULATED)")
    axes[2].set_xlabel("Time (s)")
    fig.tight_layout()
    plt.show()

    print("\nWe could place the signal window only because this data is simulated.")
    print("The filter keeps every signal faster than the threshold, not just calls.")
    print("DASCore has a patch method called slope_filter for this idea, worth reading")
    print("about once you have seen how it works inside.")

    print("\nSoftware: das_student_lab (this project), NumPy, SciPy, Matplotlib")
    print("Data: simulated only, so no external dataset citation applies.")

    print("\nQuestions to answer in your own words:")
    print("1. The bandpass filter barely helped, and the speed filter helped a lot.")
    print("   Why can a frequency filter not remove noise that sits in the same band?")
    print("2. In the f-k plot, where does the call sit and where does the noise sit?")
    print("   What does the dashed line mean?")
    print("3. We invented slow noise. What would have to be true of real noise for")
    print("   this to work, and how could you check that on real data first?")
    print("4. The filter keeps anything faster than the threshold. Name one signal")
    print("   that is not a call that it would keep, and what that does to the number.")


if __name__ == "__main__":
    main()