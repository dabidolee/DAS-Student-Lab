"""Small deterministic synthetic examples for teaching and unit tests.

The generator in this module is intentionally simplified. It is not a validated
model of DAS instrument response, cable coupling, or ocean acoustic propagation.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class SyntheticDAS:
    """A labeled synthetic channels-by-time array."""

    data: NDArray[np.float64]
    time_s: NDArray[np.float64]
    distance_m: NDArray[np.float64]
    sample_rate_hz: float
    channel_spacing_m: float
    description: str


def make_synthetic_whale(
    *,
    channels: int = 96,
    duration_s: float = 8.0,
    sample_rate_hz: float = 200.0,
    channel_spacing_m: float = 2.0,
    source_channel: float | None = None,
    call_frequency_hz: float = 20.0,
    propagation_speed_m_s: float = 1500.0,
    noise_std: float = 0.15,
    seed: int = 7,
) -> SyntheticDAS:
    """Create a small DAS-like array with a curved, whale-like narrowband arrival.

    This pedagogical signal uses a delayed Gaussian-windowed sinusoid. It omits
    instrument response, cable coupling, attenuation, dispersion, reflections,
    and realistic ocean noise. It must not be treated as measured or validated
    physical data.

    Returns
    -------
    SyntheticDAS
        Data have shape ``(channels, time samples)``. Time is in seconds and
        distance is in meters.
    """

    if channels < 2:
        raise ValueError("channels must be at least 2")
    if duration_s <= 0 or not np.isfinite(duration_s):
        raise ValueError("duration_s must be a positive finite number")
    if sample_rate_hz <= 0 or not np.isfinite(sample_rate_hz):
        raise ValueError("sample_rate_hz must be a positive finite number")
    if channel_spacing_m <= 0 or not np.isfinite(channel_spacing_m):
        raise ValueError("channel_spacing_m must be a positive finite number")
    if call_frequency_hz <= 0 or call_frequency_hz >= sample_rate_hz / 2:
        raise ValueError("call_frequency_hz must be between 0 and the Nyquist rate")
    if propagation_speed_m_s <= 0 or not np.isfinite(propagation_speed_m_s):
        raise ValueError("propagation_speed_m_s must be a positive finite number")
    if noise_std < 0 or not np.isfinite(noise_std):
        raise ValueError("noise_std must be a non-negative finite number")
    if not isinstance(seed, int):
        raise TypeError("seed must be an integer")

    samples = int(round(duration_s * sample_rate_hz))
    if samples < 2:
        raise ValueError(
            "duration_s and sample_rate_hz must produce at least 2 samples"
        )

    source = (channels - 1) / 2 if source_channel is None else float(source_channel)
    if source < 0 or source > channels - 1:
        raise ValueError("source_channel must fall within the channel range")

    rng = np.random.default_rng(seed)
    time_s = np.arange(samples, dtype=np.float64) / sample_rate_hz
    distance_m = np.arange(channels, dtype=np.float64) * channel_spacing_m
    data = rng.normal(0.0, noise_std, size=(channels, samples))

    source_distance_m = source * channel_spacing_m
    horizontal_offset_m = np.abs(distance_m - source_distance_m)
    arrival_delay_s = horizontal_offset_m / propagation_speed_m_s
    base_arrival_s = duration_s * 0.45
    envelope_width_s = min(0.12, duration_s / 10)

    for channel_index, delay_s in enumerate(arrival_delay_s):
        centered_time = time_s - (base_arrival_s + delay_s)
        envelope = np.exp(-0.5 * (centered_time / envelope_width_s) ** 2)
        carrier = np.sin(2 * np.pi * call_frequency_hz * centered_time)
        data[channel_index] += envelope * carrier

    return SyntheticDAS(
        data=data,
        time_s=time_s,
        distance_m=distance_m,
        sample_rate_hz=float(sample_rate_hz),
        channel_spacing_m=float(channel_spacing_m),
        description=(
            "Synthetic pedagogical narrowband arrival; not measured data and not a "
            "validated DAS or ocean-acoustic propagation model."
        ),
    )
