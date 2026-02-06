"""
Database configuration for the LC-MS demo pipeline.

DataJoint loads configuration from environment variables or dj_local_conf.json.
This module provides utilities for schema prefixing and database mode switching.

Environment Variables
---------------------
DJ_HOST : str
    Database hostname (default: localhost)
DJ_USER : str
    Database username
DJ_PASS : str
    Database password
"""

import json
import os
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _load_config() -> dict:
    """Load dj_local_conf.json from project root."""
    config_path = Path(__file__).parent.parent / "dj_local_conf.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def get_schema_prefix() -> str:
    """
    Get schema prefix from configuration.

    Returns
    -------
    str
        Schema prefix (e.g., 'lcms_demo_'), or empty string if not set.

    Notes
    -----
    The schema prefix is read from dj_local_conf.json under:
    {"custom": {"schema_prefix": "your_prefix_"}}
    """
    config = _load_config()
    return config.get("custom", {}).get("schema_prefix", "")


def use_local_database() -> None:
    """
    Configure DataJoint to use local Docker MySQL.

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


def use_remote_database() -> None:
    """
    Clear environment overrides, using dj_local_conf.json settings.

    Example
    -------
    >>> from lcms_demo.config import use_remote_database
    >>> use_remote_database()
    >>> from lcms_demo import subject  # Uses config file settings
    """
    for var in ["DJ_HOST", "DJ_USER", "DJ_PASS"]:
        os.environ.pop(var, None)
