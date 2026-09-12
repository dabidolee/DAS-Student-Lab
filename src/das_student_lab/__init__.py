"""Beginner-facing tools for learning with small DAS arrays.

This package is a pre-alpha educational scaffold. It is not a validated
whale-detection or acoustic-localization system.
"""

from das_student_lab.datasets import OOI_DATASET, DatasetCitation
from das_student_lab.diagnostics import ArraySummary, format_summary, summarize_array
from das_student_lab.synthetic import SyntheticDAS, make_synthetic_whale

__all__ = [
    "ArraySummary",
    "DatasetCitation",
    "OOI_DATASET",
    "SyntheticDAS",
    "format_summary",
    "make_synthetic_whale",
    "summarize_array",
]

__version__ = "0.0.1"

