"""Simple, explicit signal quality measurements for (channels, time samples) arrays."""

import numpy as np


def window_snr_db(
    data: np.ndarray,
    time_s: np.ndarray,
    *,
    signal_window_s: tuple[float, float],
    noise_window_s: tuple[float, float],
) -> float:
    """Ratio of average power in a signal window to a noise window, in decibels.

    Both windows are measured on the same array. The signal window still
    contains noise, so this is a window power ratio, not a clean separation of
    signal from noise. It is only meaningful when you have independent evidence
    of when the signal arrives, such as synthetic ground truth.

    Parameters
    ----------
    data:
        Array of shape (channels, time samples).
    time_s:
        Time in seconds of each sample, one value per column of ``data``.
    signal_window_s:
        (start, end) in seconds of the window expected to contain the signal.
    noise_window_s:
        (start, end) in seconds of a window expected to contain only noise.

    Returns
    -------
    float
        10 * log10(mean power in signal window / mean power in noise window).
        Returns negative infinity if the signal window has exactly zero power.

    Raises
    ------
    ValueError
        If the shapes disagree, a window is reversed, empty, or overlaps the
        other window, a window contains NaN or infinite values, or the noise
        window has zero power.
    """

    data = np.asarray(data)
    time_s = np.asarray(time_s)
    if data.ndim != 2:
        raise ValueError(
            f"data must be 2-dimensional (channels, time samples), got shape {data.shape}"
        )
    if time_s.ndim != 1 or time_s.shape[0] != data.shape[1]:
        raise ValueError(
            f"time_s must have one value per time sample ({data.shape[1]}), "
            f"got shape {time_s.shape}"
        )

    for label, (start, end) in (
        ("signal_window_s", signal_window_s),
        ("noise_window_s", noise_window_s),
    ):
        if not start < end:
            raise ValueError(f"{label} must have start < end, got ({start}, {end})")

    if max(signal_window_s[0], noise_window_s[0]) <= min(
        signal_window_s[1], noise_window_s[1]
    ):
        raise ValueError(
            "signal_window_s and noise_window_s overlap; the measurement would "
            "compare the data with itself"
        )

    def window_power(label: str, window: tuple[float, float]) -> float:
        mask = (time_s >= window[0]) & (time_s <= window[1])
        if not mask.any():
            raise ValueError(
                f"{label} {window} contains no samples; the recording spans "
                f"{time_s[0]:g} to {time_s[-1]:g} s"
            )
        values = data[:, mask]
        if not np.all(np.isfinite(values)):
            raise ValueError(f"{label} contains NaN or infinite values")
        return float(np.mean(values.astype(np.float64) ** 2))

    signal_power = window_power("signal_window_s", signal_window_s)
    noise_power = window_power("noise_window_s", noise_window_s)

    if noise_power == 0:
        raise ValueError("noise window has zero power, so the ratio is undefined")
    if signal_power == 0:
        return float("-inf")
    return float(10 * np.log10(signal_power / noise_power))