# Final numerical audit — 15 November 2026

Every number shown by the product and quoted in the submission text was recomputed from the shipped data files by `recompute.py`. That script is read-only and prints one line per check; its output is retained in `recompute-observed.json`.

```sh
.venv/bin/python docs/audits/final-2026-11-15/recompute.py
```

**Result after corrections: 0 FAIL, 33 PASS, 13 NOTE.**

## Corrected in this audit

| Item | Before | Recomputed | Change |
|---|---|---|---|
| WISE 0855 published W2 | "≈ 13.9 mag (0.48 mJy)" | 13.9 mag = 0.473 mJy; 0.48 mJy corresponds to 13.89 mag (W2 zero point 171.787 Jy) | Text now says 13.89 mag |
| 3I/ATLAS CO₂ comparison | "inside the published range" | 1.17×10²⁷ s⁻¹ agrees with the preliminary 0.94×10²⁷ s⁻¹ but lies below the updated 1.6×10²⁷ s⁻¹ ± 10%: −2.6σ using the statistical error alone, and our 16–84% upper bound (1.38×10²⁷) is below 1.44×10²⁷ | Stated explicitly in the atlas, the submission and the form; not attributed to any cause |
| ±3% photometric scale | all-field band medians only | Per-field medians span 0.943 (NEP, Ks) to 1.023 | Range added to the method page and the form |
| R Dra 225–241 d | interval shown without context | Rayleigh resolution P²/T ≈ 123 d over 425 d; catalogued 245.6 d lies between p84 (241) and p97 (261) | Added to the caveat |
| Live Gaia marker (F9) | proper motion only | Observer parallax now applied in the viewer; against an Astropy/DE440 geocentric reference the error is 4.67 mas at most (was up to 530 mas) | Implemented and unit-tested (`apps/web/tests/parallax.test.ts`) |

## Verified (PASS)

- **Barnard's Star.** PM 10.552″/yr from components (shown 10.6); propagated formal error 0.105″/yr (shown ±0.10); Gaia 10.393″/yr and 546.98 mas; position angle within 0.9° of Gaia.
- **ε Indi B.** Differential PM 4.754 ± 0.039″/yr from the visit bootstrap; Gaia 4.684″/yr; parallax 270.74 ± 19.62 mas; methane ratio 5.43 (median of 3.9–4.1 µm over median of 3.2–3.4 µm; shown 5.4×).
- **R Dra.** 228.6 d (225–241); amplitudes 1.96 and 0.70 mag; 1.1–2.4 µm gives 236.2 d (230–519).
- **RW Aur.** Last/first epoch ratio is 1.76 at 0.75–1.1 µm and 0.46 at 3.8–5.0 µm (shown ×1.8 and ×0.5).
- **W2 conversions.** 13.89 → 0.478, 13.82 → 0.509, 13.70 → 0.569 mJy.
- **Comets.** The status rule reproduces all 20 statuses and the 17/2/1/0 counts. Q percentiles are ordered. Q(v₀ = 0.50)/Q(0.85) = 0.592–0.601 (the 40% statement). Far and zero-core flags are correct. Both literature checks lie inside their stated envelopes.
- **Asteroids.** Tier counts are 11/17/6 with 7 PHAs in A/B. D = 1329/√pV · 10^(−H/5) holds within 1.2% for every object (pV is rounded). Every D lies inside its interval. CV p16/p50/p84 = 0.672/1.019/1.358 is recomputed from the 50 shipped ratios (−32.8%/+35.8%).
- **Instrument.** Detector edges and resolving powers match `channels.json` (102 channels, 0.753–4.988 µm centres). Calibration mean 0.994, range 0.972–1.011.

## Notes retained (not errors, disclosed or out of scope)

- Barnard `pm_total_err` = 0.149 in the data file is the quadrature sum of the component errors, not a propagation; it is not displayed.
- ε Indi B PM differs from Gaia by +0.070″/yr (1.8σ). Gaia DR3 treats B as one source, and the Ba/Bb orbital motion is not modelled.
- R Dra's 0.75–1.1 µm (135 d) and 2.4–3.8 µm (101 d) periodogram peaks are not shown and are inconsistent with the Mira period.
- Six asteroids have pV < 0.03, which is below the usual NEO albedo floor; the product flags them ("check H").
- The CV robust width (0.388) matches the stored σ_ln (0.387); the ordinary standard deviation is 0.357.
- The 41-star calibration table and the J standard deviation (8.35%) come from the retained research table, which is not in this repository.
- The correlation between Q r⁻²Δ⁻² and S/N across the 20 comets is 0.33 (rank correlation). It is a weak sanity check only: S/N also depends on exposure count and background.
