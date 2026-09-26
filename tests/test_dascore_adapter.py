import numpy as np
import pytest

from das_student_lab.dascore_adapter import to_dascore_patch


def test_to_dascore_patch_has_correct_dims_and_shape() -> None:
    data = np.zeros((10, 50))

    patch = to_dascore_patch(data, sample_rate_hz=100.0, channel_spacing_m=2.0)

    assert patch.dims == ("distance", "time")
    assert patch.shape == (10, 50)


def test_to_dascore_patch_distance_coord_uses_spacing() -> None:
    data = np.zeros((5, 20))

    patch = to_dascore_patch(data, sample_rate_hz=100.0, channel_spacing_m=3.0)

    distance = patch.coords.get_array("distance")
    assert distance[0] == pytest.approx(0.0)
    assert distance[-1] == pytest.approx(4 * 3.0)


def test_to_dascore_patch_uses_provided_start_time() -> None:
    data = np.zeros((5, 20))
    start = np.datetime64("2021-11-01T15:33:40.764174")

    patch = to_dascore_patch(
        data, sample_rate_hz=100.0, channel_spacing_m=2.0, start_time=start
    )

    time = patch.coords.get_array("time")
    assert time[0] == np.datetime64(start, "ns")


def test_to_dascore_patch_defaults_start_time_when_not_given() -> None:
    data = np.zeros((5, 20))

    patch = to_dascore_patch(data, sample_rate_hz=100.0, channel_spacing_m=2.0)

    time = patch.coords.get_array("time")
    assert time[0] == np.datetime64("2000-01-01T00:00:00", "ns")


def test_to_dascore_patch_rejects_non_2d_input() -> None:
    with pytest.raises(ValueError, match="2-dimensional"):
        to_dascore_patch(np.zeros(10), sample_rate_hz=100.0, channel_spacing_m=2.0)


def test_to_dascore_patch_is_actually_filterable() -> None:
    """The real point of this adapter: DASCore's own tools must work on it."""

    data = np.random.default_rng(0).normal(size=(5, 200))

    patch = to_dascore_patch(data, sample_rate_hz=200.0, channel_spacing_m=2.0)
    filtered = patch.pass_filter(time=(15, 25))

    assert filtered.data.shape == patch.data.shape