"""Convert this project's own data structures into DASCore Patch objects.

DASCore's Patch is the standard object its own processing tools (filtering,
spectral analysis, and more) expect. This adapter is intentionally thin: it
only reshapes and relabels data that already exists, it does not reimplement
any DASCore functionality (see docs/architecture.md, design principle).
"""

import numpy as np

try:
    import dascore as dc
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "dascore is required for this adapter. Install it with: "
        "pip install -e '.[science]'"
    ) from exc


def to_dascore_patch(
    data: np.ndarray,
    *,
    sample_rate_hz: float,
    channel_spacing_m: float,
    start_time: np.datetime64 | None = None,
):
    """Wrap a (channels, time samples) array as a DASCore Patch.

    Parameters
    ----------
    data:
        Array of shape (channels, time samples), the same layout used
        throughout this project (see synthetic.py, tdms_reader.py).
    sample_rate_hz:
        Time samples per second.
    channel_spacing_m:
        Physical spacing between adjacent channels, in meters.
    start_time:
        The real or assumed timestamp of the first sample. DASCore's time
        coordinate requires actual calendar timestamps, not elapsed seconds.
        Pass the file's real recording start time for real data (for example,
        from a TDMS file's GPSTimeStamp property). If not given, an arbitrary
        fixed reference time is used, which is fine for synthetic data but
        must not be treated as a real timestamp.

    Returns
    -------
    dascore.Patch
        A Patch with dims ("distance", "time"), ready to use with DASCore's
        own processing methods, such as patch.pass_filter(time=(low, high)).
    """

    if data.ndim != 2:
        raise ValueError(
            f"data must be 2-dimensional (channels, time samples), got shape {data.shape}"
        )

    channels, samples = data.shape

    if start_time is None:
        start_time = np.datetime64("2000-01-01T00:00:00")

    distance = np.arange(channels, dtype=np.float64) * channel_spacing_m
    time_offsets_ns = (np.arange(samples, dtype=np.float64) / sample_rate_hz * 1e9).astype(
        "timedelta64[ns]"
    )
    time = np.datetime64(start_time, "ns") + time_offsets_ns

    return dc.Patch(
        data=data,
        coords={"distance": distance, "time": time},
        dims=("distance", "time"),
    )