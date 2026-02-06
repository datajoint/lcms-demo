"""
Scan schema for LC-MS pipeline.

Tables: Scans, Spectra, Peaks (with Part tables for individual data)
"""

import datajoint as dj

from lcms_demo import session

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
