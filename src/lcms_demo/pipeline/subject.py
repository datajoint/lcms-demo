"""
Subject schema for LC-MS pipeline.

Tables: Subject, Sample
"""

import datajoint as dj

schema = dj.Schema("subject")


@schema
class Subject(dj.Manual):
    definition = """
    # Experimental subject or sample source
    subject_id : varchar(32)
    ---
    subject_description = '' : varchar(256)
    """


@schema
class Sample(dj.Manual):
    definition = """
    # Biological or chemical sample
    -> Subject
    sample_id : varchar(32)
    ---
    sample_type : varchar(64)  # e.g., plasma, liver, urine
    collection_datetime = null : datetime
    sample_description = '' : varchar(256)
    """
