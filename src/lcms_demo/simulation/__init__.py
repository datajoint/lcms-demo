"""
Simulation utilities for generating synthetic LC-MS data.

This module provides functions to generate realistic test data
without requiring actual instrument files.

Functions
---------
generate_spectrum
    Generate a synthetic mass spectrum.
acquire_demo_data
    Acquire demo data into Manual tables.
acquire_nvs4821_study
    Acquire hepatotoxicity study data into Manual tables.
"""

from lcms_demo.simulation.generators import generate_chromatogram, generate_spectrum

__all__ = [
    "generate_chromatogram",
    "generate_spectrum",
    "acquire_demo_data",
    "acquire_nvs4821_study",
    "acquire_session",
]


def __getattr__(name):
    """Lazy import functions that require database connection."""
    if name == "acquire_demo_data":
        from lcms_demo.simulation.acquire import acquire_demo_data
        return acquire_demo_data
    elif name == "acquire_session":
        from lcms_demo.simulation.acquire import acquire_session
        return acquire_session
    elif name == "acquire_nvs4821_study":
        from lcms_demo.simulation.nvs4821_study import acquire_nvs4821_study
        return acquire_nvs4821_study
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
