"""
Spectrum and chromatogram generation utilities.

Functions for creating synthetic LC-MS data with realistic characteristics.
"""

import numpy as np


def generate_spectrum(
    n_peaks: int = 50,
    mz_range: tuple[float, float] = (100.0, 1000.0),
    intensity_range: tuple[float, float] = (1e3, 1e6),
    noise_level: float = 100.0,
    seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate a synthetic mass spectrum.

    Parameters
    ----------
    n_peaks : int
        Number of peaks to generate.
    mz_range : tuple[float, float]
        Range of m/z values (min, max).
    intensity_range : tuple[float, float]
        Range of peak intensities (min, max).
    noise_level : float
        Standard deviation of baseline noise.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    mz_array : np.ndarray
        Array of m/z values (float32).
    intensity_array : np.ndarray
        Array of intensity values (float32).

    Example
    -------
    >>> mz, intensity = generate_spectrum(n_peaks=100, seed=42)
    >>> mz.shape
    (1000,)
    """
    rng = np.random.default_rng(seed)

    # Generate m/z grid
    n_points = 1000
    mz_array = np.linspace(mz_range[0], mz_range[1], n_points, dtype=np.float32)

    # Start with noise baseline
    intensity_array = np.abs(rng.normal(0, noise_level, n_points)).astype(np.float32)

    # Add peaks at random positions
    peak_positions = rng.integers(50, n_points - 50, size=n_peaks)
    peak_intensities = rng.uniform(intensity_range[0], intensity_range[1], size=n_peaks)
    peak_widths = rng.uniform(1.0, 5.0, size=n_peaks)

    for pos, height, width in zip(peak_positions, peak_intensities, peak_widths):
        # Gaussian peak shape
        x = np.arange(n_points)
        peak = height * np.exp(-0.5 * ((x - pos) / width) ** 2)
        intensity_array += peak.astype(np.float32)

    return mz_array, intensity_array


def generate_chromatogram(
    n_scans: int = 100,
    rt_range: tuple[float, float] = (0.5, 12.0),
    n_compounds: int = 20,
    seed: int | None = None,
) -> list[dict]:
    """
    Generate synthetic chromatographic data for multiple scans.

    Parameters
    ----------
    n_scans : int
        Number of scans to generate.
    rt_range : tuple[float, float]
        Retention time range in minutes (start, end).
    n_compounds : int
        Number of eluting compounds to simulate.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    list[dict]
        List of scan dictionaries with keys:
        - retention_time: float
        - total_ion_current: float
        - base_peak_mz: float
        - base_peak_intensity: float
        - mz_array: np.ndarray
        - intensity_array: np.ndarray

    Example
    -------
    >>> scans = generate_chromatogram(n_scans=50, seed=42)
    >>> len(scans)
    50
    """
    rng = np.random.default_rng(seed)

    # Generate compound elution profiles
    compound_rt = rng.uniform(rt_range[0] + 1, rt_range[1] - 1, n_compounds)
    compound_mz = rng.uniform(150, 800, n_compounds)
    compound_intensity = rng.uniform(1e4, 1e6, n_compounds)
    compound_width = rng.uniform(0.1, 0.5, n_compounds)  # RT width in minutes

    scans = []
    retention_times = np.linspace(rt_range[0], rt_range[1], n_scans)

    for scan_idx, rt in enumerate(retention_times):
        # Generate base spectrum
        mz_array, intensity_array = generate_spectrum(
            n_peaks=30,
            noise_level=50.0,
            seed=seed + scan_idx if seed else None,
        )

        # Add compound peaks based on elution profile
        for comp_rt, comp_mz, comp_int, comp_width in zip(
            compound_rt, compound_mz, compound_intensity, compound_width
        ):
            # Gaussian elution profile
            elution_factor = np.exp(-0.5 * ((rt - comp_rt) / comp_width) ** 2)
            if elution_factor > 0.01:  # Only add if significant
                # Find closest m/z index
                mz_idx = np.argmin(np.abs(mz_array - comp_mz))
                intensity_array[mz_idx] += comp_int * elution_factor

        # Calculate summary statistics
        total_ion_current = float(np.sum(intensity_array))
        base_peak_idx = np.argmax(intensity_array)
        base_peak_mz = float(mz_array[base_peak_idx])
        base_peak_intensity = float(intensity_array[base_peak_idx])

        scans.append({
            "retention_time": float(rt),
            "total_ion_current": total_ion_current,
            "base_peak_mz": base_peak_mz,
            "base_peak_intensity": base_peak_intensity,
            "mz_array": mz_array,
            "intensity_array": intensity_array,
        })

    return scans
