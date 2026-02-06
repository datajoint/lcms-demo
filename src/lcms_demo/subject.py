"""
Subject schema for LC-MS pipeline.

Defines tables for experimental subjects and biological samples.

Tables
------
Subject : Manual
    Experimental subject or sample source.
Sample : Manual
    Biological or chemical sample for LC-MS analysis.
"""

import datajoint as dj

# Schema name is automatically prefixed by dj.config.database.database_prefix
schema = dj.Schema("subject")


@schema
class Subject(dj.Manual):
    """
    Experimental subject or sample source.

    Attributes
    ----------
    subject_id : varchar(32)
        Unique identifier for the subject.
    subject_description : varchar(256)
        Free-text description (optional).
    """

    definition = """
    # Experimental subject or sample source
    subject_id : varchar(32)
    ---
    subject_description = '' : varchar(256)
    """


@schema
class Sample(dj.Manual):
    """
    Biological or chemical sample for LC-MS analysis.

    Attributes
    ----------
    subject_id : varchar(32)
        Foreign key to Subject.
    sample_id : varchar(32)
        Unique identifier for the sample within a subject.
    sample_type : varchar(64)
        Type of sample (e.g., 'plasma', 'liver', 'urine').
    collection_datetime : datetime
        When the sample was collected (optional).
    sample_description : varchar(256)
        Free-text description (optional).
    """

    definition = """
    # Biological or chemical sample
    -> Subject
    sample_id : varchar(32)
    ---
    sample_type : varchar(64)
    collection_datetime = null : datetime
    sample_description = '' : varchar(256)
    """
