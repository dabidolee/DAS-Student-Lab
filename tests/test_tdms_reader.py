from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from nptdms import ChannelObject, RootObject, TdmsWriter

from das_student_lab.tdms_reader import read_tdms_subset


def _write_fake_tdms(path: Path, *, num_channels: int = 5, samples_per_channel: int = 10) -> None:
    """Write a small, real TDMS file with the same structure and file-level
    properties this project's reader depends on: a "Measurement" group,
    numbered channels, and SamplingFrequency[Hz] / SpatialResolution[m].
    """

    root = RootObject(
        properties={
            "SamplingFrequency[Hz]": 100.0,
            "SpatialResolution[m]": 1.5,
        }
    )
    channels = [
        ChannelObject(
            "Measurement",
            str(i),
            np.arange(samples_per_channel, dtype=np.float64) + i,
        )
        for i in range(num_channels)
    ]
    with TdmsWriter(str(path)) as writer:
        writer.write_segment([root] + channels)


@pytest.fixture
def fake_tdms_file(tmp_path: Path) -> Path:
    path = tmp_path / "fake_example.tdms"
    _write_fake_tdms(path)
    return path


def test_read_tdms_subset_returns_correct_shape_and_metadata(
    fake_tdms_file: Path,
) -> None:
    subset = read_tdms_subset(fake_tdms_file, first_channel=0, last_channel=2)

    assert subset.data.shape == (3, 10)
    assert subset.sample_rate_hz == pytest.approx(100.0)
    assert subset.channel_spacing_m == pytest.approx(1.5)
    assert subset.first_channel == 0
    assert subset.last_channel == 2
    assert subset.data[1, 0] == pytest.approx(1.0)


def test_read_tdms_subset_rejects_negative_first_channel(
    fake_tdms_file: Path,
) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        read_tdms_subset(fake_tdms_file, first_channel=-1, last_channel=2)


def test_read_tdms_subset_rejects_last_before_first(fake_tdms_file: Path) -> None:
    with pytest.raises(ValueError, match="last_channel"):
        read_tdms_subset(fake_tdms_file, first_channel=3, last_channel=1)


def test_read_tdms_subset_rejects_out_of_range_channel(
    fake_tdms_file: Path,
) -> None:
    with pytest.raises(ValueError, match="out of range"):
        read_tdms_subset(fake_tdms_file, first_channel=0, last_channel=99)


def test_read_tdms_subset_rejects_size_over_limit(fake_tdms_file: Path) -> None:
    with patch("das_student_lab.tdms_reader._MAX_BYTES", 10):
        with pytest.raises(ValueError, match="exceeds"):
            read_tdms_subset(fake_tdms_file, first_channel=0, last_channel=4)