"""Dataset citations and a bounded, provenance preserving OOI example fetcher."""

import hashlib
import json
import shutil
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
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
# OOI PI web server, small enough to respect the 500 MiB default limit in the
# project's data-safety rules. These are short Silixa "noise check" recordings,
# not whale detections, and must not be described as containing a validated
# biological signal.
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
        # Known good SHA-256 of the exact file. Two separate downloads matched
        # this value byte for byte. Every download is verified against it.
        "sha256": "3f30fcb11ed5d2f43803a2c6c8869f26477e8f707d2a01c8a8230439a11b63fe",
    },
}

_MAX_BYTES = 500 * 1024 * 1024
_TIMEOUT_S = 30
_DISK_HEADROOM = 1.1


def _cache_dir() -> Path:
    """Return the local cache directory, creating it if needed.

    Cached files live outside the installed package, per the data-safety rules.
    """

    cache_dir = Path.home() / ".cache" / "das_student_lab" / "ooi_examples"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _offline_message(url: str) -> str:
    return (
        f"Could not reach {url}. Check your internet connection and try again. "
        "You can still work offline with make_synthetic_whale(), or, if you "
        "already downloaded the file, pass its path to read_tdms_subset()."
    )


def _remote_size_bytes(url: str) -> int:
    """Ask the server how large the file is without downloading it."""

    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_S) as response:
            content_length = response.headers.get("Content-Length")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ConnectionError(_offline_message(url)) from exc
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


def _quarantine(path: Path) -> Path:
    """Move a file that failed verification aside instead of silently reusing it."""

    quarantined = path.with_name(path.name + ".corrupt")
    path.replace(quarantined)
    return quarantined


def _write_manifest(
    manifest_path: Path,
    *,
    name: str,
    example: dict[str, str],
    size_bytes: int,
    retrieved_utc: str,
) -> None:
    """Record where a cached file came from, so provenance travels with it."""

    manifest = {
        "example_name": name,
        "dataset_citation": OOI_DATASET.citation,
        "dataset_doi": OOI_DATASET.doi,
        "source_url": example["url"],
        "description": example["description"],
        "time_window": example["time_window"],
        "channels": example["channels"],
        "preprocessing": "none; raw file as downloaded from source",
        "sha256": example["sha256"],
        "size_bytes": size_bytes,
        "retrieved_utc": retrieved_utc,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))


def fetch_ooi_example(
    name: str = "north_65km_noisecheck",
    *,
    confirm: bool = False,
    cache_dir: Path | None = None,
) -> Path:
    """Download and cache one small, exact, known-good OOI DAS example file.

    A cached copy that matches the known SHA-256 is returned immediately with
    no network access, so a file you already have keeps working offline.

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
        Local path to the checksum-verified file. A matching
        ``<file>.manifest.json`` sits alongside it recording the dataset
        citation, source URL, time window, channels, checksum, and the UTC
        time it was retrieved.

    Raises
    ------
    KeyError
        If ``name`` is not a known example.
    ValueError
        If the remote file exceeds the 500 MiB safety limit, ``confirm`` is not
        ``True``, or the downloaded file fails checksum verification (it is
        set aside with a ``.corrupt`` suffix and never used).
    OSError
        If there is not enough free disk space for the download.
    ConnectionError
        If the server cannot be reached.
    """

    if name not in _KNOWN_EXAMPLES:
        available = ", ".join(sorted(_KNOWN_EXAMPLES))
        raise KeyError(f"Unknown example {name!r}. Available examples: {available}")

    example = _KNOWN_EXAMPLES[name]
    url = example["url"]

    target_dir = cache_dir if cache_dir is not None else _cache_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = url.rsplit("/", maxsplit=1)[-1]
    target_path = target_dir / filename
    manifest_path = target_dir / f"{filename}.manifest.json"

    if target_path.exists():
        if _sha256_of_file(target_path) == example["sha256"]:
            if not manifest_path.exists():
                stat = target_path.stat()
                modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                _write_manifest(
                    manifest_path,
                    name=name,
                    example=example,
                    size_bytes=stat.st_size,
                    retrieved_utc=modified.isoformat(),
                )
            return target_path
        # Present but does not match the known good checksum: never reuse it.
        _quarantine(target_path)
        manifest_path.unlink(missing_ok=True)

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

    free_bytes = shutil.disk_usage(target_dir).free
    if free_bytes < size_bytes * _DISK_HEADROOM:
        raise OSError(
            f"Not enough disk space in {target_dir}: the download needs about "
            f"{size_mib:.1f} MiB and only {free_bytes / (1024**2):.1f} MiB is free. "
            "Free some space or pass a different cache_dir."
        )

    # Download to a temporary name so an interrupted transfer never leaves a
    # partial file sitting at the final path.
    part_path = target_path.with_name(target_path.name + ".part")
    try:
        with urllib.request.urlopen(url, timeout=_TIMEOUT_S) as response:
            with part_path.open("wb") as handle:
                while chunk := response.read(1024 * 1024):
                    handle.write(chunk)
    except (urllib.error.URLError, TimeoutError) as exc:
        part_path.unlink(missing_ok=True)
        raise ConnectionError(_offline_message(url)) from exc

    if _sha256_of_file(part_path) != example["sha256"]:
        corrupt_path = _quarantine(part_path)
        raise ValueError(
            f"Checksum mismatch for {name!r}: the downloaded file does not match "
            f"the known good SHA-256, so it was set aside as {corrupt_path.name} "
            "and will not be used. Delete it and try again; if this keeps "
            "happening, the file on the server may have changed."
        )

    part_path.replace(target_path)
    _write_manifest(
        manifest_path,
        name=name,
        example=example,
        size_bytes=target_path.stat().st_size,
        retrieved_utc=datetime.now(timezone.utc).isoformat(),
    )
    return target_path