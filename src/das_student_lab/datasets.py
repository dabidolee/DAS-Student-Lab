"""Dataset citations and a bounded, provenance-preserving OOI example fetcher."""

import hashlib
import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path


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


# Known small examples. Each entry is one exact, manually verified file on the
# OOI PI web server, chosen because it is small enough to respect the 500 MiB
# default limit described in the project's data-safety rules. These are short
# Silixa "noise check" recordings, not whale detections, and must not be
# described as containing a validated biological signal.
_KNOWN_EXAMPLES: dict[str, dict[str, str]] = {
    "north_65km_noisecheck": {
        "url": (
            "http://piweb.ooirsn.uw.edu/das/data/Silixa/DAS/North65km/"
            "noisecheck/P9/OOIPacCity_UTC_20211101_153340.764.tdms"
        ),
        "description": (
            "Short Silixa iDASv3 noise-check recording from the OOI Regional "
            "Cabled Array north cable (~65 km segment), collected 2021-11-01. "
            "This is an instrument noise check, not a labeled whale detection."
        ),
        "time_window": "2021-11-01T15:33:40.764Z (start of recording)",
        "channels": "All channels recorded by the Silixa iDASv3 unit on this segment",
    },
}

_MAX_BYTES = 500 * 1024 * 1024
_TIMEOUT_S = 30


def _cache_dir() -> Path:
    """Return the local cache directory, creating it if needed.

    Cached files live outside the installed package, per the data-safety rules.
    """

    cache_dir = Path.home() / ".cache" / "das_student_lab" / "ooi_examples"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _remote_size_bytes(url: str) -> int:
    """Ask the server how large the file is without downloading it."""

    request = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(request, timeout=_TIMEOUT_S) as response:
        content_length = response.headers.get("Content-Length")
    if content_length is None:
        raise RuntimeError(
            f"Server did not report a size for {url!r}; refusing to download "
            "blind. Try again later or verify the URL in a browser."
        )
    return int(content_length)


def _sha256_of_file(path: Path) -> str:
    """Compute a streaming SHA-256 checksum without loading the file into memory."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_ooi_example(
    name: str = "north_65km_noisecheck",
    *,
    confirm: bool = False,
    cache_dir: Path | None = None,
) -> Path:
    """Download and cache one small, exact, known-good OOI DAS example file.

    Parameters
    ----------
    name:
        Key identifying a known small example. See ``_KNOWN_EXAMPLES``.
    confirm:
        Must be explicitly set to ``True`` to allow a real network transfer.
        This is a deliberate safety gate: the function will not silently
        download data just because it was called.
    cache_dir:
        Optional override of the cache location, mainly for tests.

    Returns
    -------
    Path
        Local path to the downloaded and checksum-verified file. A matching
        ``<file>.manifest.json`` is written alongside it recording the
        dataset citation, source URL, time window, channels, and checksum.

    Raises
    ------
    KeyError
        If ``name`` is not a known example.
    ValueError
        If the remote file exceeds the 500 MiB safety limit, or ``confirm``
        is not ``True``.
    """

    if name not in _KNOWN_EXAMPLES:
        available = ", ".join(sorted(_KNOWN_EXAMPLES))
        raise KeyError(f"Unknown example {name!r}. Available examples: {available}")

    example = _KNOWN_EXAMPLES[name]
    url = example["url"]

    size_bytes = _remote_size_bytes(url)
    size_mib = size_bytes / (1024**2)

    if size_bytes > _MAX_BYTES:
        raise ValueError(
            f"{name!r} is {size_mib:.1f} MiB, which exceeds the "
            f"{_MAX_BYTES / (1024**2):.0f} MiB default limit; refusing to "
            "download automatically"
        )

    if not confirm:
        raise ValueError(
            f"fetch_ooi_example({name!r}) would download {size_mib:.1f} MiB "
            f"from {url}. Call again with confirm=True to proceed."
        )

    target_dir = cache_dir if cache_dir is not None else _cache_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = url.rsplit("/", maxsplit=1)[-1]
    target_path = target_dir / filename
    manifest_path = target_dir / f"{filename}.manifest.json"

    if target_path.exists() and manifest_path.exists():
        # Already cached; verify it before handing it back rather than
        # trusting a possibly stale or corrupted local copy.
        existing_checksum = _sha256_of_file(target_path)
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("sha256") == existing_checksum:
            return target_path

    request = urllib.request.Request(url)
    with urllib.request.urlopen(request, timeout=_TIMEOUT_S) as response:
        with target_path.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)

    checksum = _sha256_of_file(target_path)

    manifest = {
        "dataset_citation": OOI_DATASET.citation,
        "dataset_doi": OOI_DATASET.doi,
        "source_url": url,
        "description": example["description"],
        "time_window": example["time_window"],
        "channels": example["channels"],
	"preprocessing": "none; raw file as downloaded from source",
        "sha256": checksum,
        "size_bytes": size_bytes,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))

    return target_path