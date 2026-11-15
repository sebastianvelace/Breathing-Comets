# Breathing Comets: a Small-Body Lab for SPHEREx

## High-Level Project Summary

SPHEREx maps the sky in 102 infrared colors. Breathing Comets turns real mission images into a public time machine: play exposures, blink two dates, compare the sky at matched wavelengths, and click a position for a measured spectrum. Five prepared challenge targets and tracked comet plates remain available when the live API is unavailable. Our Small-Body Lab presents 28 thermal-size estimates for near-Earth asteroids, including 7 with potentially hazardous orbits, plus 6 explicitly provisional estimates. A retained cross-validation diagnostic against 50 NEOWISE objects gives −33%/+36% dispersion; it is not yet a blind test of the new-object estimator, and every size keeps its interval and ±35% systematic floor. The comet atlas shows emission-band measurements with their detection diagnostics and limitations. English and Spanish interfaces, source credits, a public method page and a reproducible codebase make the evidence available for inspection.

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

- **Barnard's Star:** Proper motion (SPHEREx): 10.6 ± 0.4″/yr (Gaia 10.39″/yr); Parallax: not measurable (saturated core) (547 mas). Caveat: formal error ±0.10″/yr; ±0.4 reflects frame systematics (saturated core, 3 useful visits).
- **ε Indi B:** Proper motion (SPHEREx): 4.75 ± 0.04″/yr (Gaia DR3 4.68″/yr); Parallax (differential vs 4 Gaia field stars): 271 ± 20 mas (Gaia DR3 270.7 mas (ε Ind A: 274.8 mas)). Caveat: error from per-visit bootstrap (9 visits); dropping one control star gives 277–294 mas.
- **WISE 0855−0714:** Below 3.8 µm: ≈ 0 (deblended from Gaia star at 6.8″) (J ≈ 25); Synthetic W2 (real W2 response curve): 0.45 ± 0.02 mJy, statistical and conditional on a flat tail beyond 4.97 µm (tail sensitivity 0.41–0.49 mJy) (published W2 ≈ 13.9 mag (0.48 mJy); CatWISE2020 13.82 (0.51 mJy)). Caveat: 14% of the W2 band lies beyond SPHEREx's 5.0 µm limit; the AllWISE catalogue value (13.70 mag, 0.57 mJy) is blended at the 2010 position.
- **R Draconis:** Variability timescale (3.8–5.0 µm, wing photometry): ≈ 229 d (225–241) (catalogued period 245.6 d); Peak-to-peak range (5–95%): 2.0 mag (0.9 µm) → 0.7 mag (4.4 µm) (Mira). Caveat: only 1.9 cycles observed: consistent with the catalogued period, not an independent measurement (1.1–2.4 µm gives 236 d, 230–519).
- **RW Aurigae:** 2025-09 → 2026-09: optical ×1.8 · 4–5 µm ×0.5 (anti-correlated) (inner-disk hot dust); SPLICES: ice target (Class II YSO) (IRSA). Caveat: three epochs only.

### Small-Body Lab

The catalog presents 11 tier-A and 17 tier-B sizes from 86 candidates, plus 6 provisional entries. No tier-C result is published. Every diameter is accompanied by its 16–84% interval, evidence tier, ±35% systematic floor and single-visit warning where applicable. A D-versus-H chart separates measured diameters from assumed-albedo reference curves. All 50 retained cross-validation pairs are shown against NEOWISE on logarithmic axes with a 1:1 line; each held-out template used its NEOWISE diameter and albedo, so this is a diagnostic until a blind re-validation is run; the reference entries and query provenance are retained.

For example, 2025 YH5 has D = 0.949 km, interval 0.610–1.363 km, and tier A. It has one visit: this is preliminary, and its low inferred albedo requires checking H. The NEATM calibration uses η = 1.48 ± 0.44; the trail limit is 3 pixels. The fitted median is not an independent accuracy statistic. The page displays retained results rather than refitting the asteroid data in the browser.

### Comets and Consistency Checks

The atlas contains 20 comets and distinguishes detections, measurements with systematics and marginal cases; two detections with no band-core channel are flagged as weakly constrained in Q. Each CO₂ rate retains its 16–84% interval, S/N of detection, fractional flux error, core-channel count and reduced χ². Far-distance and outflow-speed limitations remain visible. Detail pages for 3I/ATLAS and 29P show real tracked plates ordered by wavelength, measured spectra, diagnostics and provenance. A plate taken in the CO₂ band is labelled as a band image, not a continuum-subtracted gas map.

For 3I/ATLAS in August, Q(CO₂) = 1.17 × 10^27 s⁻¹ lies within the published 9.4 × 10^26–1.6 × 10^27 s⁻¹ range. The product's independent physical-model regression uses retained sky-subtracted photometry and must recover that range. This is a consistency check, not an independent discovery or confirmation. Its displayed statistical and total-interval provenance are distinguished. The December fit carries its poor-fit caveat. For 29P, Q(CO) = 4.5 × 10^28 s⁻¹ is compared with the published 2.9 × 10^28–5.6 × 10^28 s⁻¹ range, also as a consistency check. The unsupported August H₂O comparison remains withheld.

## Architecture and Validation

The static Svelte frontend is deployed on Cloudflare Pages. The FastAPI backend runs on one Fly machine with a persistent cache. The scientific core resolves canonical public-S3 files, reads their physical FITS layout, uses full-resolution spectral calibration, reprojects north-up cutouts, and samples visits across time. The WebGL2 viewer uploads frames progressively from a worker; Aladin is imported only in Lab mode.

One-click spectra use a sampled normalized effective PSF, a weighted amplitude-plus-background fit, the header pixel solid angle and the official photometry mask, without an aperture correction. Reference calibration ratios (band medians of 41 selected stars, power law at the isophotal wavelength, not response-convolved photometry) are J: 0.982; H: 1.008; Ks: 1.011; W1: 0.972; W2: 0.996. Three deployed-API stellar spectra were additionally compared in Ks and W2 and passed the required ±5% checks. The detector-3 ePSF grid and raw/compressed FITS layouts have regression coverage.

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
- 3I published comparison: Lisse et al. 2025, RNAAS, arXiv:2508.15469 (0.94e27, preliminary); Lisse et al. 2026, ApJL 1000, L52, arXiv:2512.07318 (1.6e27 +/- 0.16e27).
- 29P published comparison: Bockelee-Morvan et al. 2022 (IRAM, 2.9-5.6e28); quiescent 1.8e28 (Festou et al. 2001).
- Aladin Lite: CDS, Boch & Fernique 2014; Baumann et al. 2022; https://aladin.cds.unistra.fr/
- Astropy Collaboration 2022; https://www.astropy.org/; reproject: https://reproject.readthedocs.io/

This is an independent Space Apps project, not a NASA product. Data retain their original attribution; project code is released under GNU GPL version 3.
