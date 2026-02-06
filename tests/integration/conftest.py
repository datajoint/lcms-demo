"""
Integration test fixtures.

Uses testcontainers to spin up a MySQL database for tests.
"""

import os

import pytest


@pytest.fixture(scope="session")
def mysql_container():
    """Start a MySQL container for the test session."""
    # Skip if using external database
    if os.environ.get("DJ_USE_EXTERNAL_DB"):
        yield None
        return

    from testcontainers.mysql import MySqlContainer

    with MySqlContainer("datajoint/mysql:8.0") as mysql:
        # Configure DataJoint to use the container
        os.environ["DJ_HOST"] = mysql.get_container_host_ip()
        os.environ["DJ_USER"] = "root"
        os.environ["DJ_PASS"] = "test"
        # MySQL port from container
        port = mysql.get_exposed_port(3306)
        os.environ["DJ_PORT"] = str(port)

        yield mysql


@pytest.fixture(scope="function")
def clean_schemas(mysql_container):
    """Drop and recreate schemas for each test."""
    import datajoint as dj

    from lcms_demo.config import get_schema_prefix

    prefix = get_schema_prefix()
    schema_names = [f"{prefix}scan", f"{prefix}session", f"{prefix}subject"]

    # Drop schemas in reverse order (respecting dependencies)
    for schema_name in schema_names:
        schema = dj.Schema(schema_name)
        schema.drop(force=True)

    yield

    # Cleanup after test
    for schema_name in schema_names:
        try:
            schema = dj.Schema(schema_name)
            schema.drop(force=True)
        except Exception:
            pass
