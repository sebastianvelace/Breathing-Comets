"""Render the written submission from shipped product data, without a video draft."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "apps/web/static/data"


def read(path):
    return json.loads((DATA / path).read_text())


def sci(value):
    mantissa, power = f"{value:.3g}".split("e")
    return f"{mantissa} × 10^{int(power)}"


def render():
    neo, atlas, calibration = read("neo/index.json"), read("comets/index.json"), read("calibration.json")
    counts, method = neo["counts"], neo["method"]
    channels = read("channels.json")["channels"]
    validation = atlas["validation"]
    august = next(v for v in validation if v["id"] == "3i-atlas_co2_2025-08")
    co = next(v for v in validation if v["id"] == "29p_co_2025-12")
    pairs = read("neo/validation_diameters.json")["points"]
    size = next(o for o in neo["objects"] if o["pdes"] == "2025 YH5")
    checked = counts["A"] + counts["B"]
    notes = []
    names = {"barnard": "Barnard's Star", "eps-indi-b": "ε Indi B", "wise-0855": "WISE 0855−0714",
             "r-dra": "R Draconis", "rw-aur": "RW Aurigae"}
    for slug, name in names.items():
        target = read(f"targets/{slug}.json")
        text = "; ".join(f"{n['label']}: {n['value']} ({n['ref']})" for n in target["notes"][:2])
        notes.append(f"- **{name}:** {text}. Caveat: {target['caveat']}.")
    checks = "; ".join(f"{v['band']}: {v['ratio']:.3f}" for v in calibration["validation"])
    return f"""# Breathing Comets: a Small-Body Lab for SPHEREx

## High-Level Project Summary

SPHEREx maps the sky in {len(channels)} infrared colors. Breathing Comets turns real mission images into a public time machine: play exposures, blink two dates, compare the sky at matched wavelengths, and click a position for a measured spectrum. Five prepared challenge targets and tracked comet plates remain available when the live API is unavailable. Our Small-Body Lab presents {checked} thermal-size estimates for near-Earth asteroids, including {counts['pha_AB']} with potentially hazardous orbits, plus {counts['provisional']} explicitly provisional estimates. Cross-validation against {method['cv_n']} NEOWISE objects gives −{(1-method['cv_p16'])*100:.0f}%/+{(method['cv_p84']-1)*100:.0f}% dispersion; every size keeps its interval and ±{method['floor_fraction']*100:.0f}% systematic floor. The comet atlas shows emission-band measurements with their detection diagnostics and limitations. English and Spanish interfaces, source credits, a public method page and a reproducible codebase make the evidence available for inspection.

## Project Links

- Product: https://breathingcomets.org
- Source code: https://github.com/sebastianvelace/Breathing-Comets
- Method and limitations: https://breathingcomets.org/method
- Video: supplied separately by the team in the demonstration-video field before submission.

## What the Product Does

### Sky Explorer

Search a prepared target, a stellar name or coordinates. Play actual north-up SPHEREx images on a timeline; blink two dates; or use Diff λ to compare against other visits at compatible wavelengths. Each exposure retains its detector, wavelength, date, observation identifier and source. A shared URL restores the selected field and observation; an embed route is available.

Gaia positions are propagated to the displayed epoch when proper motion is measured. The Lab adds a pixel and quality-flag inspector, links to the original FITS file, forced-ePSF spectra, and an Aladin Lite reference viewer with the real DR1 spectral cube, Gaia and a 2MASS layer. A contextual tour introduces the controls without blocking first use. Prepared packages continue to work without the API; arbitrary queries depend on archive coverage and available external services.

The five targets retain the following measured notes and caveats:

{chr(10).join(notes)}

### Small-Body Lab

The catalog presents {counts['A']} tier-A and {counts['B']} tier-B sizes from {counts['candidates']} candidates, plus {counts['provisional']} provisional entries. No tier-C result is published. Every diameter is accompanied by its 16–84% interval, evidence tier, ±{method['floor_fraction']*100:.0f}% systematic floor and single-visit warning where applicable. A D-versus-H chart separates measured diameters from assumed-albedo reference curves. All {len(pairs)} validation pairs are shown against NEOWISE on logarithmic axes with a 1:1 line; the reference entries and query provenance are retained.

For example, {size['pdes']} has D = {size['D_km']:.3f} km, interval {size['D16']:.3f}–{size['D84']:.3f} km, and tier {size['tier']}. It has one visit: this is preliminary, and its low inferred albedo requires checking H. The NEATM calibration uses η = {method['eta']} ± {method['eta_sigma']}; the trail limit is {method['trail_max_px']} pixels. The fitted median is not an independent accuracy statistic. The page displays retained results rather than refitting the asteroid data in the browser.

### Comets and Consistency Checks

The atlas contains {atlas['counts']['comets']} comets and distinguishes detections, measurements with systematics and marginal cases. Each CO₂ rate retains its 16–84% interval, S/N of detection, fractional flux error, core-channel count and reduced χ². Far-distance and outflow-speed limitations remain visible. Detail pages for 3I/ATLAS and 29P show real tracked plates ordered by wavelength, measured spectra, diagnostics and provenance. A plate taken in the CO₂ band is labelled as a band image, not a continuum-subtracted gas map.

For 3I/ATLAS in August, Q(CO₂) = {sci(august['measured'])} s⁻¹ lies within the published {sci(august['published_lo'])}–{sci(august['published_hi'])} s⁻¹ range. The product's independent physical-model regression uses retained sky-subtracted photometry and must recover that range. This is a consistency check, not an independent discovery or confirmation. Its displayed statistical and total-interval provenance are distinguished. The December fit carries its poor-fit caveat. For 29P, Q(CO) = {sci(co['measured'])} s⁻¹ is compared with the published {sci(co['published_lo'])}–{sci(co['published_hi'])} s⁻¹ range, also as a consistency check. The unsupported August H₂O comparison remains withheld.

## Architecture and Validation

The static Svelte frontend is deployed on Cloudflare Pages. The FastAPI backend runs on one Fly machine with a persistent cache. The scientific core resolves canonical public-S3 files, reads their physical FITS layout, uses full-resolution spectral calibration, reprojects north-up cutouts, and samples visits across time. The WebGL2 viewer uploads frames progressively from a worker; Aladin is imported only in Lab mode.

One-click spectra use a sampled normalized effective PSF, a weighted amplitude-plus-background fit, the header pixel solid angle and the official photometry mask, without an aperture correction. Reference calibration ratios from {calibration['n_stars']} stars are {checks}. Three deployed-API stellar spectra were additionally compared in Ks and W2 and passed the required ±5% checks. The detector-3 ePSF grid and raw/compressed FITS layouts have regression coverage.

Known limits are public: source coverage differs by detector; R Dra D6 currently ends before the requested September baseline; some external identification queries time out; and cold arbitrary stacks can exceed the four-second performance goal. No missing sky data, gas maps or unavailable catalog identifications are fabricated. Current test and performance evidence is recorded with the code.

## Pre-event Research Disclosure

[This section is written by Sebastián before submission.]

## Built During the 48 Hours

The delivered work comprises the deployed web application and API; SPXF reader/writer and scientific core; prepared five-target and tracked-comet packages; progressive image viewer; playback, blink and Diff λ; epoch-aware Gaia markers; URL sharing and embedding; one-click spectra and Lab inspector; Aladin cube controls; Small-Body Lab; comet atlas and two detail pages; data-driven landing; onboarding; English and Spanish; method, credits and source provenance pages; and automated contract, data, numerical, browser and deployment verification. This list describes the software and packaging built for the event and does not claim the retained research measurements were first made during it. The demonstration video is produced separately by the team.

## Use of Artificial Intelligence

AI-assisted tools were used for software implementation, debugging, documentation and test preparation. Scientific statements are tied to retained measurements, catalog values or cited publications; numerical and browser checks distinguish working behavior from unresolved limitations. The scientific sky plates are real mission data. The interface's decorative background is separate from those plates. No generated sky scene is presented as an observation.

## Space Agency Data and References

- NASA/JPL-Caltech/IRSA: SPHEREx L2 DR1/QR3 images and the DR1 HiPS spectral cube; https://irsa.ipac.caltech.edu/Missions/spherex.html
- NASA/JPL: Horizons spacecraft-observer ephemerides, SBDB and background Small-Body Identification; https://ssd.jpl.nasa.gov/horizons/
- ESA/Gaia/DPAC: Gaia DR3 positions and proper motion; https://www.cosmos.esa.int/web/gaia/dr3
- NASA/IPAC IRSA: 2MASS, WISE/AllWISE and NEOWISE V2 diameters; https://irsa.ipac.caltech.edu/
- 3I published comparison: {august['source']}.
- 29P published comparison: {co['source']}.
- Aladin Lite: CDS, Boch & Fernique 2014; Baumann et al. 2022; https://aladin.cds.unistra.fr/
- Astropy Collaboration 2022; https://www.astropy.org/; reproject: https://reproject.readthedocs.io/

This is an independent Space Apps project, not a NASA product. Data retain their original attribution; project code is released under GNU GPL version 3.
"""


if __name__ == "__main__":
    path = ROOT / "docs/SUBMISSION.md"
    path.write_text(render())
    print(f"Wrote {path.relative_to(ROOT)}")
