"""
Simulation utilities for generating synthetic LC-MS data.

This module provides functions to generate realistic test data
without requiring actual instrument files.

Functions
---------
generate_spectrum
    Generate a synthetic mass spectrum.
populate_demo_data
    Populate tables with demo data.
populate_nvs4821_study
    Populate tables with hepatotoxicity study data.
"""

from lcms_demo.simulation.generators import generate_chromatogram, generate_spectrum

__all__ = [
    "generate_spectrum",
    "generate_chromatogram",
    "populate_demo_data",
    "populate_session",
    "populate_nvs4821_study",
]


def __getattr__(name):
    """Lazy import functions that require database connection."""
    if name == "populate_demo_data":
        from lcms_demo.simulation.populate import populate_demo_data
        return populate_demo_data
    elif name == "populate_session":
        from lcms_demo.simulation.populate import populate_session
        return populate_session
    elif name == "populate_nvs4821_study":
        from lcms_demo.simulation.nvs4821_study import populate_nvs4821_study
        return populate_nvs4821_study
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
