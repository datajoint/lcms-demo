"""
Integration tests for database operations.
"""

import pytest


@pytest.mark.integration
class TestDatabaseConnection:
    """Test database connectivity."""

    def test_connection(self, postgres_container):
        """Should connect to database successfully."""
        import datajoint as dj

        conn = dj.conn()
        assert conn.is_connected

    def test_schema_creation(self, postgres_container, clean_schemas):
        """Should create schemas and tables."""
        from lcms_demo.pipeline import scan, session, subject

        # Tables should exist
        assert len(subject.Subject()) >= 0
        assert len(subject.Sample()) >= 0
        assert len(session.Instrument()) >= 0
        assert len(session.Session()) >= 0
        assert len(scan.Acquisition.Scan()) >= 0


@pytest.mark.integration
class TestDataPopulation:
    """Test data insertion and queries."""

    def test_insert_subject(self, postgres_container, clean_schemas):
        """Should insert and retrieve a subject."""
        from lcms_demo.pipeline import subject

        subject.Subject.insert1({
            "subject_id": "TEST_001",
            "subject_description": "Test subject",
        })

        result = (subject.Subject & {"subject_id": "TEST_001"}).fetch1()
        assert result["subject_id"] == "TEST_001"

    def test_acquire_demo_data(self, postgres_container, clean_schemas):
        """Should acquire demo data successfully."""
        from lcms_demo.pipeline import scan, session, subject
        from lcms_demo.simulation import acquire_demo_data

        summary = acquire_demo_data(
            n_subjects=2,
            samples_per_subject=1,
            scans_per_session=10,
            seed=42,
        )

        assert summary["subjects"] == 2
        assert len(subject.Subject()) == 2
        assert len(subject.Sample()) == 2
        assert len(session.Session()) == 2

        # Populate downstream tables
        scan.Acquisition.populate(display_progress=False)
        assert len(scan.Acquisition.Scan()) == 20  # 2 sessions x 10 scans
