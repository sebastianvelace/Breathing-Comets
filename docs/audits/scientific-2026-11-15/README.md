# Scientific audit — 15 November 2026

**Assessment: requires revision for quantitative scientific claims.** Two high-priority findings affect the validity of the difference images and the interpretation of asteroid cross-validation. Several additional issues limit uncertainty, calibration and physical interpretation. These findings do not establish that all retained fluxes or diameters are wrong.

Reviewed product commit: `f47f1e4e6ebc6e16d8036796287659fdd699d063`. Production scientific code and derived measurements were not modified by this audit. Controlled synthetic inputs below are diagnostic counterexamples, never observations or replacement product data. A concurrent spectrum tick-label commit (`d67eb24`) did not alter any cited numerical source or input; the snapshot and source hashes are recorded separately.

## Scope and evidence

- Inspected native FITS access, calibration, masks, TAN reprojection, variance, ePSF photometry, time/position propagation, Diff λ, the comet conversion and the published JSON/validation scripts.
- Read the retained research reference separately, including the actual NEATM/CV generators, centroid tables, control-star fits, filter response and null/injection tables. This checkout is not part of the public product repository; findings relying on it are labelled below.
- Executed existing scientific acceptance tests unchanged: **154 passed, 1 failed, 8 deselected**. The existing R Dra D6 baseline assertion still fails; no assertion was relaxed.
- Executed all real-FITS network tests: **9 passed, 200 deselected**, 59.38 s. These compare physical FITS layouts, ePSF table zones, detector-3 geometry and wavelength maps with independent Astropy reads.
- Replayed the five published default-detector difference packages, independently evaluated the thermal integral, recomputed the retained 3I CO₂ fit, and independently solved the retained ε Indi B centroid regression.
- Consulted the official SPHEREx Explanatory Supplement **v2.1, 2026-11-10**, IRSA examples, the WISE photometric documentation, JPL Horizons documentation and the original 3I paper. Input and source hashes are in `provenance.json`.

Passing software tests establish their specific contracts. They do not establish population accuracy, interval coverage or astrophysical discovery significance.

## Findings

### F1 — P1: invalid reference pixels can create apparently valid changes

**Product sources:** `packages/spxcore/spxcore/sky.py:34–59`; `packages/spxcore/spxcore/cutout.py:112–129`.

`difference_stack` defines valid reference samples using finite flux and wavelength only. It never applies their quality flags. Its output copies the target frame's flags, so contamination from a flagged reference can appear in an unflagged result. Nearest-neighbour flag reprojection also fails to describe every native pixel contributing to bilinearly interpolated flux.

**Reproduction:** a static target of 10 and reference values 100, 10, 10, with the 100 explicitly flagged `SUR_ERROR`, produce a difference of **−30**, `flags=0`, `diff_available=true`. Only two usable references actually remain. A separate reprojection of a flagged native value 100 at fractional coordinates (0.49, 0.49) produces **24.01** with output flags zero.

**Effect on retained observations:** the current unmodified algorithm exactly reproduces the five published difference packages: maximum replay discrepancy is zero. Applying the official hard mask to reference fluxes in memory changes thousands of originally unflagged pixel-frame values by more than five original display-MAD scales: Barnard **4,379**; ε Indi B **3,299**; R Dra **4,116**; RW Aur **3,527**; WISE 0855 **2,223**. Barnard also loses the minimum usable reference count at 18,118 previously finite, unflagged pixel-frame positions.

These are correlated image values, **not counts of false astronomical discoveries or statistical 5σ detections**. They nevertheless demonstrate a material effect on shipped data.

**Required correction:** propagate the validity of all resampling contributors; exclude invalid reference samples before fitting/clipping; enforce at least three usable references per pixel; propagate reference validity into the output. Regenerate the affected prepared differences after adding these cases as regressions.

### F2 — P1: asteroid validation uses the held-out diameter inside its predictor

**Retained research sources:** `research/feasibility/neo_cv_psf.py:12–31`, `research/feasibility/neatm.py:35–43`. **Public claims:** `apps/web/static/data/neo/index.json` (`cv_note`); `apps/web/messages/en.json:324`; `docs/SUBMISSION.md`.

The fold excludes an object when estimating the common η, which is appropriate. However, its held-out template is still built with that object's `D_NEOWISE` and the albedo inferred from it:

`pV = (1329 / D_NEOWISE)^2 × 10^(-0.4 H)`.

The validation fits a linear amplitude to that fixed template and reports `D_NEOWISE × sqrt(q)`. The estimator used for new objects instead updates `pV(D)` while solving for D. These are different estimators. Holding η out does not remove the use of the test target's diameter in the temperature, Bond albedo and reflected component of its prediction.

**Controlled counterexample:** an unchanged synthetic spectrum generated for D=0.500 km, H=18, r=2 au, an observer at 1 au and solar elongation 90° gives **0.433, 0.570 and 0.600 km** when only the reference diameter supplied to the CV-style predictor is changed from 0.4 to 0.7 to 1.0 km. A blind nonlinear fit to the same observations recovers **0.500000 km**. No real asteroid size is inferred by this experiment.

All 50 shipped rounded CV ratios match the retained CV table, so this is not a JSON transcription finding. The newly retained NEOWISE catalog correctly supplies references, but multiplying a ratio by a reference diameter does not independently validate the estimator that generated the ratio.

**Required correction:** recompute the CV with η and every tuned decision learned on training objects only. Fit each test object's D from its observed fluxes, geometry and H using exactly the new-object estimator, without its NEOWISE diameter/albedo. Reveal the reference afterward; report bias, scatter, failures, interval coverage and performance by thermal fraction/phase angle. Until then, the advertised −33%/+36% is a retained diagnostic, not a validated error distribution for the new-object pipeline. Its direction of bias cannot be inferred from this audit.

### F3 — P2: reprojected variance is interpolated as intensity

**Product source:** `packages/spxcore/spxcore/cutout.py:130–133`.

For a linear resampling `y = Σ w_i x_i`, independent input variance propagates as `Var(y) = Σ w_i² Var(x_i)`. The code instead interpolates the variance with `w_i`. Adjacent output pixels also acquire covariance, which is not represented.

The executed (0.49, 0.49) test returns variance **1.0000** for unit input variance, whereas the independent-input calculation gives **0.25020004**, a factor **3.9968** difference. This quantifies the inconsistency under the stated independent-pixel model; it is not a claim that every actual mission variance is wrong by this factor.

**Required correction:** use squared interpolation weights, define how invalid contributors are treated, and document/validate covariance or the approximation used for spatial sums and differences. This finding affects reprojected image/Diff variance; native-pixel live PSF fitting uses a different path.

### F4 — P2: sparse-band production rates need stronger uncertainty validation

**Sources:** `pipelines/export_comets.py:55–79`; retained `data/derived/injection_recovery.csv`, `research/15_injection_recovery.py`; shipped comet index.

The status rule does not consider core coverage or flux/profile degeneracy. **235P/LINEAR** is labelled detected with zero core channels, S/N_det=14.25 but physical-flux S/N≈1.69 and fractional error≈59%. **C/2025 Q3** is also detected with zero core channels. A statistically significant excess and an identified integrated band flux are different inferences.

A retained spectral-injection experiment exists in the research checkout, although it is not published/reproduced end to end in the product. Among 573 retained injection cells passing the joint S/N≥5 and χ²ᵣ<50 rule, the 12 with zero core channels have recovered/injected flux percentiles **0.321 / 1.161 / 5.037**; only 1/12 has |total-error pull|≤1. The corresponding two-or-more-core subset has 358 cells and coverage≈66.5%.

These cells reuse backgrounds and span multiple fluxes/temperatures; they are not independent population trials. Detection conditioning, the small zero-core subset and the use of unsubtracted null spectra prevent interpreting these numbers as a current census-wide error rate. They do identify a failure regime requiring matched validation.

**Required correction:** distinguish band-excess evidence from an adequately constrained Q, flag zero-core inference, and execute injections through the actual sky-subtraction/photometry/response pipeline. Calibrate interval coverage at fixed injected flux/geometry before making completeness or precision claims.

### F5 — P2: synthetic W2 has an unpropagated extrapolation assumption

**Retained generator:** `research/28_export_static.py:78–86`. **Published value:** `apps/web/static/data/targets/wise-0855.json`.

The W2 estimator extends the last measured flux bin as a flat tail through the response beyond 5 µm using `np.interp`. Approximately **13.89%** of its response-weight integral lies beyond 5 µm; the last supported bin is at 4.971 µm. Monte Carlo perturbations vary measured bins, not the tail model.

The audit reproduces **0.449899 mJy**. Keeping the measured part fixed and setting only the unobserved red tail to zero or twice the flat extrapolation gives **0.414728–0.485070 mJy**, versus quoted ±0.02 mJy. These are sensitivity scenarios, not confidence bounds or models of the true brown-dwarf spectrum.

**Required correction:** explicitly label the published error as conditional/statistical, state the extrapolation, and retain a separate tail-model systematic or publish an in-coverage diagnostic. A full synthetic catalog comparison should also use the relevant response and catalog reference-spectrum convention. WISE explicitly documents such color corrections [S3].

### F6 — P2: stellar acceptance checks do not fully validate broadband calibration

**Product source:** `scripts/validate-api-spectra.py:20–26`; `data/validation/photometric_bands.json`. **Retained 41-star generator:** `research/25_validate_spectra_2mass_wise.py:45–61`.

The three-star check uses an unweighted median of spectral points inside rectangular Ks/W2 windows. The research 41-star check instead fits a power law and evaluates it at an isophotal wavelength. Neither is a full response-convolved catalog synthetic measurement. An uneven wavelength/time sampling, molecular features or a red spectrum can therefore affect the comparison.

The reported band medians and robust dispersions reproduce from the retained 41-star table: J **0.9821**, H **1.0081**, Ks **1.0109**, W1 **0.9721**, W2 **0.9959**. This is useful support for approximate flux scale on that selected sample. It does not establish ±3% accuracy for every point/source; e.g. the actual J sample standard deviation (N−1 denominator) is 8.35%, whereas the published 1.96% is the robust MAD-based scatter.

**Required correction:** retain the approximate check with its correct scope and add response-convolved photometry, catalog errors/color conventions, wavelength-coverage checks, and independent objects spanning color, brightness, crowding and detector position.

### F7 — P2: the public outflow-speed sentence changes the physical law

**Product sources:** `apps/web/messages/en.json:189,314`, corresponding Spanish messages, `pipelines/landing_3i.py:63–67`. **Retained model:** `research/13_census_physical.py:33–44`.

The alternate recipe changes **v₀ from 0.85 to 0.50 in v=v₀ r_h⁻¹ᐟ² km/s**. It does not set v=0.50 km/s at every distance. The public sentence omits the distance dependence from the alternative and says all Q fall by ≈40%.

At r=3.2 au the baseline speed is 0.475 km/s. Replacing it by a constant 0.50 increases Q by approximately 5.1% in the executed Haser calculation; at 29P's r≈6.3045 au it increases Q by approximately 46.7%. Changing the coefficient in both distance-dependent laws is the recipe that reduces Q by ≈40%.

**Required correction:** write both complete laws. The retained alternate recipe values are not changed by this wording finding.

### F8 — P2: median fallback is not a wavelength-matched static reference

**Product source:** `packages/spxcore/spxcore/sky.py:52–55`; public description `apps/web/messages/en.json:298–299`.

The fallback is explicitly documented, but its resulting images still share the broad claim that unchanged sky cancels. With a perfectly static linear spectrum `F(λ)=10+100λ`, target λ=4.50 µm and three references at 4.52/4.54/4.56 µm, the executed fallback produces **−4**, with Diff available. The same-color change is exactly zero.

**Required correction:** expose bracketed/matched support per pixel or mark this fallback as a color-dependent approximation. Avoid interpreting its residuals or its display-MAD scale as calibrated temporal significance. PSF, background and astrometric differences also require validation before quantitative transient detection.

### F9 — P2: live Gaia propagation omits observer parallax

**Product sources:** `packages/spxcore/spxcore/ephem.py:18–25`; frontend `apps/web/src/lib/data/coordinates.ts`.

Supplying distance to `apply_space_motion` performs barycentric space motion; it does not subtract the observer's position [S4]. The frontend similarly propagates proper motion only. A monthly 2026 diagnostic for Barnard gives an omitted observer-parallax displacement reaching **0.546 arcsec**, about **0.089 native pixels**. This is a precision limit, not an explanation for multi-pixel motion or proof that every fitted flux is biased.

The retained research astrometry separately includes the observer vector and should not be confused with this live path. Its central result independently reproduces: **270.739 mas**, 194 retained centroids and nine visits. An independent visit resampling gives ≈19.5 mas half-width, consistent with retained 19.6 mas; individual finite-bootstrap draws depend on ordering. Dropping controls gives 276.7–293.6 mas, an additional sensitivity, not included automatically in a total error.

**Required correction:** label live predictions as proper-motion-only, or implement observer-referenced positions for precision fitting; propagate/catalogue radial-velocity assumptions explicitly. Do not use the live marker implementation as validation of a parallax measurement.

### F10 — P2: the physical CO₂ regression is conditional, not complete model validation

**Product source:** `packages/spxcore/spxcore/comets.py:27–90`; `data/derived/comets/3i_aug2025_physical.json`.

The executed golden case gives **Q=1.16743×10²⁷ s⁻¹**, statistical error **3.00417×10²⁵ s⁻¹**, χ²ᵣ=27.4833, T=100 K and extra width=0.005 µm. Its Haser conversion and unit conversions are coherent. However:

- A Gaussian channel response is substituted for calibrated transmission profiles, which IRSA makes available [S5]. The rotational temperature/extra width can absorb response mismatch.
- The covariance is conditional on the selected profile. The reduced-χ² divisor N−4 has no documented effective-degree-of-freedom justification for searching temperature and width in addition to three linear coefficients.
- There are **26** nonzero retained fit points; the provenance text says 28.
- The displayed 16–84% interval is retained from notes, not regenerated by this regression.
- The “published range” combines a preliminary and an updated estimate from the same observation campaign. The updated paper reports 1.6×10²⁷±10%, with its stated aperture and g factor [S6]. Agreement with the combined envelope is a useful consistency check, not an independent calibration or a confidence interval.

**Required correction:** convolve line models with the released responses, evaluate profile/continuum/calibration/velocity uncertainty jointly, validate coverage empirically, correct point-count metadata and compare literature estimates separately under common assumptions.

### F11 — P2: public reproducibility does not cover every retained headline result

The repository publicly retains images, point lists, derived summaries, catalog rows and several executable core tests. It does not include the complete NEATM/CV fitting pipeline and held-out photometry needed to regenerate the 50 ratios, or the retained centroid/control tables and fitting pipeline used for the headline differential parallax. Several of those inputs were available only in the separate research checkout for this audit. Recovering the 50 reference diameters addresses reference provenance, not the missing measurement/model chain.

**Required correction:** version the minimal licensed generators, exact selections and inputs, source-release/calibration identifiers, coordinate/time conventions and seeds. Mark non-reproduced results as retained research in the public claims until this chain is available. Do not interpret a count/value equality assertion as an independent scientific validation.

## Checks that support the scientific foundation

- The official supplement supports native calibrated intensity units, use of the supplied effective PSF, local-background fitting and the 3% photometric error term. The current core's native-pixel flux conversion using positive header solid angle is dimensionally consistent [S1–S2].
- The native photometry hard mask is consistent with the documented recommendation; intentionally retaining `OVERFLOW` is not by itself a masking bug. The F1 finding concerns invalid references/resampling, not a demand to mask every flag indiscriminately.
- All nine real-FITS checks passed, including the detector-3 11×41 ePSF grid. Sampled evaluation of a pixel-convolved ePSF is consistent with IRSA's executable rendering example; reintegrating an already pixel-convolved model would need justification [S2].
- The independently integrated NEATM thermal component agrees with the retained implementation within **0.0461%** in three tested quadrature cases. This supports its numerical integration; it does not validate its priors, reflected component, thermal fraction or population calibration.
- The parent Haser aperture fraction agrees with an independent direct line-of-sight cylindrical population integral to relative error below 1e-12 at five tested aperture/scale ratios. The 3I central rate and the ε Indi B centroid-regression central result reproduce with the limitations above.
- The retained null table has **0/79** passing the joint rule. One null has S/N=5.287 but χ²ᵣ≈6817 and is rejected. Thus the public joint-rule count is consistent with the retained table. These correlated, differently processed controls do not establish a Gaussian 5σ false-alarm probability or end-to-end completeness.
- R Dra's failed September coverage assertion remains visible. The product appropriately calls its ≈229-day result a timescale over ≈1.9 cycles rather than an independent period determination.

## Recommended order

1. Correct reference/input quality handling and variance propagation; rerun prepared-image numerical and visual acceptance without changing expected scientific thresholds.
2. Rebuild asteroid validation using a genuinely blind version of the production estimator; revise the public scatter/accuracy wording until it passes.
3. Validate comet band-flux/Q intervals using the actual subtraction, responses and quality-selection pipeline, including sparse-core cases.
4. Correct the outflow law wording, W2 error scope, response-convolved broadband comparisons and live astrometric scope.
5. Publish the minimal reproducibility chain and a claim-to-evidence table, distinguishing retained summaries, rerun checks and still-open assumptions.

## Reproduction

Run from the product repository root, using its existing pinned environment:

```sh
PYTHONPATH=packages/spxcore .venv/bin/python docs/audits/scientific-2026-11-15/core_probe.py
PYTHONPATH=packages/spxcore .venv/bin/python docs/audits/scientific-2026-11-15/prepared_probe.py
```

Optional read-only checks require the separately retained research checkout:

```sh
.venv/bin/python docs/audits/scientific-2026-11-15/thermal_probe.py --research-root /path/to/research-checkout
PYTHONPATH=packages/spxcore .venv/bin/python docs/audits/scientific-2026-11-15/research_probe.py --research-root /path/to/research-checkout
.venv/bin/python docs/audits/scientific-2026-11-15/astrometry_probe.py --research-root /path/to/research-checkout
```

The probes print diagnostics and never write to scientific input files. `*-observed.json` records the audit observations, and the two test logs retain the existing test outcomes. Research probes reuse retained measurements or model definitions; they do not independently remeasure every source from raw mission pixels.

## Primary sources

- **S1:** [SPHEREx Explanatory Supplement v2.1](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp.pdf), photometry/masking guidance, uncertainty correction and spectral WCS.
- **S2:** [IRSA ePSF tutorial](https://caltech-ipac.github.io/irsa-tutorials/spherex-psf/), especially the pixel-convolved definition and native-grid rendering example.
- **S3:** [WISE photometric calibration and color corrections](https://irsa.ipac.caltech.edu/data/WISE/docs/release/All-Sky/expsup/sec4_4h.html).
- **S4:** [Astropy space motion](https://docs.astropy.org/en/stable/coordinates/apply_space_motion.html) and [JPL observer-table time/coordinate definitions](https://ssd.jpl.nasa.gov/horizons/manual.html).
- **S5:** [SPHEREx spectral calibration products](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Spectral_Calibrations_V2.pdf).
- **S6:** [Lisse et al., updated SPHEREx 3I analysis](https://arxiv.org/html/2512.07318v2), gas-production assumptions and updated rates.
