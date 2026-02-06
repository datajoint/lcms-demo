"""
Pipeline operations for ingesting LC-MS data.

This module contains functions for populating the pipeline tables
from real mzML files. For simulated data, see lcms_demo.simulation.
"""

import numpy as np

from lcms_demo import scan, session


def ingest_scans(session_key: dict) -> None:
    """
    Ingest scan metadata from an mzML file into Scans and Scans.Scan tables.

    Parameters
    ----------
    session_key : dict
        Primary key of the Session to ingest.
    """
    from pyteomics import mzml

    raw_data_path = (session.Session & session_key).fetch1("raw_data_path")

    scan_entries = []
    with mzml.read(raw_data_path) as reader:
        for scan_number, spectrum in enumerate(reader, start=1):
            rt_seconds = spectrum["scanList"]["scan"][0]["scan start time"]
            retention_time = float(rt_seconds) / 60.0
            ms_level = int(spectrum["ms level"])

            mz_array = spectrum["m/z array"]
            intensity_array = spectrum["intensity array"]

            total_ion_current = float(np.sum(intensity_array))

            if len(intensity_array) > 0:
                base_peak_idx = np.argmax(intensity_array)
                base_peak_mz = float(mz_array[base_peak_idx])
                base_peak_intensity = float(intensity_array[base_peak_idx])
            else:
                base_peak_mz = 0.0
                base_peak_intensity = 0.0

            scan_entries.append({
                **session_key,
                "scan_number": scan_number,
                "retention_time": retention_time,
                "ms_level": ms_level,
                "total_ion_current": total_ion_current,
                "base_peak_mz": base_peak_mz,
                "base_peak_intensity": base_peak_intensity,
            })

    scan.Scans.insert1({**session_key, "n_scans": len(scan_entries)})
    scan.Scans.Scan.insert(scan_entries)


def ingest_spectra(session_key: dict) -> None:
    """
    Ingest spectrum arrays from an mzML file into Spectra and Spectra.Spectrum tables.

    Parameters
    ----------
    session_key : dict
        Primary key of the Session to ingest.
    """
    from pyteomics import mzml

    raw_data_path = (session.Session & session_key).fetch1("raw_data_path")

    spectrum_entries = []
    with mzml.read(raw_data_path) as reader:
        for scan_number, spectrum in enumerate(reader, start=1):
            mz_array = np.array(spectrum["m/z array"], dtype=np.float32)
            intensity_array = np.array(spectrum["intensity array"], dtype=np.float32)

            spectrum_entries.append({
                **session_key,
                "scan_number": scan_number,
                "mz_array": mz_array,
                "intensity_array": intensity_array,
            })

    scan.Spectra.insert1(session_key)
    scan.Spectra.Spectrum.insert(spectrum_entries)


def detect_peaks(session_key: dict) -> None:
    """
    Detect peaks in all spectra for a session.

    Parameters
    ----------
    session_key : dict
        Primary key of the Session to process.
    """
    from scipy.signal import find_peaks
    from scipy.stats import median_abs_deviation

    spectra = (scan.Spectra.Spectrum & session_key).fetch(as_dict=True)

    peak_entries = []
    for spectrum in spectra:
        mz_array = spectrum["mz_array"]
        intensity_array = spectrum["intensity_array"]

        # Estimate noise level using MAD
        noise_level = 1.4826 * median_abs_deviation(intensity_array)
        if noise_level == 0:
            noise_level = 1.0

        # Find peaks
        peak_indices, _ = find_peaks(
            intensity_array,
            height=3 * noise_level,
            prominence=2 * noise_level,
            distance=3,
        )

        for idx, peak_idx in enumerate(peak_indices):
            peak_mz = float(mz_array[peak_idx])
            peak_intensity = float(intensity_array[peak_idx])
            snr = peak_intensity / noise_level

            peak_entries.append({
                **session_key,
                "scan_number": spectrum["scan_number"],
                "peak_idx": idx,
                "mz": peak_mz,
                "intensity": peak_intensity,
                "snr": float(snr),
            })

    scan.Peaks.insert1({**session_key, "total_peaks": len(peak_entries)})
    if peak_entries:
        scan.Peaks.Peak.insert(peak_entries)


def ingest_session(session_key: dict, detect_peaks_flag: bool = False) -> None:
    """
    Ingest all data for a session from mzML file.

    Parameters
    ----------
    session_key : dict
        Primary key of the Session to ingest.
    detect_peaks_flag : bool
        If True, also run peak detection after ingesting spectra.
    """
    ingest_scans(session_key)
    ingest_spectra(session_key)
    if detect_peaks_flag:
        detect_peaks(session_key)
