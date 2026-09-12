# Architecture

## Design principle

Keep the project a thin educational and reproducibility layer. Delegate established DAS file handling and signal processing to established packages whenever possible.

## Proposed layers

### 1. Examples and provenance

- Deterministic synthetic data for offline learning and tests.
- A future bounded public-data accessor.
- A manifest containing source, DOI, subset, checksum, parameters, and versions.

### 2. Diagnostics

- Array shape and axis expectations.
- Sampling, channel spacing, duration, and distance span.
- Memory and invalid values.
- Future adapters for metadata-aware library objects.

### 3. Teaching workflows

- Small, explicit recipes that use DASCore/DAS4Whales.
- Parameter-comparison exercises.
- Beginner explanations and actionable errors.
- No hidden claim that a wrapper invented the underlying method.

### 4. Optional scientific extension

One carefully scoped method originating from David's research may be added later, after mentor review, related-work analysis, licensing review, and synthetic validation.

## Dependency direction

```text
tutorials / CLI
      |
diagnostics + provenance + teaching helpers
      |
DASCore / DAS4Whales / NumPy / SciPy
      |
public OOI data or synthetic examples
```

The lower layers must not import from the tutorials. Scientific dependencies should remain optional until a feature genuinely requires them.

## Current state

Implemented:

- synthetic example;
- plain NumPy array summary;
- dataset citation object;
- status CLI;
- baseline tests.

Protected TODOs:

- public data accessor;
- metadata-aware DAS adapters;
- project manifest;
- teaching workflows;
- scientific extension.

