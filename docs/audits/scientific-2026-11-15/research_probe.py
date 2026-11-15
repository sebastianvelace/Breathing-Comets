"""Optional retained-research diagnostic; source files are never modified."""

from pathlib import Path
import numpy as np, json
import csv as csvlib
from spxcore import comets, ephem
from astropy.coordinates import SkyCoord, get_body_barycentric
from astropy.time import Time
from astropy import units as u
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--research-root", required=True, type=Path)
args = parser.parse_args()
R = args.research_root / "data/derived"
out = {}


def csv(p):
    return np.genfromtxt(p, delimiter=",", names=True, dtype=None, encoding="utf8")


null = csv(R / "null_tests_physical.csv")
out["retained_nulls"] = {
    "n": len(null),
    "snr_only_ge5": int((null["snr_detect"] >= 5).sum()),
    "joint_rule_pass": int(((null["snr_detect"] >= 5) & (null["chi2_red"] < 50)).sum()),
    "largest_snr": float(null["snr_detect"].max()),
    "note": "Spectral controls are correlated and not processed identically to the sky-subtracted census; no population false-alarm rate is inferred.",
}
validation = csv(R / "spectrum_validation_2mass_wise.csv")
out["retained_stellar_scale"] = {}
for name in ("J", "H", "Ks", "W1", "W2"):
    v = validation["ratio"][validation["band"] == name]
    med = float(np.median(v))
    out["retained_stellar_scale"][name] = {
        "n": len(v),
        "median": med,
        "robust_MAD_sigma": float(1.4826 * np.median(np.abs(v - med))),
        "sample_standard_deviation_ddof1": float(v.std(ddof=1)),
    }
raw_cv = list(csvlib.DictReader((R / "neo_validation_cv50_psf.csv").open()))
published_cv = json.loads(Path("apps/web/static/data/neo/validation.json").read_text())[
    "cv"
]
lookup = {str(x["key"]): float(x["D_ratio_psf"]) for x in raw_cv}
out["cv_transcription"] = {
    "n": len(published_cv),
    "ratios_matching_retained_source": int(
        sum(np.isclose(round(lookup[x["key"]], 3), x["D_ratio"]) for x in published_cv)
    ),
}
a = csv(R / "injection_recovery.csv")
sel = (a["snr_detect"] >= 5) & (a["chi2"] < 50)
out["retained_injections"] = {}
for label, keep in [
    ("joint_detection_rule", sel),
    ("joint_rule_no_core", sel & (a["n_core"] == 0)),
    ("joint_rule_two_core", sel & (a["n_core"] >= 2)),
]:
    s = a[keep]
    out["retained_injections"][label] = {
        "n": len(s),
        "ratio_percentiles": np.percentile(s["ratio"], [16, 50, 84]).tolist()
        if len(s)
        else [],
        "one_sigma_pull_coverage": float((np.abs(s["pull_tot"]) <= 1).mean())
        if len(s)
        else None,
    }
s = csv(R / "wise-0855_deblended.csv")
s = s[np.isfinite(s["f"]) & (s["e"] > 0)]
rs = csv(R / "wise_w2_rsr.csv")
lw, tw = rs["lam_um"], rs["rsr"]
b = np.arange(3.8, 5.06, 0.05)
cen = []
val = []
err = []
for l0, l1 in zip(b[:-1], b[1:]):
    x = s[(s["lam"] >= l0) & (s["lam"] < l1)]
    if len(x) >= 2:
        w = 1 / x["e"] ** 2
        cen.append(x["lam"].mean())
        val.append(np.sum(w * x["f"]) / np.sum(w))
        err.append(1 / np.sqrt(w.sum()))
y = np.interp(lw, cen, val)
weight = tw / lw**2
den = np.trapezoid(weight, lw)
flux = lambda y: float(np.trapezoid(y * weight, lw) / den)
base = flux(y)
none = y.copy()
none[lw > 5] = 0
double = y.copy()
double[lw > 5] *= 2
out["wise0855_W2_tail_sensitivity"] = {
    "baseline_mJy": base,
    "zero_unobserved_tail_mJy": flux(none),
    "double_flat_unobserved_tail_mJy": flux(double),
    "quoted_sigma_mJy": 0.02,
    "response_fraction_gt5_um": float(np.trapezoid(weight[lw > 5], lw[lw > 5]) / den),
    "last_supported_bin_um": float(cen[-1]),
    "last_supported_bin_mJy": float(val[-1]),
}
out["speed_copy_diagnostic"] = []
for r, delta in ((3.2, 2.6), (6.3045, 6.19956)):
    tau = 5e5 * r * r
    rho = 3 * 6.15 / 206265 * delta * comets.AU_M
    exact = comets.haser_fraction(
        rho / (850 / np.sqrt(r) * tau)
    ) / comets.haser_fraction(rho / (500 * tau))
    out["speed_copy_diagnostic"].append(
        {
            "r_au": r,
            "baseline_km_s": float(0.85 / np.sqrt(r)),
            "ratio_if_constant_half_km_s_small_aperture": float(
                0.5 / (0.85 / np.sqrt(r))
            ),
            "ratio_if_constant_half_km_s_exact_haser": exact,
            "ratio_if_half_coefficient_small_aperture": 0.5 / 0.85,
        }
    )
target = json.loads(Path("apps/web/static/data/targets.json").read_text())["targets"][0]
shifts = []
for month in range(1, 13):
    t = Time(f"2026-{month:02d}-15", scale="utc")
    ra, dec = ephem.propagate(
        target["ra_j2000"],
        target["dec_j2000"],
        target["pmra_masyr"],
        target["pmdec_masyr"],
        2000.0,
        t.mjd,
        target["plx_mas"],
    )
    c = SkyCoord(ra * u.deg, dec * u.deg, distance=(1000 / target["plx_mas"]) * u.pc)
    xyz = (
        c.cartesian.xyz.to(u.au).value
        - get_body_barycentric("earth", t.tdb).xyz.to(u.au).value
    )
    app = SkyCoord(
        x=xyz[0] * u.au,
        y=xyz[1] * u.au,
        z=xyz[2] * u.au,
        representation_type="cartesian",
    )
    shifts.append(float(c.separation(app).to_value(u.arcsec)))
out["barnard_observer_parallax_omitted"] = {
    "max_2026_shift_arcsec": max(shifts),
    "max_native_pixels": max(shifts) / 6.15,
}
d = csv(Path("data/derived/comets/3I_aug2025_D5_skysub.csv"))
d = d[d["f3_jy"] != 0]
fit = comets.fit_co2_rate(
    d["lam_um"], d["bw_um"], d["f3_jy"], d["e3_jy"], d["r"], d["delta"]
)
out["golden_CO2_recomputed"] = {
    "q_s_1": fit.q,
    "statistical_error": fit.statistical_error,
    "chi2_red": fit.chi2_red,
    "temperature_K": fit.temperature_k,
    "extra_width_um": fit.extra_width_um,
    "n_points": len(d),
}
print(json.dumps(out, indent=2))
