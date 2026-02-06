"""
Unit tests for spectrum generation utilities.
"""

import numpy as np

from lcms_demo.simulation.generators import generate_chromatogram, generate_spectrum


class TestGenerateSpectrum:
    """Tests for generate_spectrum function."""

    def test_returns_arrays(self):
        """Should return mz and intensity arrays."""
        mz, intensity = generate_spectrum()
        assert isinstance(mz, np.ndarray)
        assert isinstance(intensity, np.ndarray)

    def test_array_shapes_match(self):
        """Arrays should have the same length."""
        mz, intensity = generate_spectrum()
        assert len(mz) == len(intensity)

    def test_mz_in_range(self):
        """m/z values should be within specified range."""
        mz_range = (200.0, 800.0)
        mz, _ = generate_spectrum(mz_range=mz_range)
        assert mz.min() >= mz_range[0]
        assert mz.max() <= mz_range[1]

    def test_reproducibility_with_seed(self):
        """Same seed should produce identical spectra."""
        mz1, int1 = generate_spectrum(seed=42)
        mz2, int2 = generate_spectrum(seed=42)
        np.testing.assert_array_equal(mz1, mz2)
        np.testing.assert_array_equal(int1, int2)

    def test_different_seeds_differ(self):
        """Different seeds should produce different spectra."""
        _, int1 = generate_spectrum(seed=42)
        _, int2 = generate_spectrum(seed=43)
        assert not np.allclose(int1, int2)

    def test_float32_dtype(self):
        """Arrays should be float32 for storage efficiency."""
        mz, intensity = generate_spectrum()
        assert mz.dtype == np.float32
        assert intensity.dtype == np.float32


class TestGenerateChromatogram:
    """Tests for generate_chromatogram function."""

    def test_returns_list(self):
        """Should return a list of scan dictionaries."""
        scans = generate_chromatogram(n_scans=10)
        assert isinstance(scans, list)
        assert len(scans) == 10

    def test_scan_keys(self):
        """Each scan should have required keys."""
        scans = generate_chromatogram(n_scans=1)
        required_keys = {
            "retention_time",
            "total_ion_current",
            "base_peak_mz",
            "base_peak_intensity",
            "mz_array",
            "intensity_array",
        }
        assert required_keys.issubset(scans[0].keys())

    def test_retention_time_order(self):
        """Retention times should be in ascending order."""
        scans = generate_chromatogram(n_scans=50)
        rts = [s["retention_time"] for s in scans]
        assert rts == sorted(rts)

    def test_rt_range(self):
        """Retention times should be within specified range."""
        rt_range = (1.0, 10.0)
        scans = generate_chromatogram(n_scans=20, rt_range=rt_range)
        rts = [s["retention_time"] for s in scans]
        assert min(rts) >= rt_range[0]
        assert max(rts) <= rt_range[1]

    def test_reproducibility(self):
        """Same seed should produce identical chromatograms."""
        scans1 = generate_chromatogram(n_scans=10, seed=42)
        scans2 = generate_chromatogram(n_scans=10, seed=42)
        for s1, s2 in zip(scans1, scans2):
            assert s1["retention_time"] == s2["retention_time"]
            assert s1["total_ion_current"] == s2["total_ion_current"]
