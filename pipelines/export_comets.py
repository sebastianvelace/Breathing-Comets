"""Export the comet atlas to ``apps/web/static/data/comets/index.json``.

Every number is copied from the retained research CSVs in ``data/derived/comets/``
(never typed). Status rules follow BUILD sections 8.9 and 10.6:

* ``detected``          S/N_det >= 5 and chi2_red < 50 (0/79 false positives on nulls)
* ``with_systematics``  S/N_det >= 5 but chi2_red >= 50: a band is present, the model is not trusted
* ``marginal``          3 <= S/N_det < 5
* ``not_detected``      S/N_det < 3

Usage: ``python pipelines/export_comets.py``
"""

import csv
import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/derived/comets"
OUT = ROOT / "apps/web/static/data/comets/index.json"

CO_CLASS = {"sin cobertura": "no_coverage", "sin datos D6": "no_data", "límite superior": "upper_limit",
            "candidato": "candidate", "detección robusta": "robust_detection"}
H2O_CLASS = {"sin cobertura": "no_coverage", "límite superior": "upper_limit", "detección": "detection"}
FAR_AU = 10.0  # beyond this the CO2 band flux is too small for a trustworthy Q (BUILD 10.6 legend)


def rows(name):
    with open(SRC / name, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def num(value):
    if value in ("", None):
        return None
    x = float(value)
    return x if math.isfinite(x) else None


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def designation_type(name):
    if re.match(r"^\d+I/", name):
        return "interstellar"
    if re.match(r"^(\d+P/|P/)", name):
        return "periodic"
    return "non_periodic"


def status(snr, chi2):
    if snr is None:
        return "not_detected"
    if snr >= 5:
        return "detected" if chi2 is not None and chi2 < 50 else "with_systematics"
    return "marginal" if snr >= 3 else "not_detected"


def main():
    co = {r["name"]: r for r in rows("co_census_final.csv")}
    h2o = {r["name"]: r for r in rows("h2o_census.csv")}
    aperture = {r["name"]: r for r in rows("q_vs_aperture.csv")}
    comets = []
    for r in rows("co2_census_physical.csv"):
        name = r["name"]
        snr, chi2, r_au = num(r["snr_detect"]), num(r["chi2_phys"]), num(r["r_au"])
        q = {k: num(r[c]) for k, c in (("q16", "QA_16"), ("q50", "QA_50"), ("q84", "QA_84"))}
        entry = {
            "slug": slug(name), "name": name, "designation_type": designation_type(name),
            "r_au": r_au, "delta_au": num(r["delta_au"]),
            "co2": {**q, "q50_alt_tau_g": num(r["QB_50"]), "q50_alt_velocity": num(r["QC_50"]),
                    "sys_tau_g": num(r["sys_tau_g"]), "sys_v": num(r["sys_v"]),
                    "snr_det": snr, "flux_rel_err": num(r["flux_rel_err"]), "n_core": int(float(r["n_core"])),
                    "chi2_red": chi2, "t_rot_k": num(r["T_rot"]), "n_exposures": int(float(r["n"])),
                    "status": status(snr, chi2)},
            "flags": [],
        }
        if r_au is not None and r_au > FAR_AU:
            entry["flags"].append("far_unreliable")
        c = co.get(name)
        entry["co"] = None if c is None else {
            "class": CO_CLASS[c["clase_CO"]], "q50": num(c["QCO_50"]), "ratio_co_co2": num(c["ratio_50"]),
            "ratio_16": num(c["ratio_16"]), "ratio_84": num(c["ratio_84"]), "ratio_upper_2sigma": num(c["ratio_ul2s"]),
            "snr_med": num(c["snr_med"]), "chi2_red": num(c["chi2_base"])}
        h = h2o.get(name)
        entry["h2o"] = None if h is None else {
            "class": H2O_CLASS[h["clase_H2O"]], "q16": num(h["QH2O_16"]), "q50": num(h["QH2O_50"]),
            "q84": num(h["QH2O_84"]), "upper_2sigma": num(h["QH2O_ul2s"]), "snr": num(h["snr"]),
            "chi2_red": num(h["chi2"]), "co2_h2o": num(h["CO2_H2O_50"])}
        a = aperture.get(name)
        entry["aperture"] = None if a is None else {
            "q_2px": num(a["Q2"]), "q_3px": num(a["Q3"]), "q_5px": num(a["Q5"]), "q_8px": num(a["Q8"]),
            "dlnq_dlnrho": num(a["slope_dlnQ_dlnrho"]), "q8_over_q2": num(a["Q8_over_Q2"])}
        comets.append(entry)
    comets.sort(key=lambda c: c["r_au"])
    by_slug = {c["slug"]: c for c in comets}

    physical = json.loads((SRC / "3i_aug2025_physical.json").read_text())
    reference = json.loads((SRC / "published_reference.json").read_text())["references"]
    best = physical["reproduced"]["best_no_evolution"]
    p29 = by_slug["29p-schwassmann-wachmann"]["co"]
    validation = [
        {"id": "3i-atlas_co2_2025-08", "comet": "3I/ATLAS", "species": "CO2", "epoch": "2025-08",
         "measured": best["q"], "measured_lo": physical["interval_16_84"]["lo"],
         "measured_hi": physical["interval_16_84"]["hi"], "stat_err": best["q_stat_err"],
         "chi2_red": best["chi2_red"], "unit": "s-1",
         "published_lo": reference["3i-atlas_co2_2025-08"]["lo"], "published_hi": reference["3i-atlas_co2_2025-08"]["hi"],
         "source": reference["3i-atlas_co2_2025-08"]["source"],
         "provenance": physical["reproduced"]["command"], "interval_source": physical["interval_16_84"]["source"]},
        {"id": "29p_co_2025-12", "comet": "29P/Schwassmann-Wachmann", "species": "CO", "epoch": "2025-12",
         "measured": p29["q50"], "measured_lo": None, "measured_hi": None, "stat_err": None,
         "chi2_red": p29["chi2_red"], "ratio_co_co2": p29["ratio_co_co2"],
         "ratio_16": p29["ratio_16"], "ratio_84": p29["ratio_84"], "unit": "s-1",
         "published_lo": reference["29p_co_2025-12"]["lo"], "published_hi": reference["29p_co_2025-12"]["hi"],
         "source": reference["29p_co_2025-12"]["source"], "provenance": "co_census_final.csv"},
    ]
    out = {
        "generated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ"),
        "generator": "pipelines/export_comets.py",
        "method": {
            "status_rule": "detected: S/N_det >= 5 and chi2_red < 50; with_systematics: S/N_det >= 5 and chi2_red >= 50; "
                           "marginal: 3 <= S/N_det < 5; not_detected: S/N_det < 3",
            "q_percentiles": "16/50/84 of a 4,000-draw Monte Carlo (flux, +/-5% calibration, +/-5% g, lognormal tau 0.3, lognormal v 0.2)",
            "baseline": "recipe A: g=2.86e-3 s-1 at 1 au, tau=5e5 s, v=0.85 r^-0.5 km/s",
            "far_au": FAR_AU,
            "sources": sorted(p.name for p in SRC.iterdir() if p.suffix == ".csv"),
        },
        "counts": {"comets": len(comets),
                   **{s: sum(c["co2"]["status"] == s for c in comets)
                      for s in ("detected", "with_systematics", "marginal", "not_detected")}},
        "comets": comets,
        "validation": validation,
        "pending": [{"id": "3i-atlas_h2o_2025-08",
                     "reason": "no retained CSV or reproducible script output for the August 2025 H2O fit; the guide cites 4.0e26 against 3.2e26 (Lisse et al. 2026) but it is not exported until re-derived"}],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, allow_nan=False, ensure_ascii=False))
    print(f"wrote {OUT.relative_to(ROOT)}: {out['counts']}")


if __name__ == "__main__":
    main()
