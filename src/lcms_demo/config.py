"""
Database configuration utilities for the LC-MS demo pipeline.

DataJoint 2.1 Configuration
---------------------------
DataJoint automatically loads configuration from multiple sources (in priority order):

1. Environment variables (``DJ_HOST``, ``DJ_USER``, ``DJ_PASS``, etc.)
2. Secrets directory (``.secrets/database.user``, ``.secrets/database.password``)
3. Project config file (``datajoint.json``)

Schema Prefix
-------------
Set ``database.database_prefix`` in datajoint.json or use ``DJ_DATABASE_PREFIX``
environment variable to prefix all schema names (e.g., ``lcms_`` → ``lcms_subject``).

Setup
-----
1. Copy ``datajoint.json.example`` to ``datajoint.json``
2. Copy ``.secrets.example/`` to ``.secrets/`` and add credentials
3. Import datajoint - it connects automatically

Example
-------
>>> import datajoint as dj
>>> dj.config.database.host
'localhost'
>>> dj.config.database.database_prefix
'lcms_'
"""

import os


def use_local_database() -> None:
    """
    Configure DataJoint to use local Docker PostgreSQL.

    Sets environment variables to connect to localhost with default
    credentials (datajoint/datajoint).

    Example
    -------
    >>> from lcms_demo.config import use_local_database
    >>> use_local_database()
    >>> from lcms_demo import subject  # Connects to localhost
    """
    os.environ["DJ_HOST"] = "localhost"
    os.environ["DJ_USER"] = "datajoint"
    os.environ["DJ_PASS"] = "datajoint"
    os.environ["DJ_BACKEND"] = "postgresql"


def use_remote_database() -> None:
    """
    Clear environment overrides, using datajoint.json settings.

    Example
    -------
    >>> from lcms_demo.config import use_remote_database
    >>> use_remote_database()
    >>> from lcms_demo import subject  # Uses datajoint.json settings
    """
    for var in ["DJ_HOST", "DJ_USER", "DJ_PASS"]:
        os.environ.pop(var, None)
