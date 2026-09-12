"""Dataset citations and future access points.

No network download is implemented in the starter. Data access must be designed
after the official path, size, checksum, caching, and redistribution terms are
verified.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DatasetCitation:
    """Citation and landing-page metadata for a dataset.

    Parameters
    ----------
    title:
        Dataset title supplied by its publisher.
    creators:
        Creator string supplied by its publisher.
    year:
        Publication year.
    doi:
        Persistent digital object identifier URL.
    landing_page:
        Official project or access page.
    citation:
        Human-readable citation requested by the publisher.
    """

    title: str
    creators: str
    year: int
    doi: str
    landing_page: str
    citation: str


OOI_DATASET = DatasetCitation(
    title=(
        "Rapid: A Community Test of Distributed Acoustic Sensing on the "
        "Ocean Observatories Initiative Regional Cabled Array"
    ),
    creators="Wilcock, W., & Ocean Observatories Initiative",
    year=2023,
    doi="https://doi.org/10.58046/5J60-FJ89",
    landing_page=(
        "https://oceanobservatories.org/pi-instrument/rapid-a-community-test-of-"
        "distributed-acoustic-sensing-on-the-ocean-observatories-initiative-"
        "regional-cabled-array/"
    ),
    citation=(
        "Wilcock, W., & Ocean Observatories Initiative. (2023). Rapid: A "
        "Community Test of Distributed Acoustic Sensing on the Ocean "
        "Observatories Initiative Regional Cabled Array [Data set]. Ocean "
        "Observatories Initiative. https://doi.org/10.58046/5J60-FJ89"
    ),
)


def fetch_ooi_example(name: str = "fin_whale_small") -> None:
    """Placeholder for a future bounded, provenance-preserving data accessor.

    The implementation must not be added until the exact source URL, expected
    size, checksum, cache behavior, and redistribution terms are documented and
    tested. The function intentionally fails instead of pretending to download
    a real example.
    """

    raise NotImplementedError(
        f"Example {name!r} is not available in the starter. Complete the data-access "
        "design and tests before implementing this function. See "
        "docs/architecture.md and tests/TODO_TESTS.md."
    )

