# Reproducible Project Manifest — Draft Schema

This is a design document, not an implemented format. David should test it against real beginner workflows.

```yaml
schema_version: 0.1
project:
  name: my_first_das_project
  created_utc: 2026-01-01T00:00:00Z

data:
  kind: synthetic | measured
  dataset_title: null
  doi: null
  source_url_or_path: null
  cable_or_fiber: null
  time_start_utc: null
  time_end_utc: null
  channel_start: null
  channel_end: null
  checksum_algorithm: sha256
  checksum: null
  downloaded_bytes: null

coordinates:
  dimension_order: [distance, time]
  sample_rate_hz: null
  channel_spacing_m: null
  coordinate_reference_system: null

processing:
  steps: []
  parameters: {}

software:
  das_student_lab_version: null
  python_version: null
  dependencies: {}
  git_commit: null

outputs:
  files: []
  notes: null
```

Questions before implementation:

- Which fields are required for synthetic versus measured data?
- How should unknown information be represented without guessing?
- Should the manifest be YAML, JSON, TOML, or a dataclass serialized to JSON?
- How are lazy/remote data references handled?
- How is personally identifying or confidential path information excluded?

