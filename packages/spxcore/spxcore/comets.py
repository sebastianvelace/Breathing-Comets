"""Independent verification of the CO2 P/R band and parent Haser conversion.

Model equations and constants: BUILD 8.9. This module checks retained measurements;
it does not replace the published census or regenerate its Monte Carlo intervals.
"""

from dataclasses import dataclass

import numpy as np
from scipy.integrate import quad
from scipy.special import k0, k1

AU_M = 149597870700.0
LIGHT_M_S = 299792458.0
PLANCK_J_S = 6.62607015e-34


def haser_fraction(x):
    """Fraction of parent molecules inside a projected circular aperture."""
    if not np.isfinite(x) or x <= 0:
        raise ValueError("Haser aperture ratio must be finite and positive")
    if x > 50:
        return 1.0
    return float(x * (quad(k0, x, np.inf, limit=200)[0] + 1 / x - k1(x)))


def co2_profile(wavelength, bandwidth, temperature, extra_width=0):
    """Unit-area even-J 12C16O2 profile sampled with each channel's response."""
    if temperature <= 0 or extra_width < 0 or np.any(np.asarray(bandwidth) <= 0):
        raise ValueError("Temperature and channel widths must be positive")
    j = np.arange(0, 120, 2)
    population = (2*j + 1) * np.exp(-0.3902*j*(j+1)*1.4388/temperature)
    population /= population.sum()
    centers = np.concatenate((1e4/(2349.143+2*0.3902*(j+1)),
                              1e4/(2349.143-2*0.3902*j[1:])))
    weights = np.concatenate((population*(j+1)/(2*j+1),
                              (population*j/(2*j+1))[1:]))
    weights /= weights.sum()
    sigma = np.hypot(np.asarray(bandwidth)/2.355, extra_width)
    offsets = (np.asarray(wavelength)[:, None] - centers)/sigma[:, None]
    return (np.exp(-offsets**2/2)*weights).sum(axis=1)/(sigma*np.sqrt(2*np.pi))


@dataclass(frozen=True)
class Co2Rate:
    q: float
    statistical_error: float
    chi2_red: float
    temperature_k: float
    extra_width_um: float


def fit_co2_rate(wavelength, bandwidth, flux_jy, error_jy, r_au, delta_au, aperture_px=3):
    """Fit a constant-Q band plus a linear continuum to retained D5 photometry.

    Uses geometry for each actual exposure, not median observer distance. The
    uncertainty here is statistical with residual inflation; it excludes velocity
    and other systematics and must not be described as the total uncertainty.
    """
    lam, bw, flux, error, r, delta = np.broadcast_arrays(
        wavelength, bandwidth, flux_jy, error_jy, r_au, delta_au)
    if lam.ndim != 1 or len(lam) < 5 or aperture_px <= 0:
        raise ValueError("At least five one-dimensional samples are required")
    if not all(np.all(np.isfinite(a)) for a in (lam, bw, flux, error, r, delta)):
        raise ValueError("Nonfinite spectral input")
    if any(np.any(a <= 0) for a in (lam, bw, error, r, delta)):
        raise ValueError("Wavelength, widths, errors and distances must be positive")
    conversion = 1e-26*LIGHT_M_S/(lam*1e-6)**2*1e-6
    observed, uncertainty = flux*conversion, error*conversion
    lifetime = 5e5*r**2
    speed = 850/np.sqrt(r)
    radius = aperture_px*6.15/206265*delta*AU_M
    fraction = np.array([haser_fraction(x) for x in radius/(speed*lifetime)])
    unit_rate_flux = (2.86e-3/r**2)*PLANCK_J_S*LIGHT_M_S/4.262e-6*lifetime*fraction/(4*np.pi*(delta*AU_M)**2)
    best = None
    for temperature in (20, 40, 60, 80, 100, 150):
        for width in (0, .005, .01, .015, .02):
            band = co2_profile(lam, bw, temperature, width)*unit_rate_flux*1e27
            matrix = np.column_stack((np.full_like(lam, 1e-16), (lam-4.26)*1e-16, band))
            weighted = matrix/uncertainty[:, None]
            parameters = np.linalg.lstsq(weighted, observed/uncertainty, rcond=None)[0]
            # Four fitted parameters include the selected profile temperature.
            chi2 = float(np.sum(((observed-matrix@parameters)/uncertainty)**2)/(len(lam)-4))
            covariance = np.linalg.inv(weighted.T@weighted)
            fit = Co2Rate(float(parameters[-1]*1e27),
                          float(np.sqrt(covariance[-1, -1]*max(1, chi2))*1e27),
                          chi2, temperature, width)
            if best is None or fit.chi2_red < best.chi2_red:
                best = fit
    return best
