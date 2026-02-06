"""
Functions to populate DataJoint tables with simulated data.
"""

from datetime import datetime

from lcms_demo.pipeline import scan, session, subject
from lcms_demo.simulation.generators import generate_chromatogram


def populate_session(
    subject_id: str,
    sample_id: str,
    sample_type: str = "plasma",
    n_scans: int = 100,
    instrument_id: str = "QTOF_01",
    method_id: str = "POS_METAB",
    seed: int | None = None,
) -> dict:
    """
    Populate a complete session with simulated data.

    Creates Subject, Sample, Session, Scans, and Spectra entries
    with synthetic LC-MS data.
    """
    # Insert subject if not exists
    if not (subject.Subject & {"subject_id": subject_id}):
        subject.Subject.insert1({
            "subject_id": subject_id,
            "subject_description": f"Demo subject {subject_id}",
        })

    # Insert sample if not exists
    sample_key = {"subject_id": subject_id, "sample_id": sample_id}
    if not (subject.Sample & sample_key):
        subject.Sample.insert1({
            **sample_key,
            "sample_type": sample_type,
            "collection_datetime": datetime.now(),
            "sample_description": f"Demo sample {sample_id}",
        })

    # Create session
    session_datetime = datetime.now()
    session_key = {
        **sample_key,
        "session_datetime": session_datetime,
    }

    session.Session.insert1({
        **session_key,
        "instrument_id": instrument_id,
        "method_id": method_id,
        "raw_data_path": f"/simulated/{subject_id}/{sample_id}.mzML",
        "session_notes": f"Simulated data with seed={seed}",
    })

    # Generate scan data
    scans_data = generate_chromatogram(n_scans=n_scans, seed=seed)

    # Insert Scans master entry
    scan.Scans.insert1(
        {**session_key, "n_scans": len(scans_data)},
        allow_direct_insert=True,
    )

    # Insert individual scans into Part table
    scan_entries = []
    spectrum_entries = []

    for scan_number, scan_data in enumerate(scans_data, start=1):
        scan_key = {**session_key, "scan_number": scan_number}

        scan_entries.append({
            **scan_key,
            "retention_time": scan_data["retention_time"],
            "ms_level": 1,
            "total_ion_current": scan_data["total_ion_current"],
            "base_peak_mz": scan_data["base_peak_mz"],
            "base_peak_intensity": scan_data["base_peak_intensity"],
        })

        spectrum_entries.append({
            **scan_key,
            "mz_array": scan_data["mz_array"],
            "intensity_array": scan_data["intensity_array"],
        })

    scan.Scans.Scan.insert(scan_entries, allow_direct_insert=True)

    # Insert Spectra master entry
    scan.Spectra.insert1(session_key, allow_direct_insert=True)

    # Insert individual spectra into Part table
    scan.Spectra.Spectrum.insert(spectrum_entries, allow_direct_insert=True)

    return session_key


def populate_demo_data(
    n_subjects: int = 3,
    samples_per_subject: int = 2,
    scans_per_session: int = 50,
    seed: int = 42,
) -> dict:
    """
    Populate tables with a complete demo dataset.
    """
    sample_types = ["plasma", "liver", "urine"]
    sessions_created = []

    for subj_idx in range(n_subjects):
        subject_id = f"SUBJ_{subj_idx + 1:03d}"

        for sample_idx in range(samples_per_subject):
            sample_id = f"SAMPLE_{sample_idx + 1:03d}"
            sample_type = sample_types[sample_idx % len(sample_types)]

            session_key = populate_session(
                subject_id=subject_id,
                sample_id=sample_id,
                sample_type=sample_type,
                n_scans=scans_per_session,
                seed=seed + subj_idx * 100 + sample_idx,
            )
            sessions_created.append(session_key)

    return {
        "subjects": n_subjects,
        "samples": n_subjects * samples_per_subject,
        "sessions": len(sessions_created),
        "scans": len(sessions_created) * scans_per_session,
    }
