"""
Integration test fixtures.

Uses testcontainers to spin up a PostgreSQL database for tests.
"""

import os

import pytest


@pytest.fixture(scope="session")
def postgres_container():
    """Start a PostgreSQL container for the test session."""
    # Skip if using external database
    if os.environ.get("DJ_USE_EXTERNAL_DB"):
        yield None
        return

    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16") as postgres:
        # Configure DataJoint to use the container
        os.environ["DJ_HOST"] = postgres.get_container_host_ip()
        os.environ["DJ_USER"] = "test"
        os.environ["DJ_PASS"] = "test"
        # PostgreSQL port from container
        port = postgres.get_exposed_port(5432)
        os.environ["DJ_PORT"] = str(port)

        yield postgres


@pytest.fixture(scope="function")
def clean_schemas(postgres_container):
    """Drop and recreate schemas for each test."""
    import importlib

    import datajoint as dj

    from lcms_demo.pipeline import scan, session, subject

    prefix = dj.config.database.database_prefix or ""
    schema_names = [f"{prefix}scan", f"{prefix}session", f"{prefix}subject"]

    # Drop schemas in reverse order (respecting dependencies)
    for schema_name in schema_names:
        schema = dj.Schema(schema_name)
        schema.drop(prompt=False)

    # `@schema` declares tables at import time, so a drop leaves the cached modules
    # pointing at tables that no longer exist. Reload in dependency order to re-declare
    # them, so each test starts from a freshly created (empty) schema.
    for module in (subject, session, scan):
        importlib.reload(module)

    yield

    # Cleanup after test
    for schema_name in schema_names:
        try:
            schema = dj.Schema(schema_name)
            schema.drop(prompt=False)
        except Exception:
            pass
