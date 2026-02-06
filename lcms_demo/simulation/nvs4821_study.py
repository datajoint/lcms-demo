"""
NVS-4821 Hepatotoxicity Study Simulation.

Generates simulated data from a preclinical hepatotoxicity study
evaluating NVS-4821, an LPAR1 inhibitor.

Treatment Groups
----------------
1. Vehicle (0 mg/kg) - 8 animals
2. NVS4821_Low (30 mg/kg) - 8 animals
3. NVS4821_Mid (100 mg/kg) - 8 animals
4. NVS4821_High (300 mg/kg) - 8 animals
5. Vehicle_Satellite (0 mg/kg) - 12 animals, Days 3, 7, 15
6. NVS4821_High_Satellite (300 mg/kg) - 12 animals, Days 3, 7, 15
"""

from datetime import datetime, timedelta

from lcms_demo.simulation.populate import populate_session

# Study design constants
TREATMENT_GROUPS = [
    {"group": 1, "name": "Vehicle", "dose_mg_kg": 0, "n_animals": 8, "timepoints": [15]},
    {"group": 2, "name": "NVS4821_Low", "dose_mg_kg": 30, "n_animals": 8, "timepoints": [15]},
    {"group": 3, "name": "NVS4821_Mid", "dose_mg_kg": 100, "n_animals": 8, "timepoints": [15]},
    {"group": 4, "name": "NVS4821_High", "dose_mg_kg": 300, "n_animals": 8, "timepoints": [15]},
    {"group": 5, "name": "Vehicle_Satellite", "dose_mg_kg": 0, "n_animals": 12, "timepoints": [3, 7, 15]},
    {"group": 6, "name": "NVS4821_High_Satellite", "dose_mg_kg": 300, "n_animals": 12, "timepoints": [3, 7, 15]},
]

SAMPLE_TYPES = ["plasma", "liver"]
IONIZATION_MODES = [("POS_METAB", "positive"), ("NEG_METAB", "negative")]


def populate_nvs4821_study(
    n_scans_per_session: int = 100,
    seed: int = 42,
    verbose: bool = True,
) -> dict:
    """
    Populate tables with NVS-4821 hepatotoxicity study data.

    Parameters
    ----------
    n_scans_per_session : int
        Number of scans per LC-MS session.
    seed : int
        Random seed for reproducibility.
    verbose : bool
        Print progress messages.

    Returns
    -------
    dict
        Summary of created data including counts by category.

    Example
    -------
    >>> summary = populate_nvs4821_study(n_scans_per_session=50, seed=42)
    >>> print(f"Created {summary['subjects']} subjects")
    """
    from lcms_demo import session, subject

    base_date = datetime(2026, 1, 1)
    sessions_created = []
    subject_count = 0

    for group in TREATMENT_GROUPS:
        group_name = group["name"]
        n_animals = group["n_animals"]
        timepoints = group["timepoints"]

        if verbose:
            print(f"Populating Group {group['group']}: {group_name} ({n_animals} animals)")

        for animal_idx in range(n_animals):
            subject_count += 1
            subject_id = f"RAT_{subject_count:03d}"

            # Insert subject with treatment info
            if not (subject.Subject & {"subject_id": subject_id}):
                subject.Subject.insert1({
                    "subject_id": subject_id,
                    "subject_description": f"Group {group['group']}: {group_name}, {group['dose_mg_kg']} mg/kg",
                })

            for timepoint_day in timepoints:
                collection_date = base_date + timedelta(days=timepoint_day)

                for sample_type in SAMPLE_TYPES:
                    sample_id = f"{sample_type.upper()}_D{timepoint_day:02d}"

                    # Insert sample if not exists
                    sample_key = {"subject_id": subject_id, "sample_id": sample_id}
                    if not (subject.Sample & sample_key):
                        subject.Sample.insert1({
                            **sample_key,
                            "sample_type": sample_type,
                            "collection_datetime": collection_date,
                            "sample_description": f"Day {timepoint_day} {sample_type} sample",
                        })

                    # Create sessions for each ionization mode
                    for method_id, mode in IONIZATION_MODES:
                        session_seed = seed + subject_count * 1000 + timepoint_day * 10 + hash(sample_type + mode) % 100

                        session_key = populate_session(
                            subject_id=subject_id,
                            sample_id=sample_id,
                            sample_type=sample_type,
                            n_scans=n_scans_per_session,
                            instrument_id="QTOF_01",
                            method_id=method_id,
                            seed=session_seed,
                        )
                        sessions_created.append(session_key)

    summary = {
        "subjects": subject_count,
        "samples": len(subject.Sample()),
        "sessions": len(sessions_created),
        "scans": len(sessions_created) * n_scans_per_session,
        "groups": len(TREATMENT_GROUPS),
    }

    if verbose:
        print(f"\nStudy populated:")
        print(f"  - {summary['subjects']} subjects (rats)")
        print(f"  - {summary['samples']} samples")
        print(f"  - {summary['sessions']} sessions")
        print(f"  - {summary['scans']} scans")

    return summary
