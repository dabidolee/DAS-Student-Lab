from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from das_student_lab.datasets import OOI_DATASET, fetch_ooi_example


def test_ooi_citation_has_persistent_identifier() -> None:
    assert OOI_DATASET.year == 2023
    assert OOI_DATASET.doi == "https://doi.org/10.58046/5J60-FJ89"
    assert OOI_DATASET.doi in OOI_DATASET.citation
    assert "Ocean Observatories Initiative" in OOI_DATASET.citation


def test_fetch_rejects_unknown_example() -> None:
    with pytest.raises(KeyError, match="Unknown example"):
        fetch_ooi_example("not_a_real_example")


def test_fetch_requires_confirmation() -> None:
    with patch(
        "das_student_lab.datasets._remote_size_bytes", return_value=1024
    ):
        with pytest.raises(ValueError, match="confirm=True"):
            fetch_ooi_example(confirm=False)


def test_fetch_rejects_oversized_file() -> None:
    too_large = 600 * 1024 * 1024
    with patch(
        "das_student_lab.datasets._remote_size_bytes", return_value=too_large
    ):
        with pytest.raises(ValueError, match="exceeds"):
            fetch_ooi_example(confirm=True)


def test_fetch_downloads_and_writes_manifest(tmp_path: Path) -> None:
    fake_bytes = b"pretend tdms file contents"
    mock_response = MagicMock()
    mock_response.headers.get.return_value = str(len(fake_bytes))
    mock_response.read.side_effect = [fake_bytes, b""]
    mock_response.__enter__.return_value = mock_response

    with patch(
        "das_student_lab.datasets.urllib.request.urlopen",
        return_value=mock_response,
    ):
        result_path = fetch_ooi_example(confirm=True, cache_dir=tmp_path)

    assert result_path.exists()
    assert result_path.read_bytes() == fake_bytes

    manifest_path = tmp_path / f"{result_path.name}.manifest.json"
    assert manifest_path.exists()
    assert OOI_DATASET.doi in manifest_path.read_text()