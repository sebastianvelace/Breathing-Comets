"""Export the data behind the comet detail pages (3I/ATLAS and 29P).

Writes ``apps/web/static/data/comets/<slug>.json`` and lossless WebP plates in
``apps/web/static/media/comets/``. Plates are real tracked SPHEREx frames from the
stacks stored in ``static/data/comets/<slug>/`` rendered with each stack's own
``stretch_hint``; frames are ordered by wavelength. Spectra reproduce the census
filters (D5 sky-subtracted, 3 px, 3.85-4.42 um, finite, non-zero flux, positive
error; D6 for the CO window). Fluxes are converted from Jy to mJy.

Usage: ``python pipelines/comet_pages.py``
"""

import csv
import json
import math
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import landing_media
from landing_media import ROOT, read_stack, save, stretch_rgb, valid_fraction

DATA = ROOT / "apps/web/static/data/comets"
SPECTRA = ROOT / "data/derived/comets/spectra"
MEDIA = ROOT / "apps/web/static/media/comets"
CO2_BAND = (4.21, 4.31)
CO_WINDOW = (4.60, 4.74)
CREDIT = "SPHEREx: NASA/JPL-Caltech/IRSA (DR1 + QR3, L2 l2b-v27); ephemeris: NASA/JPL Horizons"

COMETS = {
    "3i-atlas": {"name": "3I/ATLAS", "census_name": "3I/ATLAS", "track": "2025 N1",
                 "epochs": [("2025-08", "D5-2025-08.spxf.gz", "3I_aug2025_D5_skysub.csv", None),
                            ("2025-12", "D5-2025-12.spxf.gz", "3I_ATLAS.skysub.csv.txt", "3I_ATLAS.D6.csv.txt")]},
    "29p-schwassmann-wachmann": {"name": "29P/Schwassmann-Wachmann", "census_name": "29P/Schwassmann-Wachmann",
                                  "track": "90000393 (Horizons id of 29P)",
                                  "epochs": [("2025-12", "D5-2025-12.spxf.gz", "29P_Schwassmann-Wachmann.skysub.csv.txt",
                                "29P_Schwassmann-Wachmann.D6.csv.txt")]},
}


def num(v):
    x = float(v)
    return x if math.isfinite(x) else None


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def d5_spectrum(name):
    out = []
    for r in read_csv(SPECTRA / name):
        f, e, lam = num(r["f3_jy"]), num(r["e3_jy"]), num(r["lam_um"])
        if r["det"] != "D5" or f is None or e is None or lam is None or e <= 0 or f == 0 or not 3.85 <= lam <= 4.42:
            continue
        out.append({"lam": lam, "bw": num(r["bw_um"]), "f": f * 1e3, "e": e * 1e3, "mjd": num(r["t_mid"]),
                    "obs_id": r["obs_id"], "r_au": num(r["r"]), "delta_au": num(r["delta"])})
    return sorted(out, key=lambda p: p["lam"])


def d6_spectrum(name):
    out = []
    for r in read_csv(SPECTRA / name):
        f, e, lam = num(r["f"]), num(r["e"]), num(r["lam_um"])
        if f is None or e is None or lam is None or e <= 0:
            continue
        out.append({"lam": lam, "bw": num(r["bw_um"]), "f": f * 1e3, "e": e * 1e3})
    return sorted(out, key=lambda p: p["lam"])


def main():
    MEDIA.mkdir(parents=True, exist_ok=True)
    landing_media.OUT = MEDIA
    atlas = json.loads((DATA / "index.json").read_text())
    by_slug = {c["slug"]: c for c in atlas["comets"]}
    for slug, spec in COMETS.items():
        epochs = []
        spectra = {}
        for label, filename, d5_file, d6_file in spec["epochs"]:
            header, frames = read_stack(DATA / slug / filename)
            lo, hi = header["stretch_hint"]["lo"], header["stretch_hint"]["hi"]
            order = sorted((i for i in range(len(frames)) if valid_fraction(*frames[i]) >= 0.95),
                           key=lambda i: header["frames"][i]["lam_um"])
            shown = []
            for i in order:
                meta = header["frames"][i]
                image = save(stretch_rgb(*frames[i], lo, hi), f"{slug}-{label}-k{i}.webp")
                shown.append({"src": image["src"].replace("/media/landing/", "/media/comets/"),
                              "width": image["width"], "height": image["height"], "obs_id": meta["obs_id"],
                              "mjd": meta["mjd"], "date": meta["date"], "lam_um": meta["lam_um"], "bw_um": meta["bw_um"],
                              "in_co2_band": CO2_BAND[0] <= meta["lam_um"] <= CO2_BAND[1]})
            spectra[label] = {"d5": d5_spectrum(d5_file), "d6": d6_spectrum(d6_file) if d6_file else None,
                              "source": [f"data/derived/comets/spectra/{n}" for n in (d5_file, d6_file) if n]}
            epochs.append({"id": label, "stack": f"/data/comets/{slug}/{filename}", "det": header["det"],
                           "grid": {"nx": header["grid"]["nx"], "pixel_arcsec": header["grid"]["pixel_arcsec"],
                                    "north_up": header["grid"]["north_up"]},
                           "stretch": {"lo": lo, "hi": hi, "map": "asinh(20x)/asinh(20)"},
                           "n_frames_stack": len(frames), "frames": shown})
        census = by_slug[slug]
        out = {
            "slug": slug, "name": spec["name"], "track": spec["track"],
            "generated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ"), "generator": "pipelines/comet_pages.py",
            "credit": CREDIT, "co2_band_um": list(CO2_BAND), "co_window_um": list(CO_WINDOW),
            "epochs": epochs,
            "spectrum": {"by_epoch": spectra,
                         "filter": "D5 sky-subtracted, 3 px aperture, 3.85-4.42 um, finite non-zero flux, positive error",
                         "units": "mJy"},
            "census": {"r_au": census["r_au"], "delta_au": census["delta_au"], "co2": census["co2"],
                       "co": census["co"], "h2o": census["h2o"], "aperture": census["aperture"]},
            "validation": [v for v in atlas["validation"] if v["comet"] == spec["name"]],
        }
        (DATA / f"{slug}.json").write_text(json.dumps(out, indent=1, allow_nan=False, ensure_ascii=False))
        print(slug, {e["id"]: len(e["frames"]) for e in epochs}, "spectra", {k: (len(v["d5"]), len(v["d6"] or [])) for k, v in spectra.items()})


if __name__ == "__main__":
    main()
