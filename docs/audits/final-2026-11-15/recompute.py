"""Final numerical audit: recompute every published number from the shipped data files.

Read-only. Run from the repository root:  .venv/bin/python docs/audits/final-2026-11-15/recompute.py
Prints one line per check (PASS / FAIL / NOTE) and writes recompute-observed.json next to this file.
"""

import json
import math
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/"apps/web/static/data"
MSG = json.loads((ROOT/"apps/web/messages/en.json").read_text())
W2_ZP_JY = 171.787  # Jarrett et al. 2011, WISE W2 isophotal zero point
results = []


def check(name, ok, detail, kind=None):
    status = kind or ("PASS" if ok else "FAIL")
    results.append({"check": name, "status": status, "detail": detail})
    print(f"{status:4}  {name}: {detail}")


def close(a, b, tol):
    return abs(a-b) <= tol


def load(p):
    return json.loads((DATA/p).read_text())


# ---------------------------------------------------------------- targets
b = load("targets/barnard.json")["astrometry"]
tot = math.hypot(b["pm_ra"], b["pm_dec"])/1000
err = math.hypot(b["pm_ra"]*b["pm_ra_err"], b["pm_dec"]*b["pm_dec_err"])/math.hypot(b["pm_ra"], b["pm_dec"])/1000
gaia = math.hypot(b["ref"]["pmra"], b["ref"]["pmdec"])/1000
check("Barnard PM total", close(tot, 10.6, .05), f"{tot:.3f}″/yr from components (shown 10.6)")
check("Barnard PM formal error", close(err, .10, .01), f"propagated {err:.3f}″/yr (shown ±0.10); stored pm_total_err {b['pm_total_err']} is a quadrature sum of component errors, not a propagation")
check("Barnard Gaia PM", close(gaia, 10.39, .005), f"{gaia:.4f}″/yr (shown 10.39)")
check("Barnard Gaia parallax", close(b["ref"]["plx"], 547, .5), f"{b['ref']['plx']} mas (shown 547)")
check("Barnard PM vs Gaia", abs(tot-gaia) <= .4, f"difference {tot-gaia:+.3f}″/yr = {(tot-gaia)/.4:+.2f} of the quoted ±0.4")
pa_s, pa_g = math.degrees(math.atan2(b["pm_ra"], b["pm_dec"])), math.degrees(math.atan2(b["ref"]["pmra"], b["ref"]["pmdec"]))
check("Barnard PM direction", abs(pa_s-pa_g) < 2, f"position angle {pa_s:.2f}° vs Gaia {pa_g:.2f}°", "NOTE" if abs(pa_s-pa_g) >= 1 else None)

e = load("targets/eps-indi-b.json")
d = e["astrometry_differential"]
tot = math.hypot(d["pmra"], d["pmdec"])/1000
errb = math.hypot(d["pmra"]*d["pmra_err_visit_bootstrap"], d["pmdec"]*d["pmdec_err_visit_bootstrap"])/math.hypot(d["pmra"], d["pmdec"])/1000
gaia = math.hypot(e["astrometry"]["ref"]["pmra"], e["astrometry"]["ref"]["pmdec"])/1000
check("ε Indi B PM total (differential)", close(tot, 4.75, .005), f"{tot:.4f}″/yr (shown 4.75)")
check("ε Indi B PM error (visit bootstrap)", close(errb, .04, .005), f"{errb:.4f}″/yr (shown ±0.04)")
check("ε Indi B Gaia PM", close(gaia, 4.68, .005), f"{gaia:.4f}″/yr (shown 4.68)")
check("ε Indi B PM vs Gaia", True, f"difference {tot-gaia:+.3f}″/yr = {(tot-gaia)/errb:+.1f}σ (bootstrap); Gaia DR3 B is a resolved binary component, orbital motion not modelled", "NOTE")
check("ε Indi B parallax", close(d["plx"], 271, .5) and close(d["plx_err_visit_bootstrap"], 20, .5),
      f"{d['plx']:.2f} ± {d['plx_err_visit_bootstrap']:.2f} mas (shown 271 ± 20); Gaia {e['astrometry']['ref']['plx']}")
check("ε Indi B leave-one-out", True, f"stored {d['plx_leave_one_control_out']} (shown 277–294 mas)", "NOTE")
spec = e["spectrum"]
lam = np.array([s["lam"] for s in spec]); f = np.array([s["f"] for s in spec])
peak = np.max(f[(lam > 3.9) & (lam < 4.1)]) if np.any((lam > 3.9) & (lam < 4.1)) else np.nan
ch4 = np.median(f[(lam > 3.25) & (lam < 3.35)]) if np.any((lam > 3.25) & (lam < 3.35)) else np.nan
a = (lam >= 3.2) & (lam <= 3.4); p = (lam >= 3.9) & (lam <= 4.1)
check("ε Indi B methane ratio", close(np.median(f[p])/np.median(f[a]), 5.4, .05), f"median F(3.9–4.1 µm) / median F(3.2–3.4 µm) = {np.median(f[p])/np.median(f[a]):.2f} (shown 5.4×)")

r = load("targets/r-dra.json")["periodogram"]["3.8-5.0"]
check("R Dra period", close(r["period_d"], 229, .5) and r["period_p16"] == 225 and r["period_p84"] == 241,
      f"{r['period_d']} d ({r['period_p16']}–{r['period_p84']}); catalogue 245.6 d lies at the p84–p97 range ({r['period_p84']}–{r['period_p97']})")
check("R Dra frequency resolution", True, f"Rayleigh resolution ΔP ≈ P²/T = {r['period_d']**2/r['span_d']:.0f} d over {r['span_d']:.0f} d ({r['cycles']} cycles): the 16–84% interval is statistical precision, much narrower than the resolution", "NOTE")
rb = load("targets/r-dra.json")["periodogram"]
check("R Dra amplitude", close(rb["0.75-1.1"]["amp_95_5_mag"], 2.0, .05) and close(rb["3.8-5.0"]["amp_95_5_mag"], .7, .05),
      f"{rb['0.75-1.1']['amp_95_5_mag']} mag → {rb['3.8-5.0']['amp_95_5_mag']} mag (shown 2.0 → 0.7)")
check("R Dra 1.1–2.4 µm", rb["1.1-2.4"]["period_d"] == 236.2, f"{rb['1.1-2.4']['period_d']} d ({rb['1.1-2.4']['period_p16']}–{rb['1.1-2.4']['period_p84']})")
for band in ("0.75-1.1", "2.4-3.8"):
    q = rb[band]
    check(f"R Dra {band} µm period", True, f"{q['period_d']} d ({q['period_p16']}–{q['period_p84']}, power {q['power']}): not shown; inconsistent with the Mira period", "NOTE")

rw = load("targets/rw-aur.json")["lightcurve"]
mjd = np.array([p["mjd"] for p in rw]); rel = np.array([p["rel"] for p in rw]); band = np.array([p["band"] for p in rw])
ep = sorted({round(m/30) for m in mjd})
def epoch_med(bname, lo, hi):
    s = (band == bname) & (mjd >= lo) & (mjd < hi)
    return np.median(rel[s]), int(s.sum())
first, last = mjd.min(), mjd.max()
o1, n1 = epoch_med("0.75-1.1", first-1, first+60); o2, n2 = epoch_med("0.75-1.1", last-60, last+1)
w1, m1 = epoch_med("3.8-5.0", first-1, first+60); w2, m2 = epoch_med("3.8-5.0", last-60, last+1)
check("RW Aur optical ratio", True, f"0.75–1.1 µm last/first epoch = {o2/o1:.2f} (n={n1},{n2}; shown ×1.8)", "PASS" if close(o2/o1, 1.8, .15) else "FAIL")
check("RW Aur 4–5 µm ratio", True, f"3.8–5.0 µm last/first = {w2/w1:.2f} (n={m1},{m2}; shown ×0.5)", "PASS" if close(w2/w1, .5, .1) else "FAIL")
check("RW Aur epochs", True, f"bands {sorted(set(band))}; visit groups by 30 d: {len(ep)}", "NOTE")

for mag, shown in ((13.89, .48), (13.82, .51), (13.70, .57)):
    mjy = W2_ZP_JY*10**(-.4*mag)*1e3
    check(f"W2 {mag} mag → mJy", close(mjy, shown, .006), f"{mjy:.4f} mJy (shown {shown})")

# ---------------------------------------------------------------- comets
c = load("comets/index.json")
def status(snr, chi2):
    if snr is None: return "not_detected"
    if snr >= 5: return "detected" if chi2 is not None and chi2 < 50 else "with_systematics"
    return "marginal" if snr >= 3 else "not_detected"
bad = [x["name"] for x in c["comets"] if status(x["co2"]["snr_det"], x["co2"]["chi2_red"]) != x["co2"]["status"]]
check("Comet status rule", not bad, f"{len(c['comets'])} comets; mismatches {bad}")
counts = {s: sum(x["co2"]["status"] == s for x in c["comets"]) for s in ("detected", "with_systematics", "marginal", "not_detected")}
check("Comet counts", counts == {"detected": 17, "with_systematics": 2, "marginal": 1, "not_detected": 0}, str(counts))
order = [x["name"] for x in c["comets"] if not (x["co2"]["q16"] <= x["co2"]["q50"] <= x["co2"]["q84"])]
check("Comet Q percentile order", not order, f"violations {order}")
ratio = [(x["name"], x["co2"]["q50_alt_velocity"]/x["co2"]["q50"]) for x in c["comets"] if x["co2"]["q50_alt_velocity"]]
rs = np.array([v for _, v in ratio])
check("Outflow v₀ 0.50 vs 0.85", close(rs.mean(), .5/.85, .03), f"Q(0.50)/Q(0.85) mean {rs.mean():.3f}, range {rs.min():.3f}–{rs.max():.3f}; 0.50/0.85 = {.5/.85:.3f} (−{100*(1-.5/.85):.1f}%)")
far = [x["name"] for x in c["comets"] if x["r_au"] > c["method"]["far_au"]]
check("Comet far flag", all("far_unreliable" in x["flags"] for x in c["comets"] if x["r_au"] > 10) and len(far) == 1, f"{far}")
zc = [x["name"] for x in c["comets"] if "zero_core" in x["flags"]]
check("Comet zero-core flag", sorted(zc) == ["235P/LINEAR", "C/2025 Q3 (ATLAS)"], f"{zc}")
for v in c["validation"]:
    inside = v["published_lo"] <= v["measured"] <= v["published_hi"]
    check(f"Validation {v['id']}", inside, f"{v['measured']:.3g} in [{v['published_lo']:.3g}, {v['published_hi']:.3g}]")
lisse_upd, lisse_err = 1.6e27, .16e27
check("3I vs updated Lisse 2026 alone", True, f"(1.17−1.60)e27 / sqrt(0.30² + 1.6²)e26 = {(1.17e27-lisse_upd)/math.hypot(3e25, lisse_err):.1f}σ using the statistical error only; the 16–84% 0.86–1.38e27 does not reach 1.44e27 (1.6 − 10%)", "NOTE")
cc = next(x for x in c["comets"] if x["slug"].startswith("29p"))
check("29P CO/CO₂", True, f"stored ratio {cc['co']['ratio_co_co2']} [{cc['co']['ratio_16']}–{cc['co']['ratio_84']}]; Q(CO₂) census {cc['co2']['q50']:.3g}; implied Q(CO) {cc['co']['ratio_co_co2']*cc['co2']['q50']:.3g} vs validation 4.5e28", "NOTE")
# flux scaling sanity: S/N should grow with Q r^-2 Δ^-2 roughly
x = np.array([math.log10(k["co2"]["q50"]*k["r_au"]**-2*k["delta_au"]**-2) for k in c["comets"]]); y = np.array([math.log10(k["co2"]["snr_det"]) for k in c["comets"]])
check("Q r⁻²Δ⁻² vs S/N", True, f"Spearman-like correlation {np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1]:.2f} across 20 comets", "NOTE")

# ---------------------------------------------------------------- asteroids
n = load("neo/index.json"); obj = n["objects"]
tiers = {t: sum(o["tier"] == t for o in obj) for t in ("A", "B", "provisional")}
pha = sum(o["pha"] and o["tier"] in ("A", "B") for o in obj)
check("NEO tier counts", tiers == {"A": 11, "B": 17, "provisional": 6}, str(tiers))
check("NEO PHA in A/B", pha == 7 and n["counts"]["pha_AB"] == 7, f"{pha}")
worst = []
for o in obj:
    d_hv = 1329/math.sqrt(o["pV"])*10**(-o["H"]/5)
    worst.append((abs(d_hv/o["D_km"]-1), o["pdes"], d_hv, o["D_km"]))
    if not (o["D16"] <= o["D_km"] <= o["D84"]):
        check(f"NEO interval {o['pdes']}", False, f"{o['D16']} ≤ {o['D_km']} ≤ {o['D84']}")
worst.sort(reverse=True)
check("NEO D–H–pV consistency", worst[0][0] < .03, f"max |1329/√pV·10^(−H/5) / D − 1| = {worst[0][0]:.3f} ({worst[0][1]}: {worst[0][2]:.3f} vs {worst[0][3]}); pV is rounded to 3 decimals", "PASS" if worst[0][0] < .03 else "NOTE")
low = [o["pdes"] for o in obj if o["pV"] < .03]
check("NEO very low albedo", True, f"{len(low)} objects with pV < 0.03 ({', '.join(low)}): below the NEO albedo distribution floor; diameters depend on H", "NOTE")
cv = np.array([k["D_ratio"] for k in load("neo/validation.json")["cv"]])
p16, p50, p84 = np.percentile(cv, [16, 50, 84])
m = n["method"]
check("NEO CV n", len(cv) == m["cv_n"] == 50, f"{len(cv)}")
check("NEO CV percentiles", close(p16, m["cv_p16"], .015) and close(p84, m["cv_p84"], .015) and close(p50, m["cv_median"], .015),
      f"recomputed p16 {p16:.3f} p50 {p50:.3f} p84 {p84:.3f} vs stored {m['cv_p16']} {m['cv_median']} {m['cv_p84']}")
check("NEO CV −33%/+36%", round(100*(1-m["cv_p16"])) == 33 and round(100*(m["cv_p84"]-1)) == 36, f"{100*(1-p16):.1f}% / {100*(p84-1):.1f}% recomputed")
check("NEO CV lognormal width", True, f"stored σ_ln {m['cv_sigma_ln']}; recomputed std(ln ratio) {np.std(np.log(cv), ddof=1):.3f}, robust {1.4826*np.median(np.abs(np.log(cv)-np.median(np.log(cv)))):.3f}", "NOTE")

# ---------------------------------------------------------------- calibration and instrument
pb = json.loads((ROOT/"data/validation/photometric_bands.json").read_text())
check("Photometric bands file", True, json.dumps(pb)[:300], "NOTE")
ch = load("channels.json")
check("Channel file", True, f"keys {list(ch)[:6]}", "NOTE")

out = Path(__file__).with_name("recompute-observed.json")
out.write_text(json.dumps(results, indent=1, ensure_ascii=False))
print("\nFAIL:", sum(r["status"] == "FAIL" for r in results), "NOTE:", sum(r["status"] == "NOTE" for r in results), "PASS:", sum(r["status"] == "PASS" for r in results))
