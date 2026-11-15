"""Optional retained-research diagnostic; source files are never modified."""

import importlib.util, json, numpy as np
import sys

sys.dont_write_bytecode = True
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--research-root", required=True, type=Path)
args = parser.parse_args()
from scipy.optimize import minimize_scalar
from numpy.polynomial.legendre import leggauss

spec = importlib.util.spec_from_file_location(
    "audit_neatm", str(args.research_root / "research/feasibility/neatm.py")
)
N = importlib.util.module_from_spec(spec)
spec.loader.exec_module(N)


def physical(D, H, r, lam):
    pV = np.clip((1329 / D) ** 2 * 10 ** (-0.4 * H), 0.01, 1.0)
    delta = np.sqrt(r * r - 1)
    alpha = np.rad2deg(np.arcsin(1 / r))  # observer at 1 au, solar elongation 90 deg
    return (
        D
        * D
        * np.array(
            [
                N.neatm1(l, r, delta, alpha, 1.55, pV)
                + N.refl1(l, r, delta, alpha, 1.4 * pV)
                for l in lam
            ]
        )
    )


res = []
lam = np.linspace(3.83, 4.95, 18)
H = 18.0
truth = 0.5
for r in (1.05, 1.5, 2.0):
    observed = physical(truth, H, r, lam)
    row = {
        "synthetic": True,
        "r_au": r,
        "observer_distance_au": float(np.sqrt(r * r - 1)),
        "phase_deg": float(np.rad2deg(np.arcsin(1 / r))),
        "true_diameter_km": truth,
        "fixed_H": H,
        "results": [],
    }
    for reference in (0.4, 0.7, 1.0):
        template = physical(reference, H, r, lam)
        weights = 1 / (0.02 * observed) ** 2
        q = np.sum(weights * observed * template) / np.sum(weights * template**2)
        row["results"].append(
            {
                "reference_diameter_km": reference,
                "cv_amplitude_diameter_km": reference * np.sqrt(q),
            }
        )
    blind = minimize_scalar(
        lambda D: np.sum(
            ((observed - physical(D, H, r, lam)) / (0.02 * observed)) ** 2
        ),
        bounds=(0.3, 1.3),
        method="bounded",
    )
    row["blind_fit_diameter_km"] = blind.x
    res.append(row)


def quadrature(lam, r, delta, alpha, eta, pV):
    z, w = leggauss(100)
    u, v = leggauss(120)
    a = np.deg2rad(alpha)
    low = a - np.pi / 2
    high = np.pi / 2
    phi = (u + 1) * (high - low) / 2 + low
    wp = v * (high - low) / 2
    nx = np.sqrt(1 - z[:, None] ** 2) * np.cos(phi)
    mu = np.sqrt(1 - z[:, None] ** 2) * np.cos(phi - a)
    Tss = (
        (1 - (0.290 + 0.684 * 0.15) * pV) * 1361 / (eta * 0.9 * 5.670374e-8 * r * r)
    ) ** 0.25
    T = Tss * np.maximum(nx, 1e-15) ** 0.25
    l = lam * 1e-6
    B = (
        2
        * 6.62607015e-34
        * 299792458**2
        / l**5
        / np.expm1(np.minimum(6.62607015e-34 * 299792458 / (l * 1.380649e-23 * T), 700))
    )
    return (
        0.9
        * np.sum(B * mu * w[:, None] * wp)
        * 500**2
        / (delta * 149597870700.0) ** 2
        * l
        * l
        / 299792458
        * 1e29
    )


checks = []
for lam, r, delta, alpha in [
    (4.3, 1.0, 0.3, 40.0),
    (4.8, 1.4, 0.8, 80.0),
    (3.9, 1.2, 0.4, 100.0),
]:
    native = N.neatm1(lam, r, delta, alpha, 1.48, 0.14)
    ind = quadrature(lam, r, delta, alpha, 1.48, 0.14)
    checks.append(
        {
            "lambda_um": lam,
            "r_au": r,
            "phase_deg": alpha,
            "grid_to_independent_quadrature_ratio": native / ind,
        }
    )
print(
    json.dumps(
        {"reference_leakage_diagnostic": res, "neatm_quadrature": checks}, indent=2
    )
)
