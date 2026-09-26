import numpy as np
import pytest

from das_student_lab.diagnostics import format_summary, summarize_array


def test_summary_calculates_explicit_geometry() -> None:
    data = np.arange(60, dtype=np.float64).reshape(3, 20)

    summary = summarize_array(data, sample_rate_hz=10, channel_spacing_m=2.5)

    assert summary.channels == 3
    assert summary.samples == 20
    assert summary.duration_s == pytest.approx(2.0)
    assert summary.distance_span_m == pytest.approx(5.0)
    assert summary.memory_bytes == data.nbytes
    assert summary.minimum == pytest.approx(0)
    assert summary.maximum == pytest.approx(59)


def test_summary_counts_invalid_values_without_hiding_them() -> None:
    data = np.array([[1.0, np.nan], [np.inf, -2.0]])

    summary = summarize_array(data, sample_rate_hz=2, channel_spacing_m=1)

    assert summary.nan_count == 1
    assert summary.infinite_count == 1
    assert summary.minimum == pytest.approx(-2)
    assert summary.maximum == pytest.approx(1)


def test_summary_handles_no_finite_values() -> None:
    summary = summarize_array(
        np.array([[np.nan, np.inf]]), sample_rate_hz=2, channel_spacing_m=1
    )

    assert summary.minimum is None
    assert summary.maximum is None
    assert "no finite values" in format_summary(summary)


@pytest.mark.parametrize("shape", [(5,), (1, 2, 3)])
def test_summary_rejects_non_2d_input(shape: tuple[int, ...]) -> None:
    with pytest.raises(ValueError, match="two-dimensional"):
        summarize_array(np.zeros(shape), sample_rate_hz=1, channel_spacing_m=1)


@pytest.mark.parametrize(
    ("sample_rate_hz", "channel_spacing_m"),
    [(0, 1), (-1, 1), (1, 0), (1, -1), (np.nan, 1), (1, np.inf)],
)
def test_summary_rejects_invalid_declared_units(
    sample_rate_hz: float, channel_spacing_m: float
) -> None:
    with pytest.raises(ValueError):
        summarize_array(
            np.zeros((2, 2)),
            sample_rate_hz=sample_rate_hz,
            channel_spacing_m=channel_spacing_m,
        )


def test_format_summary_names_caller_declared_units() -> None:
    summary = summarize_array(
        np.zeros((2, 20)), sample_rate_hz=10, channel_spacing_m=3
    )

    text = format_summary(summary)

    assert "caller-declared units" in text
    assert "2 channels x 20 time samples" in text
    assert "Distance span: 3.000 m" in text

def test_summary_calculates_mean_and_standard_deviation() -> None:
    data = np.array([[1.0, 2.0, 3.0, 4.0]])

    summary = summarize_array(data, sample_rate_hz=10, channel_spacing_m=1)

    assert summary.mean == pytest.approx(2.5)
    assert summary.standard_deviation == pytest.approx(np.std(data))


def test_summary_reports_dtype() -> None:
    data = np.zeros((2, 20), dtype=np.float32)

    summary = summarize_array(data, sample_rate_hz=10, channel_spacing_m=1)

    assert summary.dtype == "float32"


def test_summary_calculates_frequency_resolution() -> None:
    data = np.zeros((2, 100))

    summary = summarize_array(data, sample_rate_hz=100, channel_spacing_m=1)

    assert summary.frequency_resolution_hz == pytest.approx(1.0)


def test_summary_rejects_arrays_over_size_limit() -> None:
    large = np.zeros((2000, 70000), dtype=np.float64)

    with pytest.raises(ValueError, match="MiB"):
        summarize_array(large, sample_rate_hz=10, channel_spacing_m=1)


def test_format_summary_shows_new_fields() -> None:
    summary = summarize_array(
        np.array([[1.0, 2.0, 3.0]]), sample_rate_hz=10, channel_spacing_m=1
    )

    text = format_summary(summary)

    assert "Mean" in text
    assert "Data type" in text
    assert "Frequency resolution" in text
