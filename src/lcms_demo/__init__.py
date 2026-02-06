"""
LC-MS Demo Pipeline - A DataJoint pipeline for mass spectrometry data.

This package demonstrates DataJoint best practices with a realistic
LC-MS (Liquid Chromatography-Mass Spectrometry) data pipeline.

Structure
---------
- lcms_demo.pipeline: Schema definitions (subject, session, scan)
- lcms_demo.simulation: Functions for generating simulated data

Example
-------
>>> from lcms_demo.pipeline import subject, session, scan
>>> subject.Subject()
"""

__version__ = "0.1.0"

__all__ = ["__version__", "pipeline", "simulation"]
