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

from lcms_demo.simulation.generators import generate_spectrum
from lcms_demo.simulation.populate import populate_demo_data, populate_session

__all__ = [
    "generate_spectrum",
    "populate_demo_data",
    "populate_session",
]

# Conditionally export hepatotoxicity study if available
try:
    from lcms_demo.simulation.nvs4821_study import populate_nvs4821_study
    __all__.append("populate_nvs4821_study")
except ImportError:
    pass
