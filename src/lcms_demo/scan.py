"""
Scan schema for LC-MS pipeline.

Defines tables for scan metadata, spectral data, and peak detection.

Tables
------
Scan : Imported
    Individual scan metadata within a session.
ScanSpectrum : Imported
    Mass spectrum arrays (m/z and intensity).
PeakList : Computed
    Detected peaks with Peak part table.
"""

import datajoint as dj
import numpy as np

from lcms_demo import session
from lcms_demo.config import get_schema_prefix

schema = dj.Schema(f"{get_schema_prefix()}scan")


@schema
class Scan(dj.Imported):
    """
    Individual scan within an LC-MS session.

    Attributes
    ----------
    scan_number : int
        Sequential scan number within the session.
    retention_time : double
        Retention time in minutes.
    ms_level : tinyint unsigned
        MS level (1 for MS1, 2 for MS2).
    total_ion_current : double
        Total ion current for the scan.
    base_peak_mz : double
        m/z of the most intense peak.
    base_peak_intensity : double
        Intensity of the most intense peak.
    """

    definition = """
    # Individual scan within a session
    -> session.Session
    scan_number : int
    ---
    retention_time : double  # minutes
    ms_level : tinyint unsigned  # 1=MS1, 2=MS2
    total_ion_current : double
    base_peak_mz : double
    base_peak_intensity : double
    """

    def make(self, key):
        """
        Populate scan data from raw mzML files.

        Parameters
        ----------
        key : dict
            Primary key of the Session to populate.

        Notes
        -----
        Requires pyteomics package: pip install pyteomics
        """
        from pyteomics import mzml

        raw_data_path = (session.Session & key).fetch1("raw_data_path")

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
                    **key,
                    "scan_number": scan_number,
                    "retention_time": retention_time,
                    "ms_level": ms_level,
                    "total_ion_current": total_ion_current,
                    "base_peak_mz": base_peak_mz,
                    "base_peak_intensity": base_peak_intensity,
                })

        self.insert(scan_entries)


@schema
class ScanSpectrum(dj.Imported):
    """
    Mass spectrum data for each scan.

    Attributes
    ----------
    mz_array : longblob
        Array of m/z values (numpy float32).
    intensity_array : longblob
        Array of intensity values (numpy float32).
    """

    definition = """
    # Mass spectrum arrays
    -> Scan
    ---
    mz_array : longblob  # m/z values
    intensity_array : longblob  # intensity values
    """

    def make(self, key):
        """
        Extract spectrum arrays from raw mzML data.

        Parameters
        ----------
        key : dict
            Primary key of the Scan.
        """
        from pyteomics import mzml

        scan_info = (Scan & key).fetch1()
        session_key = {
            k: scan_info[k]
            for k in ["subject_id", "sample_id", "session_datetime"]
        }
        raw_data_path = (session.Session & session_key).fetch1("raw_data_path")

        scan_number = key["scan_number"]
        with mzml.read(raw_data_path) as reader:
            for idx, spectrum in enumerate(reader, start=1):
                if idx == scan_number:
                    mz_array = np.array(spectrum["m/z array"], dtype=np.float32)
                    intensity_array = np.array(
                        spectrum["intensity array"], dtype=np.float32
                    )
                    self.insert1({
                        **key,
                        "mz_array": mz_array,
                        "intensity_array": intensity_array,
                    })
                    break


@schema
class PeakList(dj.Computed):
    """
    Detected peaks from scan spectra.

    Attributes
    ----------
    peak_count : int
        Number of peaks detected.
    """

    definition = """
    # Detected peaks
    -> ScanSpectrum
    ---
    peak_count : int
    """

    class Peak(dj.Part):
        """
        Individual detected peak.

        Attributes
        ----------
        peak_idx : int
            Index of the peak within the scan.
        mz : double
            m/z value of the peak.
        intensity : double
            Intensity of the peak.
        snr : double
            Signal-to-noise ratio.
        """

        definition = """
        # Individual peak
        -> master
        peak_idx : int
        ---
        mz : double
        intensity : double
        snr : double
        """

    def make(self, key):
        """
        Detect peaks using scipy's find_peaks algorithm.

        Parameters
        ----------
        key : dict
            Primary key of the ScanSpectrum.
        """
        from scipy.signal import find_peaks
        from scipy.stats import median_abs_deviation

        spectrum = (ScanSpectrum & key).fetch1()
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

        # Build peak entries
        peak_entries = []
        for idx, peak_idx in enumerate(peak_indices):
            peak_mz = float(mz_array[peak_idx])
            peak_intensity = float(intensity_array[peak_idx])
            snr = peak_intensity / noise_level

            peak_entries.append({
                **key,
                "peak_idx": idx,
                "mz": peak_mz,
                "intensity": peak_intensity,
                "snr": float(snr),
            })

        self.insert1({**key, "peak_count": len(peak_entries)})

        if peak_entries:
            self.Peak.insert(peak_entries)
