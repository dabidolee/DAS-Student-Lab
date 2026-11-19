import hashlib
import json
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from das_student_lab import datasets
from das_student_lab.datasets import OOI_DATASET, fetch_ooi_example

FAKE_BYTES = b"pretend tdms file contents"
FAKE_EXAMPLE = {
    "url": "http://example.invalid/fake.tdms",
    "description": "fake example for tests",
    "time_window": "none",
    "channels": "none",
    "sha256": hashlib.sha256(FAKE_BYTES).hexdigest(),
}
URLOPEN = "das_student_lab.datasets.urllib.request.urlopen"


@pytest.fixture(autouse=True)
def fake_example():
    with patch.dict(datasets._KNOWN_EXAMPLES, {"fake": FAKE_EXAMPLE}):
        yield


def _mock_response(payload: bytes) -> MagicMock:
    response = MagicMock()
    response.headers.get.return_value = str(len(payload))
    response.read.side_effect = [payload, b""]
    response.__enter__.return_value = response
    return response


def test_ooi_citation_has_persistent_identifier() -> None:
    assert OOI_DATASET.year == 2023
    assert OOI_DATASET.doi == "https://doi.org/10.58046/5J60-FJ89"
    assert OOI_DATASET.doi in OOI_DATASET.citation
    assert "Ocean Observatories Initiative" in OOI_DATASET.citation


def test_real_example_has_a_pinned_checksum() -> None:
    example = datasets._KNOWN_EXAMPLES["north_65km_noisecheck"]
    assert len(example["sha256"]) == 64


def test_fetch_rejects_unknown_example(tmp_path: Path) -> None:
    with pytest.raises(KeyError, match="Unknown example"):
        fetch_ooi_example("not_a_real_example", cache_dir=tmp_path)


def test_fetch_requires_confirmation(tmp_path: Path) -> None:
    with patch("das_student_lab.datasets._remote_size_bytes", return_value=1024):
        with pytest.raises(ValueError, match="confirm=True"):
            fetch_ooi_example("fake", confirm=False, cache_dir=tmp_path)


def test_fetch_rejects_oversized_file(tmp_path: Path) -> None:
    too_large = 600 * 1024 * 1024
    with patch("das_student_lab.datasets._remote_size_bytes", return_value=too_large):
        with pytest.raises(ValueError, match="exceeds"):
            fetch_ooi_example("fake", confirm=True, cache_dir=tmp_path)


def test_fetch_downloads_and_writes_manifest(tmp_path: Path) -> None:
    with patch(URLOPEN, return_value=_mock_response(FAKE_BYTES)):
        result = fetch_ooi_example("fake", confirm=True, cache_dir=tmp_path)

    assert result.read_bytes() == FAKE_BYTES
    assert not list(tmp_path.glob("*.part"))

    manifest = json.loads((tmp_path / "fake.tdms.manifest.json").read_text())
    assert manifest["dataset_doi"] == OOI_DATASET.doi
    assert manifest["sha256"] == FAKE_EXAMPLE["sha256"]
    assert manifest["preprocessing"].startswith("none")
    assert manifest["retrieved_utc"]


def test_checksum_mismatch_is_quarantined_not_kept(tmp_path: Path) -> None:
    wrong = {**FAKE_EXAMPLE, "sha256": "0" * 64}
    with patch.dict(datasets._KNOWN_EXAMPLES, {"fake": wrong}):
        with patch(URLOPEN, return_value=_mock_response(FAKE_BYTES)):
            with pytest.raises(ValueError, match="Checksum mismatch"):
                fetch_ooi_example("fake", confirm=True, cache_dir=tmp_path)

    assert not (tmp_path / "fake.tdms").exists()
    assert len(list(tmp_path.glob("*.corrupt"))) == 1


def test_verified_cache_is_reused_without_network(tmp_path: Path) -> None:
    with patch(URLOPEN, return_value=_mock_response(FAKE_BYTES)):
        first = fetch_ooi_example("fake", confirm=True, cache_dir=tmp_path)

    with patch(URLOPEN, side_effect=AssertionError("network was used")):
        second = fetch_ooi_example("fake", cache_dir=tmp_path)

    assert second == first


def test_corrupted_cache_is_quarantined_and_redownloaded(tmp_path: Path) -> None:
    (tmp_path / "fake.tdms").write_bytes(b"corrupted")

    with patch(URLOPEN, return_value=_mock_response(FAKE_BYTES)):
        result = fetch_ooi_example("fake", confirm=True, cache_dir=tmp_path)

    assert result.read_bytes() == FAKE_BYTES
    assert (tmp_path / "fake.tdms.corrupt").read_bytes() == b"corrupted"


def test_offline_error_suggests_an_alternative(tmp_path: Path) -> None:
    with patch(URLOPEN, side_effect=urllib.error.URLError("no network")):
        with pytest.raises(ConnectionError, match="offline"):
            fetch_ooi_example("fake", confirm=True, cache_dir=tmp_path)


def test_insufficient_disk_space_fails_before_download(tmp_path: Path) -> None:
    with patch("das_student_lab.datasets._remote_size_bytes", return_value=1000):
        with patch(
            "das_student_lab.datasets.shutil.disk_usage",
            return_value=MagicMock(free=10),
        ):
            with pytest.raises(OSError, match="disk space"):
                fetch_ooi_example("fake", confirm=True, cache_dir=tmp_path)

    assert not list(tmp_path.glob("*.part"))