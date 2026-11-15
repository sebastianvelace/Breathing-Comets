"""Optional retained-research diagnostic; source files are never modified."""

import csv, json, numpy as np
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--research-root", required=True, type=Path)
args = parser.parse_args()
R = args.research_root / "data/derived"
read = lambda p: list(csv.DictReader(p.open()))
target = read(R / "eps-indi-b_astrometry.csv")
reference = json.loads((R / "eps-indi-b_astrometry.json").read_text())["ref"]
groups = {}
for path in sorted((R / "astrometry_controls").glob("ctrl-*_astrometry.csv")):
    for row in read(path):
        if row["used"].lower() == "true":
            groups.setdefault((row["obs_id"], int(row["det"])), []).append(row)
rows = []
for row in target:
    controls = groups.get((row["obs_id"], int(row["det"])), [])
    if len(controls) >= 3:
        x = {
            k: float(row[k])
            for k in ["det", "mjd", "tyr", "ra_res", "de_res", "sig_as", "pa", "pd"]
        }
        x["ra_res"] -= np.mean([float(c["ra_res"]) for c in controls])
        x["de_res"] -= np.mean([float(c["de_res"]) for c in controls])
        x["sig_as"] = np.hypot(
            x["sig_as"],
            np.mean([float(c["sig_as"]) for c in controls]) / np.sqrt(len(controls)),
        )
        rows.append(x)
dets = sorted({r["det"] for r in rows})
n = len(rows)
design = np.zeros((2 * n, 2 * len(dets) + 3))
y = np.r_[[r["ra_res"] for r in rows], [r["de_res"] for r in rows]]
sig = np.array([r["sig_as"] * 1000 for r in rows] * 2)
for i, r in enumerate(rows):
    k = dets.index(r["det"])
    design[i, 2 * k] = 1
    design[n + i, 2 * k + 1] = 1
    design[i, -3] = r["tyr"] - 2026
    design[n + i, -2] = r["tyr"] - 2026
    design[i, -1] = r["pa"]
    design[n + i, -1] = r["pd"]
keep = np.ones(n, bool)
for _ in range(5):
    k = np.r_[keep, keep]
    beta = np.linalg.lstsq(design[k] / sig[k, None], y[k] / sig[k], rcond=None)[0]
    z = (y - design @ beta) / sig
    chi = np.hypot(z[:n], z[n:])
    scale = np.median(chi) / 1.1774
    keep = chi < 4 * scale
k = np.r_[keep, keep]
beta = np.linalg.lstsq(design[k] / sig[k, None], y[k] / sig[k], rcond=None)[0]
chosen = np.flatnonzero(keep)
times = np.array([r["mjd"] for r in rows])[chosen]
order = np.argsort(times)
labels = np.empty(len(times), int)
labels[order] = np.cumsum(np.r_[False, np.diff(times[order]) > 5])
visits = np.unique(labels)
rng = np.random.default_rng(0)
solutions = []
for _ in range(1000):
    draw = rng.choice(visits, len(visits))
    idx = np.concatenate([chosen[labels == v] for v in draw])
    if len(np.unique(draw)) < 4 or set(rows[i]["det"] for i in idx) != set(dets):
        continue
    both = np.r_[idx, n + idx]
    fit = np.linalg.lstsq(
        design[both] / sig[both, None], y[both] / sig[both], rcond=None
    )[0]
    solutions.append(fit[-3:])
b = np.array(solutions)
out = {
    "source": "retained centroids, independent weighted linear solve; no image remeasurement",
    "n_used": int(keep.sum()),
    "n_visits": len(visits),
    "bootstrap_draws_used": len(b),
    "parallax_mas": float(beta[-1] * reference["plx"]),
    "pmra_mas_yr": float(reference["pmra"] + beta[-3]),
    "pmdec_mas_yr": float(reference["pmdec"] + beta[-2]),
    "parallax_visit_bootstrap_half_16_84_mas": float(
        np.diff(np.percentile(b[:, 2], [16, 84]))[0] / 2 * reference["plx"]
    ),
}
print(json.dumps(out, indent=2))
