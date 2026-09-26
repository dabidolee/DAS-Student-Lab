import numpy as np
import pytest

from das_student_lab.synthetic import make_synthetic_whale


def test_synthetic_shape_coordinates_and_labels() -> None:
    example = make_synthetic_whale(
        channels=32,
        duration_s=2.0,
        sample_rate_hz=100.0,
        channel_spacing_m=4.0,
    )

    assert example.data.shape == (32, 200)
    assert example.time_s.shape == (200,)
    assert example.distance_m.shape == (32,)
    assert example.time_s[1] - example.time_s[0] == pytest.approx(0.01)
    assert example.distance_m[-1] == pytest.approx(124.0)
    assert "Synthetic" in example.description
    assert "not measured" in example.description


def test_synthetic_is_deterministic_for_fixed_seed() -> None:
    first = make_synthetic_whale(seed=23)
    second = make_synthetic_whale(seed=23)

    np.testing.assert_array_equal(first.data, second.data)


def test_synthetic_changes_with_seed() -> None:
    first = make_synthetic_whale(seed=23)
    second = make_synthetic_whale(seed=24)

    assert not np.array_equal(first.data, second.data)


@pytest.mark.parametrize(
    ("keyword", "value"),
    [
        ("channels", 1),
        ("duration_s", 0),
        ("sample_rate_hz", -1),
        ("channel_spacing_m", 0),
        ("noise_std", -0.1),
    ],
)
def test_synthetic_rejects_invalid_inputs(keyword: str, value: float) -> None:
    with pytest.raises(ValueError):
        make_synthetic_whale(**{keyword: value})


def test_synthetic_rejects_frequency_above_nyquist() -> None:
    with pytest.raises(ValueError, match="Nyquist"):
        make_synthetic_whale(sample_rate_hz=100, call_frequency_hz=50)

def test_synthetic_rejects_non_integer_seed() -> None:
    with pytest.raises(TypeError, match="seed must be an integer"):
        make_synthetic_whale(seed=3.5)

