"""Plain-language diagnostics for small two-dimensional arrays."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike


@dataclass(frozen=True, slots=True)
class ArraySummary:
    """Summary of a channels-by-time numeric array.

    All values describe the array provided to :func:`summarize_array`. The
    function does not infer physical units or verify instrument calibration.
    """

    channels: int
    samples: int
    sample_rate_hz: float
    channel_spacing_m: float
    duration_s: float
    distance_span_m: float
    memory_bytes: int
    nan_count: int
    infinite_count: int
    minimum: float | None
    maximum: float | None
    mean: float | None 
    standard_deviation: float | None 
    dtype: str 
    frequency_resolution_hz: float


def summarize_array(
    data: ArrayLike,
    *,
    sample_rate_hz: float,
    channel_spacing_m: float,
) -> ArraySummary:
    """Summarize a numeric array interpreted as ``(channels, time samples)``.

    Parameters
    ----------
    data:
        Two-dimensional numeric data with channels on axis 0 and time on axis 1.
    sample_rate_hz:
        Time samples per second. Must be positive.
    channel_spacing_m:
        Physical spacing between adjacent channels in meters. Must be positive.

    Returns
    -------
    ArraySummary
        Explicit size, sampling, spatial-span, memory, and invalid-value fields.

    Notes
    -----
    This function trusts the caller's axis order and units. A future metadata-
    aware adapter should validate those properties from a supported DAS object.
    """

    array = np.asarray(data)
    if array.ndim != 2:
        raise ValueError(
            "data must be a two-dimensional array ordered as (channels, time samples)"
        )
    if not np.issubdtype(array.dtype, np.number):
        raise TypeError(
            f"data must contain numeric values, got dtype {array.dtype}; "
            "convert your array with something like array.astype(float) first"
        )
    if array.shape[0] == 0 or array.shape[1] == 0:
        raise ValueError(
            f"data has shape {array.shape}, but summarize_array needs at least "
            "one channel and one time sample; check that you loaded the full array"
        )
    if not np.isfinite(sample_rate_hz) or sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be a positive finite number")
    max_bytes = 500 * 1024 * 1024
    if array.nbytes > max_bytes:
        raise ValueError(
            f"data is {array.nbytes / (1024**2):.1f} MiB, which exceeds the "
            f"{max_bytes / (1024**2):.0f} MiB limit for this diagnostic; use a "
            "smaller subset of the array"

          )

    if not np.isfinite(channel_spacing_m) or channel_spacing_m <= 0:
        raise ValueError("channel_spacing_m must be a positive finite number")

    finite = np.isfinite(array)
    finite_values = array[finite]
    minimum = float(np.min(finite_values)) if finite_values.size else None
    maximum = float(np.max(finite_values)) if finite_values.size else None
    mean = float(np.mean(finite_values)) if finite_values.size else None 
    standard_deviation = float(np.std(finite_values)) if finite_values.size else None

    channels, samples = array.shape
    frequency_resolution_hz = float(sample_rate_hz) / samples
    return ArraySummary(
        channels=channels,
        samples=samples,
        sample_rate_hz=float(sample_rate_hz),
        channel_spacing_m=float(channel_spacing_m),
        duration_s=samples / float(sample_rate_hz),
        distance_span_m=max(channels - 1, 0) * float(channel_spacing_m),
        memory_bytes=array.nbytes,
        nan_count=int(np.isnan(array).sum()),
        infinite_count=int(np.isinf(array).sum()),
        minimum=minimum,
        maximum=maximum,
        mean=mean,
        standard_deviation=standard_deviation,
        dtype=str(array.dtype),
        frequency_resolution_hz=frequency_resolution_hz,
    )


def format_summary(summary: ArraySummary) -> str:
    """Format :class:`ArraySummary` as a compact beginner-facing report."""

    memory_mib = summary.memory_bytes / (1024**2)
    min_text = (
        "no finite values" if summary.minimum is None else f"{summary.minimum:.4g}"
    )
    max_text = (
        "no finite values" if summary.maximum is None else f"{summary.maximum:.4g}"
    )
    mean_text = (
        "no finite values" if summary.mean is None else f"{summary.mean:.4g}"
    )
    std_text = (
        "no finite values"
        if summary.standard_deviation is None
        else f"{summary.standard_deviation:.4g}"
    )
    return "\n".join(
        [
            "DAS array summary (caller-declared units)",
            f"  Shape: {summary.channels} channels x {summary.samples} time samples",
            f"  Sampling rate: {summary.sample_rate_hz:g} Hz",
            f"  Duration: {summary.duration_s:.3f} s",
            f"  Channel spacing: {summary.channel_spacing_m:g} m",
            f"  Distance span: {summary.distance_span_m:.3f} m",
            f"  Array memory: {memory_mib:.3f} MiB",
            f"  NaN / infinite values: {summary.nan_count} / {summary.infinite_count}",
            f"  Finite minimum / maximum: {min_text} / {max_text}",
            f"  Mean / standard deviation: {mean_text} / {std_text}",
            f"  Data type: {summary.dtype}",
            f"  Frequency resolution: {summary.frequency_resolution_hz:.4g} Hz "
            f"(sample_rate_hz / number of time samples; the smallest frequency "
            f"difference this array can distinguish)",
        ]
    )