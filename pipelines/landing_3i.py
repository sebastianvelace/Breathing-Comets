"""Render the 3I/ATLAS landing plates and write ``/data/comets/3i-atlas/landing.json``.

Inputs (already in the product): the two tracked D5 stacks in
``apps/web/static/data/comets/3i-atlas/`` and ``comets/index.json`` (exported by
``pipelines/export_comets.py``). Nothing is recalculated and no gas map is made:
the plates are real SPHEREx frames centred on the Horizons position, rendered
with the stack's own ``stretch_hint`` (same mapping as the Explorer), OVERFLOW
white before NaN, north up, pixels not resampled.

The hero uses the August 2025 stack because it carries the validated Q(CO2).
Frames covering less than 95% of the field are not shown.

Usage: ``python pipelines/landing_3i.py``
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import landing_media
from landing_media import ROOT, read_stack, save, stretch_rgb, valid_fraction

DATA = ROOT / "apps/web/static/data/comets"
STACK = DATA / "3i-atlas/D5-2025-08.spxf.gz"
OUT_JSON = DATA / "3i-atlas/landing.json"
CO2_CENTER_UM = 4.26
CREDITS = [
    "SPHEREx: NASA/JPL-Caltech/IRSA (DR1 + QR3, L2 l2b-v27)",
    "Ephemeris: NASA/JPL Horizons (SPHEREx observer)",
]


def main():
    landing_media.OUT.mkdir(parents=True, exist_ok=True)
    atlas = json.loads((DATA / "index.json").read_text())
    header, frames = read_stack(STACK)
    lo, hi = header["stretch_hint"]["lo"], header["stretch_hint"]["hi"]
    shown = [i for i in range(len(frames)) if valid_fraction(*frames[i]) >= 0.95]
    poster_k = min(shown, key=lambda i: abs(header["frames"][i]["lam_um"] - CO2_CENTER_UM))

    def plate(i, name):
        meta = header["frames"][i]
        image = save(stretch_rgb(*frames[i], lo, hi), name)
        return meta, image

    epochs = []
    for i in shown:
        meta, image = plate(i, f"3i-d5-2025-08-k{i}.webp")
        epochs.append({"image": image["src"], "width": image["width"], "height": image["height"],
                       "mjd": meta["mjd"], "lambda_um": meta["lam_um"], "obs_id": meta["obs_id"],
                       "credit": CREDITS[0]})
    poster_meta, poster = plate(poster_k, "3i-d5-2025-08-poster.webp")

    by_slug = {c["slug"]: c for c in atlas["comets"]}
    dec = by_slug["3i-atlas"]
    aug = next(v for v in atlas["validation"] if v["id"] == "3i-atlas_co2_2025-08")
    measurements = [
        {"label": "Q(CO₂), August 2025", "label_es": "Q(CO₂), agosto de 2025",
         "value": aug["measured"], "lo": aug["measured_lo"], "hi": aug["measured_hi"], "unit": "s⁻¹",
         "caveat": f"Statistical error ±{aug['stat_err']:.1e}; χ²ᵣ {aug['chi2_red']}. The 16–84% range comes from "
                   "the research notes and Q scales with the assumed outflow speed (about −40% for 0.50 instead of "
                   "0.85 r_h^−0.5 km/s).",
         "caveat_es": f"Error estadístico ±{aug['stat_err']:.1e}; χ²ᵣ {aug['chi2_red']}. El intervalo 16–84% sale de las "
                      "notas de investigación y Q es proporcional a la velocidad de salida supuesta (cerca de −40% "
                      "con 0.50 en lugar de 0.85 r_h^−0.5 km/s).",
         "source": "Research fit of the CO₂ ν₃ band (research/11_band_physical.py), reproduced 2026-11-14"},
        {"label": "Q(CO₂), December 2025", "label_es": "Q(CO₂), diciembre de 2025",
         "value": dec["co2"]["q50"], "lo": dec["co2"]["q16"], "hi": dec["co2"]["q84"], "unit": "s⁻¹",
         "caveat": f"Band present (S/N {dec['co2']['snr_det']:.1f}) but the model fits poorly (χ²ᵣ {dec['co2']['chi2_red']:.0f}): "
                   "Q is not trusted at its quoted precision.",
         "caveat_es": f"Hay banda (S/N {dec['co2']['snr_det']:.1f}) pero el modelo ajusta mal (χ²ᵣ {dec['co2']['chi2_red']:.0f}): "
                      "Q no es fiable con la precisión indicada.",
         "source": "Comet census (co2_census_physical.csv)"},
    ]
    validation = []
    for v in atlas["validation"]:
        validation.append({
            "species": f"{v['comet']} · {'CO₂' if v['species'] == 'CO2' else v['species']} · {v['epoch']}",
            "measured": v["measured"], "published_lo": v["published_lo"], "published_hi": v["published_hi"],
            "unit": "s⁻¹",
            "caveat": f"χ²ᵣ {v['chi2_red']:.1f}. Consistent with the published range; not an independent confirmation.",
            "caveat_es": f"χ²ᵣ {v['chi2_red']:.1f}. Consistente con el intervalo publicado; no es una confirmación independiente.",
            "source": v["source"]})

    packet = {
        "target": "3I/ATLAS",
        "plates": {"poster": poster["src"], "pixel_arcsec": header["grid"]["pixel_arcsec"],
                   "nx": header["grid"]["nx"], "north_up": header["grid"]["north_up"], "epochs": epochs},
        "measurements": measurements, "validation": validation, "credits": CREDITS,
        "generated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ"),
        "stack": {"file": STACK.name, "stretch": {"lo": lo, "hi": hi, "map": "asinh(20x)/asinh(20)"},
                  "poster": {"obs_id": poster_meta["obs_id"], "lambda_um": poster_meta["lam_um"], "mjd": poster_meta["mjd"]}},
    }
    OUT_JSON.write_text(json.dumps(packet, indent=1, allow_nan=False, ensure_ascii=False))
    print(f"wrote {OUT_JSON.relative_to(ROOT)}: {len(epochs)} epochs, poster {poster_meta['obs_id']} "
          f"at {poster_meta['lam_um']:.3f} um")


if __name__ == "__main__":
    main()
