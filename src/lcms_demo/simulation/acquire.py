"""Functions to acquire simulated session metadata into Manual tables."""

from datetime import datetime

from lcms_demo.pipeline import session, subject


def acquire_session(
    subject_id: str,
    sample_id: str,
    sample_type: str = "plasma",
    instrument_id: str = "QTOF_01",
    method_id: str = "POS_METAB",
    seed: int | None = None,
    n_scans: int = 50,
) -> dict:
    """
    Acquire a simulated session into Manual tables.

    Inserts Subject, Sample, and Session entries. The Session.raw_data_path
    encodes simulation parameters that the make methods will use.
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

    # Determine next session_idx for this sample
    existing_sessions = session.Session & sample_key
    if existing_sessions:
        max_idx = max(existing_sessions.fetch("session_idx"))
        session_idx = max_idx + 1
    else:
        session_idx = 1

    session_key = {
        **sample_key,
        "session_idx": session_idx,
    }

    # Encode simulation parameters in the path
    raw_data_path = f"simulate://{seed or 0}/{n_scans}"

    session.Session.insert1({
        **session_key,
        "session_datetime": datetime.now(),
        "instrument_id": instrument_id,
        "method_id": method_id,
        "raw_data_path": raw_data_path,
        "session_notes": f"Simulated data with seed={seed}, n_scans={n_scans}",
    })

    return session_key


def acquire_demo_data(
    n_subjects: int = 3,
    samples_per_subject: int = 2,
    scans_per_session: int = 50,
    seed: int = 42,
) -> dict:
    """Acquire demo dataset metadata into Manual tables."""
    sample_types = ["plasma", "liver", "urine"]
    sessions_created = []

    for subj_idx in range(n_subjects):
        subject_id = f"SUBJ_{subj_idx + 1:03d}"

        for sample_idx in range(samples_per_subject):
            sample_id = f"SAMPLE_{sample_idx + 1:03d}"
            sample_type = sample_types[sample_idx % len(sample_types)]

            session_key = acquire_session(
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
    }
