# Scientific and Data-Access Test Contracts

These are specifications for David to refine before implementation. Do not convert them mechanically into passing tests without understanding the scientific and data-access behavior.

## Public-data accessor

- Exact official source path and expected byte size are documented.
- User sees size before transfer.
- Default request cannot exceed 500 MB.
- Cache location is configurable and outside the installed package.
- Checksum mismatch deletes or quarantines the corrupted download.
- Offline error contains an actionable alternative.
- Insufficient disk space fails before transfer.
- Manifest records DOI, source, time range, cable/fiber, channels, checksum, and retrieval time.
- Second identical request uses the verified cache.

## Metadata-aware summary

- Known dimension order and units are read from a supported object.
- Missing units are reported as unknown rather than guessed.
- Reversed or unexpected axes are rejected or explicitly transformed.
- Lazy arrays are not accidentally loaded merely to summarize metadata.
- Estimated memory distinguishes stored, lazy, and materialized sizes.

## Any future detection method

- Synthetic call with known timing is detected within a stated tolerance.
- Pure noise does not produce an uncontrolled number of detections.
- Threshold behavior is tested at boundary values.
- Results preserve channels, time coordinates, units, parameters, and method citation.
- Comparison with an established implementation is documented.

## Any future localization method

- Synthetic source coordinates are recovered within a stated tolerance.
- Degenerate cable geometry is detected.
- Low-SNR or insufficient-channel input returns uncertainty/failure rather than false precision.
- Coordinate reference system and units are explicit.
- Results distinguish ground truth, estimate, and uncertainty.
- Related published implementations and licensing are documented.

