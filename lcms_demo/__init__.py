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
    """Lazy import schema modules to avoid database connection at import time."""
    if name == "subject":
        from lcms_demo import subject
        return subject
    elif name == "session":
        from lcms_demo import session
        return session
    elif name == "scan":
        from lcms_demo import scan
        return scan
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["subject", "session", "scan", "__version__"]
