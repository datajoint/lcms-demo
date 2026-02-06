"""
Scan schema for LC-MS pipeline.

Tables: Scans, Spectra, Peaks (with Part tables for individual data)
"""

import datajoint as dj
import numpy as np

from lcms_demo.pipeline import session

schema = dj.Schema("scan")


@schema
class Scans(dj.Imported):
    definition = """
    # All scans for a session
    -> session.Session
    ---
    n_scans : int32  # total number of scans
    """

    class Scan(dj.Part):
        definition = """
        # Individual scan within a session
        -> master
        scan_number : int32
        ---
        retention_time : float64  # minutes
        ms_level : int32  # 1=MS1, 2=MS2
        total_ion_current : float64
        base_peak_mz : float64
        base_peak_intensity : float64
        """

    def make(self, key):
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

        self.insert1({**key, "n_scans": len(scan_entries)})
        self.Scan.insert(scan_entries)


@schema
class Spectra(dj.Imported):
    definition = """
    # All spectra for a session
    -> Scans
    """

    class Spectrum(dj.Part):
        definition = """
        # Mass spectrum arrays for one scan
        -> master
        scan_number : int32  # matches Scans.Scan
        ---
        mz_array : <blob>  # m/z values
        intensity_array : <blob>  # intensity values
        """

    def make(self, key):
        from pyteomics import mzml

        raw_data_path = (session.Session & key).fetch1("raw_data_path")

        spectrum_entries = []
        with mzml.read(raw_data_path) as reader:
            for scan_number, spectrum in enumerate(reader, start=1):
                mz_array = np.array(spectrum["m/z array"], dtype=np.float32)
                intensity_array = np.array(spectrum["intensity array"], dtype=np.float32)

                spectrum_entries.append({
                    **key,
                    "scan_number": scan_number,
                    "mz_array": mz_array,
                    "intensity_array": intensity_array,
                })

        self.insert1(key)
        self.Spectrum.insert(spectrum_entries)


@schema
class Peaks(dj.Computed):
    definition = """
    # All detected peaks for a session
    -> Spectra
    ---
    total_peaks : int32  # total peaks across all scans
    """

    class Peak(dj.Part):
        definition = """
        # Individual detected peak
        -> master
        scan_number : int32  # matches Spectra.Spectrum
        peak_idx : int32
        ---
        mz : float64
        intensity : float64
        snr : float64  # signal-to-noise ratio
        """

    def make(self, key):
        from scipy.signal import find_peaks
        from scipy.stats import median_abs_deviation

        spectra = (Spectra.Spectrum & key).fetch(as_dict=True)

        peak_entries = []
        for spectrum in spectra:
            mz_array = spectrum["mz_array"]
            intensity_array = spectrum["intensity_array"]

            noise_level = 1.4826 * median_abs_deviation(intensity_array)
            if noise_level == 0:
                noise_level = 1.0

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
                    **key,
                    "scan_number": spectrum["scan_number"],
                    "peak_idx": idx,
                    "mz": peak_mz,
                    "intensity": peak_intensity,
                    "snr": float(snr),
                })

        self.insert1({**key, "total_peaks": len(peak_entries)})
        if peak_entries:
            self.Peak.insert(peak_entries)
