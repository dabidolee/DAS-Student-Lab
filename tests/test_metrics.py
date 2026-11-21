import numpy as np
import pytest

from das_student_lab.metrics import window_snr_db

TIME_S = np.arange(100) / 100


def _two_level_data(signal_amplitude: float, noise_amplitude: float = 1.0) -> np.ndarray:
    data = np.full((2, 100), noise_amplitude)
    data[:, (TIME_S >= 0.5) & (TIME_S <= 0.9)] = signal_amplitude
    return data


def _snr(data: np.ndarray) -> float:
    return window_snr_db(
        data, TIME_S, signal_window_s=(0.5, 0.9), noise_window_s=(0.0, 0.4)
    )


def test_double_amplitude_is_about_six_decibels() -> None:
    assert _snr(_two_level_data(2.0)) == pytest.approx(10 * np.log10(4))


def test_equal_power_is_zero_decibels() -> None:
    assert _snr(_two_level_data(1.0)) == pytest.approx(0.0)


def test_result_does_not_depend_on_overall_scale() -> None:
    data = _two_level_data(2.0)
    assert _snr(data * 10) == pytest.approx(_snr(data))


def test_zero_signal_power_returns_negative_infinity() -> None:
    assert _snr(_two_level_data(0.0)) == float("-inf")


def test_rejects_non_2d_data() -> None:
    with pytest.raises(ValueError, match="2-dimensional"):
        _snr(np.zeros(100))


def test_rejects_time_axis_of_wrong_length() -> None:
    with pytest.raises(ValueError, match="one value per time sample"):
        window_snr_db(
            np.ones((2, 100)),
            TIME_S[:50],
            signal_window_s=(0.5, 0.9),
            noise_window_s=(0.0, 0.4),
        )


def test_rejects_reversed_window() -> None:
    with pytest.raises(ValueError, match="start < end"):
        window_snr_db(
            np.ones((2, 100)),
            TIME_S,
            signal_window_s=(0.9, 0.5),
            noise_window_s=(0.0, 0.4),
        )


def test_rejects_overlapping_windows() -> None:
    with pytest.raises(ValueError, match="overlap"):
        window_snr_db(
            np.ones((2, 100)),
            TIME_S,
            signal_window_s=(0.3, 0.9),
            noise_window_s=(0.0, 0.4),
        )


def test_rejects_window_outside_the_recording() -> None:
    with pytest.raises(ValueError, match="contains no samples"):
        window_snr_db(
            np.ones((2, 100)),
            TIME_S,
            signal_window_s=(5.0, 6.0),
            noise_window_s=(0.0, 0.4),
        )


def test_rejects_nan_in_a_window() -> None:
    data = _two_level_data(2.0)
    data[0, 60] = np.nan
    with pytest.raises(ValueError, match="NaN"):
        _snr(data)


def test_rejects_zero_power_noise_window() -> None:
    with pytest.raises(ValueError, match="zero power"):
        _snr(_two_level_data(2.0, noise_amplitude=0.0))