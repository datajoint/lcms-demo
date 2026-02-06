"""
Session schema for LC-MS pipeline.

Tables: Instrument, AcquisitionMethod, Session
"""

import datajoint as dj

from lcms_demo.pipeline import subject

schema = dj.Schema("session")


@schema
class Instrument(dj.Lookup):
    definition = """
    # LC-MS instrument
    instrument_id : varchar(32)
    ---
    instrument_name : varchar(128)
    manufacturer = '' : varchar(64)
    model = '' : varchar(64)
    """

    contents = [
        ("QTOF_01", "Agilent 6550 Q-TOF", "Agilent", "6550"),
        ("ORBI_01", "Thermo Q Exactive", "Thermo", "Q Exactive HF"),
    ]


@schema
class AcquisitionMethod(dj.Lookup):
    definition = """
    # LC-MS acquisition method
    method_id : varchar(32)
    ---
    method_name : varchar(128)
    ionization_mode : varchar(16)  # positive, negative, or both
    method_description = '' : varchar(1024)
    """

    contents = [
        ("POS_METAB", "Positive Metabolomics", "positive", "Standard positive mode metabolomics"),
        ("NEG_METAB", "Negative Metabolomics", "negative", "Standard negative mode metabolomics"),
    ]


@schema
class Session(dj.Manual):
    definition = """
    # LC-MS acquisition session
    -> subject.Sample
    session_datetime : datetime
    ---
    -> Instrument
    -> AcquisitionMethod
    raw_data_path : varchar(512)
    session_notes = '' : varchar(1024)
    """
