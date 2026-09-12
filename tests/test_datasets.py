import pytest

from das_student_lab.datasets import OOI_DATASET, fetch_ooi_example


def test_ooi_citation_has_persistent_identifier() -> None:
    assert OOI_DATASET.year == 2023
    assert OOI_DATASET.doi == "https://doi.org/10.58046/5J60-FJ89"
    assert OOI_DATASET.doi in OOI_DATASET.citation
    assert "Ocean Observatories Initiative" in OOI_DATASET.citation


def test_unimplemented_downloader_fails_explicitly() -> None:
    with pytest.raises(NotImplementedError, match="data-access design"):
        fetch_ooi_example()

