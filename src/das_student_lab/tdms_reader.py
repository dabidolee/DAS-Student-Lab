"""Read a bounded subset of a downloaded Silixa TDMS file into a numpy array.

The full OOI example file has 32,448 spatial channels. Loading all of them as
float64 would use roughly 780 MiB, well over this project's 500 MiB safety
limit (see diagnostics.py). This module therefore only ever loads an explicit,
bounded range of channels, never the whole file.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from nptdms import TdmsFile

_MAX_BYTES = 500 * 1024 * 1024
@dataclass(frozen=True, slots=True)
class TdmsSubset:
    """A bounded, real slice of a downloaded TDMS file.

    Parameters
    ----------
    data:
        Array of shape (channels, time samples), one row per spatial channel.
    sample_rate_hz:
        Read directly from the file's own SamplingFrequency[Hz] property.
    channel_spacing_m:
        Read directly from the file's own SpatialResolution[m] property.
    first_channel:
        Index of the first spatial channel included in this subset.
    last_channel:
        Index of the last spatial channel included in this subset (inclusive).
    source_path:
        Path to the original TDMS file this subset was read from.
    """

    data: np.ndarray
    sample_rate_hz: float
    channel_spacing_m: float
    first_channel: int
    last_channel: int
    source_path: str


def read_tdms_subset(
    path: str | Path,
    *,
    first_channel: int = 0,
    last_channel: int = 99,
) -> TdmsSubset:
    """Read a bounded range of spatial channels from a Silixa TDMS file.

    Parameters
    ----------
    path:
        Path to a .tdms file, such as one downloaded by
        :func:`das_student_lab.datasets.fetch_ooi_example`.
    first_channel:
        Index of the first spatial channel to read (inclusive).
    last_channel:
        Index of the last spatial channel to read (inclusive). Kept small by
        default (100 channels) to stay well under the 500 MiB safety limit.

    Returns
    -------
    TdmsSubset
        The requested channels as a real (channels, time samples) array,
        along with the sample rate and channel spacing read from the file's
        own metadata.

    Raises
    ------
    ValueError
        If the channel range is invalid, or would produce an array larger
        than the 500 MiB safety limit used elsewhere in this project.
    """

    if first_channel < 0:
        raise ValueError("first_channel must be non-negative")
    if last_channel < first_channel:
        raise ValueError("last_channel must be >= first_channel")

    requested_channels = last_channel - first_channel + 1

    path = Path(path)

    with TdmsFile.open(path) as tdms_file:
        sample_rate_hz = float(tdms_file.properties["SamplingFrequency[Hz]"])
        channel_spacing_m = float(tdms_file.properties["SpatialResolution[m]"])

        group = tdms_file["Measurement"]
        available_channels = len(group.channels())
        if last_channel >= available_channels:
            raise ValueError(
                f"last_channel={last_channel} is out of range; this file has "
                f"{available_channels} channels (0 to {available_channels - 1})"
            )

        # Peek at one channel's length to estimate size before reading, same
        # "check before you load" principle as fetch_ooi_example's size check.
        first_length = len(group[str(first_channel)])
        estimated_bytes = requested_channels * first_length * 8  # float64
        if estimated_bytes > _MAX_BYTES:
            raise ValueError(
                f"Requested {requested_channels} channels would use approximately "
                f"{estimated_bytes / (1024**2):.1f} MiB, which exceeds the "
                f"{_MAX_BYTES / (1024**2):.0f} MiB limit; request fewer channels"
            )

        rows = []
        for channel_index in range(first_channel, last_channel + 1):
            channel = group[str(channel_index)]
            rows.append(channel[:].astype(np.float64))

    data = np.stack(rows)

    return TdmsSubset(
        data=data,
        sample_rate_hz=sample_rate_hz,
        channel_spacing_m=channel_spacing_m,
        first_channel=first_channel,
        last_channel=last_channel,
        source_path=str(path),
    )