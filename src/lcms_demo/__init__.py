"""
LC-MS Demo Pipeline - A DataJoint pipeline for mass spectrometry data.

This package demonstrates DataJoint best practices with a realistic
LC-MS (Liquid Chromatography-Mass Spectrometry) data pipeline.

Example
-------
>>> from lcms_demo import subject, session, scan
>>> subject.Subject()
"""

__version__ = "0.1.0"


def __getattr__(name):
    """Lazy import modules to avoid database connection at import time."""
    import importlib

    if name in ("subject", "session", "scan", "ingest"):
        module = importlib.import_module(f".{name}", __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["__version__", "ingest", "scan", "session", "subject"]
