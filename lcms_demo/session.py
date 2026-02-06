"""
Session schema for LC-MS pipeline.

Defines tables for instruments, acquisition methods, and LC-MS sessions.

Tables
------
Instrument : Lookup
    LC-MS instrument reference data.
AcquisitionMethod : Lookup
    Acquisition method/protocol reference data.
Session : Manual
    LC-MS acquisition session metadata.
"""

import datajoint as dj

from lcms_demo import subject
from lcms_demo.config import get_schema_prefix

schema = dj.Schema(f"{get_schema_prefix()}session")


@schema
class Instrument(dj.Lookup):
    """
    LC-MS instrument information.

    Attributes
    ----------
    instrument_id : varchar(32)
        Unique identifier for the instrument.
    instrument_name : varchar(128)
        Human-readable name.
    manufacturer : varchar(64)
        Instrument manufacturer (optional).
    model : varchar(64)
        Instrument model (optional).
    """

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
    """
    LC-MS acquisition method/protocol.

    Attributes
    ----------
    method_id : varchar(32)
        Unique identifier for the method.
    method_name : varchar(128)
        Human-readable name.
    ionization_mode : enum
        Ionization mode: 'positive', 'negative', or 'both'.
    method_description : varchar(1024)
        Detailed description (optional).
    """

    definition = """
    # LC-MS acquisition method
    method_id : varchar(32)
    ---
    method_name : varchar(128)
    ionization_mode : enum('positive', 'negative', 'both')
    method_description = '' : varchar(1024)
    """

    contents = [
        ("POS_METAB", "Positive Metabolomics", "positive", "Standard positive mode metabolomics"),
        ("NEG_METAB", "Negative Metabolomics", "negative", "Standard negative mode metabolomics"),
    ]


@schema
class Session(dj.Manual):
    """
    A single LC-MS acquisition session/run.

    Each session corresponds to one sample analyzed on one instrument
    using one acquisition method.

    Attributes
    ----------
    subject_id : varchar(32)
        Foreign key to Subject (via Sample).
    sample_id : varchar(32)
        Foreign key to Sample.
    session_datetime : datetime
        When the acquisition was performed.
    instrument_id : varchar(32)
        Foreign key to Instrument.
    method_id : varchar(32)
        Foreign key to AcquisitionMethod.
    raw_data_path : varchar(512)
        Path to the raw data file.
    session_notes : varchar(1024)
        Notes about the session (optional).
    """

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
