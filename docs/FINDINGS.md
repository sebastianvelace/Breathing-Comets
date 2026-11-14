# Findings log (2026-11-14)

Everything found while integrating steps 8–11, with evidence and what was done. "Open" means it still needs a decision or work.

## 1. Product defects and fixes

| # | Finding | Evidence | Action | State |
|---|---|---|---|---|
| F1 | **Tracked stacks fail beyond ~4 days.** `tracked_rows` sampled Horizons every hour; more than ~100 JD values in the URI are truncated, and the call fails as `EphemerisUnavailable` / HTTP 503 `UPSTREAM_UNAVAILABLE`. | `ephem.horizons_positions("2025 N1", linspace(60886, 60903, n))`: n = 5 and 60 ok; 150 and 409 failed in ≤ 1 s, with astroquery warning "uri ... very long and might have been truncated". | `horizons_positions` now splits into chunks of 40 epochs; `tracked_rows` samples every 6 h (D5 field is 3.5°, comet moves ~0.5°/day). `tests/test_horizons_chunks.py` (2 passed). | **Fixed in code, NOT deployed to Fly.** The public API still has the bug. |
| F2 | **29P cannot be tracked by designation.** Horizons answers "no ephemeris" for `29P`, `29P;`, `DES=29P;` and the full name (ambiguous apparition records). The resolver's SBDB `des` is `29P`, so `/v1/resolve?q=29P` also fails. | Four designations failed, numeric SPK id `90000393` returned (173.1519, −2.738) at MJD 61025.2. | Stack fetched with `track=90000393`; documented in `static/data/comets/29p-schwassmann-wachmann/provenance.json`. | **Open:** the resolver should map periodic comets to a unique Horizons id (or use `NAME=`/ closest-apparition records). |
| F3 | **Public API blocks the E2E origin.** `services/api/fly.toml` sets `SPX_ALLOWED_ORIGINS` to production + `localhost:5173`, overriding the code default that includes `127.0.0.1:4183`. Two live-click E2E tests failed locally with `blocked by CORS policy`. | Console capture; `curl -H 'Origin: http://127.0.0.1:4183'` returned no `access-control-allow-origin`. | Tests built against the local API (`VITE_API_BASE`) pass 26/26. | **Open (decision):** add `http://127.0.0.1:4183` to `fly.toml` if public-API E2E from a laptop is wanted. |
| F4 | Cold stack latency still above target. | 5.2 s first byte / 6.6 s total against the 4 s goal (STATUS step 7). | Not optimised. | **Open.** |
| F5 | SB Identification (JPL) lookups time out at 25 s. | STATUS step 7. | Reported as source unavailable; nothing invented. | **Open.** |

## 2. Scientific findings (what may and may not be claimed)

| # | Finding | Evidence | Action |
|---|---|---|---|
| S1 | **The retained `3I_aug2025_bandfits.csv` does not support 1.17e27.** It is the earlier Gaussian fit without sky subtraction: 3 px gives Q = 1.11e27 with χ²ᵣ = 278, and Q falls from 1.1e27 (2–3 px) to 0.7e27 (16 px). | `data/derived/comets/3I_aug2025_bandfits.csv`. | Not used as the validation measurement. |
| S2 | **1.17e27 ± 3.0e25 is reproducible** from the sky-subtracted D5 spectrum with the physical band model: best no-evolution fit χ²ᵣ = 27.5, T_rot = 100 K, σx = 0.005 µm. | Re-ran `research/11_band_physical.py` read-only; evidence in `data/derived/comets/3i_aug2025_physical.json`. | Used as the headline August value. The 16–84% range 0.86–1.38e27 comes from research notes and was **not** re-run; the page says so. |
| S3 | **3I December and C/2025 A6 Lemmon: band present, model poor** (χ²ᵣ 185 and 72 ≥ 50). | `co2_census_physical.csv`. | Status "with systematics"; Q shown with that caveat and not as a clean detection. |
| S4 | **P/2021 N1 is marginal** (S/N 4.1) and **C/2014 UN271 at 15 au is unreliable** by the flux ∝ Q r⁻²Δ⁻² argument. | Same CSV; BUILD A.2. | Marked in the atlas. |
| S5 | **Q ∝ outflow speed**: assuming 0.50 instead of 0.85 r_h^−0.5 km/s lowers every Q by about 40%. | Median `sys_v` = 0.6 over the 20 comets. | The percentage is computed from the data and shown on the atlas and in the 3I caveat. |
| S6 | **3I August H₂O (4.0e26 against 3.2e26) was withheld.** No CSV or script output was retained for it. | No file under `data/derived` or the research repo produces it. | Shown as "pending" with the reason; re-derive before publishing. |
| S7 | **"29P in outburst" (BUILD 10.6) was not published.** Nothing retained verifies the outburst state. | — | Omitted. |
| S8 | **29P and 3I comparisons are consistency checks, not independent confirmations** (PENDIENTES P3): 29P Q(CO) 4.504e28 inside 2.9–5.6e28; 3I Aug inside 0.94–1.6e27. | `published_reference.json` with citations. | Wording on the pages says "inside the published range". |
| S9 | **R Dra baseline acceptance still fails**: last sampled date 2026-06-12 against required 2026-09-01 (source D6 coverage ends in June). | `test_r_dra_samples_full_baseline`, unchanged assertion. | Left failing, documented since step 5. |
| S10 | **NEOWISE absolute references available for 5 of 50 validation pairs** (IRSA TAP failed twice: 502 and read timeout). | STATUS step 9. | Page states 5/50. |
| S11 | Many real 3I frames show only a faint diffuse glow; the coma is clear at the CO₂ band. | `3i-sheet` contact sheet of the 12 August frames. | Shown as is, caption says "no continuum subtracted". No gas map exists, so none is shown. |

## 3. Process and environment findings

| # | Finding | Action |
|---|---|---|
| P1 | `AGENTS.md` does not exist in the repository although the task brief names it; `CLAUDE.md` and `docs/BUILD.md` were used. | Noted. |
| P2 | `pkill -f <pattern>` kills the calling shell when the pattern appears in the command line (exit 144). | Servers are now stopped by port/PID. |
| P3 | A `vite preview` left running across a rebuild serves a stale asset manifest (unstyled page). | Restart after each build; E2E owns port 4183. |
| P4 | Playwright's default browser cache is absent; the browsers live in `/tmp/breathing-comets-browsers`. | Use `PLAYWRIGHT_BROWSERS_PATH=/tmp/breathing-comets-browsers`. A reboot clears `/tmp`. |
| P5 | `ruff check .` reports 16 findings, all in `tests/test_reference.py` (ported reference tests the project forbids editing). | Left unchanged. |
| P6 | Bare `npx vitest run` also collects `e2e/*.spec.ts` and fails ("Playwright Test did not expect test() to be called here"). | Run `vitest run tests`. Config not changed. |
| P7 | Lighthouse is not installed and was not installed without authorisation. | LCP is only a proxy (see below). |

## 4. Budgets

| Budget | Result | Evidence |
|---|---|---|
| Initial landing JS < 90 KB gz | **88.5 KB** (25 modules) after the redesign | Sum of gzip -9 of the modules referenced by `build/index.html` and `build/es.html`. History: 70.4 → 80.8 (3I packet bundled) → 90.2 (ribbon with full `channels.json`) → 88.5 (derived `channels-lite.json`, 102 rows × 3 columns). |
| LCP < 1.5 s (Lighthouse mobile) | **Not verified.** Proxy 0.8–0.9 s measured before the redesign (Playwright + CDP throttling). Not re-measured after it. | — |
| Landing media | 252 KB landing plates + 228 KB comet plates (lossless WebP, 31–147 px) | `du`. |

## 5. Design deviations from BUILD 10.4 (flexibility requested by the user, each justified)

BUILD 10.4 forbids gradients, glows, glassmorphism and cards with shadow. The redesign keeps the paper/ink/ochre identity and Newsreader/Plex type, and deviates in these places only:

| Deviation | Where | Justification |
|---|---|---|
| Dark "plate" bands alternating with paper | Hero, ribbon, §2, §4, footer | The sky is the protagonist; plates are black in the concept (10.1). Dark bands make real frames and the Diff λ comparison read better. |
| Soft radial ochre vignette + 80 px registration grid + slowly turning star-chart rings | Hero background | Depth behind the plate without illustration or imagery; low contrast, `aria-hidden`, stops with reduced motion. |
| `color-mix` between the semantic blue and ochre | 102-channel ribbon | The colour encodes the real wavelength axis (short = blue, long = ochre); it is data, not decoration. |
| Glow on the 2 px scan line | Hero plate | It marks the current position of the blink loop; only drawn while playing. |
| `backdrop-filter` blur on the sticky masthead | Header | Keeps the navigation legible over dark and paper bands. |
| Scroll-driven reveals (`animation-timeline: view()`) and a scroll progress bar | Sections | CSS only, so no JS cost and no flash; absent where unsupported; disabled under `prefers-reduced-motion`. |

Everything else (no emoji, no stock icons, no NASA logos, no generated imagery, labelled uncertainty and caveats) is unchanged.

## 6. Known cosmetic items

- Ribbon band labels (CO₂ ν₃ / CO) touch on very narrow phones (≈ 375 px).
- The hero's first 3I frame is a faint field; the strongest frame is used in §4 as the poster.

## 7. Test findings

- `comet-detail.spec.ts` failed twice on production and passed locally. Cause: the prerendered HTML is interactive before Svelte hydrates, so a key press on the wavelength slider is lost when hydration is slow (local hydrates instantly). First attempt (poll instead of immediate read) did not fix it; the test now retries Home/End until the handler is attached (`toPass`). Product behaviour unchanged: a very early key press before hydration is ignored, as with any hydrated page.
- Production E2E after the final push: landing, comets, comet-detail and neo suites pass (see STATUS).

## 8. `/method` and a bundle-size finding (2026-11-14)

- `/method` (EN/ES, 10 sections) reads its numbers from product files: `build.json` (new, generated by `pipelines/build_info.py` from the stack header, parquet/npz indices, calibration and atlas), `calibration.json`, `channels.json`, the comet atlas and the NEO method block. Model constants (g, τ, speeds, windows) live in `src/lib/data/method.ts` with their source. Claims were checked against the code before writing them: Diff λ uses K = 8 references from other visits within 3 bandwidths, a per-pixel line fit with one 3·MAD clip (median if the references do not bracket the wavelength), σ = 1.4826·MAD; the photometric mask is `HARD_ES21`; the ePSF fit uses R = 4 px and a 3% floor.
- Not re-run and labelled as such on the page: the Diff λ χ²ᵣ improvements (104 → 6.5, 440 → 32), the 0/79 false positives on null spectra, and the 3I August 16–84% range. **Pending, stated on the page:** a published injection–recovery test; no completeness or false-alarm rate is claimed.
- Integers on `/method` are grouped with a narrow no-break space instead of `toLocaleString`, so Spanish text never contains ambiguous commas (tested).
- **Bundle finding:** the landing's initial JS jumped to 96.4 KB gz (budget 90) after adding messages. Cause: `noteText` looked messages up dynamically (`messages[key]`), which defeats tree-shaking, so *every* message of the site entered the landing bundle, and each new message page grew it. Replaced by an explicit table (`noteMessages.ts`) with a test that it covers every `note_*` key in both languages. Landing initial JS is now **75.1 KB gz** (22 modules), below even the pre-redesign 88.5 KB. Rule going forward: never index the paraglide namespace dynamically in code reachable from the landing.
