# Findings log (2026-11-14)

Everything found while integrating steps 8–11, with evidence and what was done. "Open" means it still needs a decision or work.

## 1. Product defects and fixes

| # | Finding | Evidence | Action | State |
|---|---|---|---|---|
| F1 | **Tracked stacks fail beyond ~4 days.** `tracked_rows` sampled Horizons every hour; more than ~100 JD values in the URI are truncated, and the call fails as `EphemerisUnavailable` / HTTP 503 `UPSTREAM_UNAVAILABLE`. | `ephem.horizons_positions("2025 N1", linspace(60886, 60903, n))`: n = 5 and 60 ok; 150 and 409 failed in ≤ 1 s, with astroquery warning "uri ... very long and might have been truncated". | `horizons_positions` now splits into chunks of 40 epochs; `tracked_rows` samples every 6 h (D5 field is 3.5°, comet moves ~0.5°/day). `tests/test_horizons_chunks.py` (2 passed). | **Fixed and deployed to Fly on 2026-11-14** (see section 9). |
| F2 | **29P cannot be tracked by designation.** Horizons answers "no ephemeris" for `29P`, `29P;`, `DES=29P;` and the full name (ambiguous apparition records). The resolver's SBDB `des` is `29P`, so `/v1/resolve?q=29P` also fails. | Four designations failed, numeric SPK id `90000393` returned (173.1519, −2.738) at MJD 61025.2. | Stack fetched with `track=90000393`; documented in `static/data/comets/29p-schwassmann-wachmann/provenance.json`. | **Fixed and deployed 2026-11-14; public /resolve?q=29P returns 200 with track DES=29P; CAP.** |
| F3 | **Public API blocks the E2E origin.** `services/api/fly.toml` sets `SPX_ALLOWED_ORIGINS` to production + `localhost:5173`, overriding the code default that includes `127.0.0.1:4183`. Two live-click E2E tests failed locally with `blocked by CORS policy`. | Console capture; `curl -H 'Origin: http://127.0.0.1:4183'` returned no `access-control-allow-origin`. | Tests built against the local API (`VITE_API_BASE`) pass 26/26. | **Fixed and deployed 2026-11-14:** explicit `http://127.0.0.1:4183` allowlist entry; public response echoes the expected Access-Control-Allow-Origin. |
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

## 9. Fly deployment of the Horizons fix (2026-11-14)

- Command, from the repo root: `fly deploy . -a breathing-comets-api -c services/api/fly.toml --dockerfile services/api/Dockerfile --ha=false`. Image `deployment-01M7DQ56PM0SKP62HE6VB2C19N` (339 MB), rolling update of the single machine `847222a27700d8` (version 3 → 4). The machine ended the deploy in `stopped` (auto-suspend); the first request woke it: `/v1/health` 200 in 18.0 s (cold start), `ok: true`, 809 593 index rows, `cal-swcs-v5-2026-191`.
- Verification of the fix on the public API: the 17-day 3I window that used to fail now returns `200`, 46 516 B, **6.8 s** cold; the 11-day 29P window (`track=90000393`) returns `200`, 113 570 B, **4.3 s**. Decoded content equals the stacks stored in the repo: 14 and 34 frames, same obs_id/MJD/λ per frame, identical pixels and flags (`array_equal`), same stretch. The gzip bytes differ only in the header timestamp. This also shows the tracked-stack path is reproducible.
- `/v1/resolve?q=3I` works; `/v1/resolve?q=29P` still returns `RESOLVE_FAILED` (finding F2 stays open).
- Cold latency: 4.3–6.8 s for tracked stacks; the 4 s target (F4) is still not met in general.
- Production E2E after the deploy: first full run `34 passed, 2 failed` (`comets.spec` keyboard selection and `comet-detail.spec` sweep); both passed when re-run alone. Same cause family as section 7: acting on a prerendered element before Svelte hydrates, under load. `Enter` on a chart point toggles the selection, so it cannot be retried; those tests now wait for `networkidle` first. Two consecutive full runs: `36 passed (2.1m)` and `36 passed (2.0m)`.

## 10. Resolver for periodic comets (2026-11-14)

- **Cause:** `/v1/resolve` took the SBDB `des` (`29P`) and sent it to Horizons, which has several apparition records for numbered periodic comets and answers "no ephemeris". Second cause for fragmented comets: SBDB answers **HTTP 300** (`240P` matches `240P` and `240P-B`), which `raise_for_status` turned into a misleading `UPSTREAM_UNAVAILABLE`.
- **Change (`known.py`):** `track_candidates` tries the plain designation, then `DES=<des>; CAP` (closest apparition) for periodic comets, then the SBDB `spkid`; `first_working_track` moves to the next candidate only when Horizons says "no ephemeris", never when the service is unavailable; `pick_sbdb_match` accepts a 300 answer only if exactly one record's `pdes` equals the query and otherwise lists the matches. 5 tests in `tests/test_resolve_periodic.py`.
- **Live results (local API):** `29P` → `track "DES=29P; CAP"`; `24P` → `DES=24P; CAP`; `235P`, `12P`, `3I`, `C/2022 N2`, `P/2018 VN2` resolve with their plain designation; `240P-B` resolves; `240P` and `73P` now fail with `RESOLVE_FAILED` and a message naming what was tried and suggesting a fragment designation; `73P-B` has no Horizons record under that name.
- **Which 29P record is better?** Horizons gives `90000393` and `DES=29P; CAP` positions 3.0″ apart (different orbital solutions). Flux-weighted centroids in the real D5 frames, 16–21 Dec 2025: `90000393` mean offset 0.63 px (median 0.51, 34 frames); `DES=29P; CAP` 0.44 px (median 0.37, 30 frames). Both centre the comet within about half a pixel (3″); the difference is small against the noise, so it is **not** claimed as an improvement. The stored 29P stack (`track=90000393`) is unchanged and documented as such.
- `CAP` is relative to the time of the request, so a track string is only meaningful alongside the epoch it was resolved at; it is part of the stack cache key.

## 11. `/about` and items that need the user (2026-11-14)

- `/about` (EN/ES, six sections): what it is, the challenge, where to start, data and credits (8 sources with providers and use), use of AI, software and fonts. Figures come from data (102 channels from `channels.json`, comet count from the atlas). No team members or personal details were invented; none exist in the repository.
- **Deliberately left out, needs the user:** (1) the declaration of prior research, which BUILD 16 says the user writes by hand (the page and landing footer only point to the "Use of AI" section of the submission); (2) names of team members and the virtual site, if wanted on the page.
- **Licence finding (open):** the repository has **no `LICENSE` file**, so the page states only the licences verified in `node_modules`: Newsreader and IBM Plex are OFL-1.1, Aladin Lite is **GPL-3**. Because Aladin Lite is bundled in the build (loaded in an iframe in Lab mode), the licence of this site's own code should be chosen with that in mind; the page says "source code is public on GitHub" and claims no licence.
- Attributions checked against the sources: 2MASS is credited to UMass and IPAC/Caltech and WISE/NEOWISE to NASA/JPL-Caltech (an earlier draft lumped them under IPAC); the Aladin and Astropy citations are those given in BUILD 16 (authors and year only, no venue invented).
- Test: `about.spec.ts` (4 E2E). Landing initial JS 73.6 KB gz.

## 12. One unexplained intermittent failure (2026-11-14)

- After the `/about` deploy, a full production run gave `39 passed, 1 failed`: `story.spec.ts › shared URL restores the same observation in a fresh context`. The failure message was not captured. The test passed alone twice and in the next full run (`40 passed (1.5m)`). It presses `Home` then `ArrowRight` twelve times on the timeline right after the frame count appears, so a timing cause (progressive frame upload or late hydration, the families in sections 7 and 9) is plausible, **but this is not proven**. Not changed; if it recurs, capture the error before touching the test.

## 13. Landing: call-to-action flow (2026-11-14)

- **Weakness found (measured, not assumed):** the page is ~9 190 px tall at 1440 px wide and the only calls to action were the two hero buttons. After the hero a reader had no way to act without scrolling back, and the page ended on a text-only footer.
- **Changes:** (1) a masthead button "Open the sky →" that fades in only after the hero has left the viewport (also on phones; at 375 px it fits between the brand and the language switch, checked by test); (2) a closing band `#start` ("Now open the sky.") with the same primary and secondary actions plus four entry routes (Barnard's Star, WISE 0855−0714, RW Aurigae, 3I/ATLAS) each with a one-line description taken from the existing field notes; (3) the masthead background is more opaque (93 %) because at 78 % it looked grey over the light bands.
- **Side effect handled:** "Open the sky" now names three links, so the strict role selectors in `landing.spec.ts` and `story.spec.ts` were pointed at the existing `data-testid="open-sky"`.
- **Preview artefact worth knowing:** a `vite preview` left running across a rebuild serves 404 for the new hashed chunks and the page never hydrates (the ribbon stayed at `scaleY(0.04)`). This looked like a ribbon bug and was not; restart the preview after every build.
- Verified: svelte-check 0 errors / 0 warnings, Vitest 44 passed, local E2E landing + story 16 passed (3 new assertions), initial landing JS 72.7 KB gz. Not re-measured: Lighthouse LCP (still not installed).

## 14. Lighthouse, LCP and explorer layout shift (2026-11-14)

Lighthouse 13.6 (installed outside the repo, Playwright's Chromium), against production.

- **Before:** landing mobile LCP 3.0–3.3 s, desktop 1.3 s; explorer mobile CLS 0.13–0.146 and TBT ~0.9–1.0 s. Accessibility, best practices and SEO 100 on all three pages.
- **Cause of the slow mobile LCP (mine):** the LCP element was hero text, and kicker, headline words, lede and buttons all started at `opacity: 0` with delays up to ~1.9 s. Lighthouse reported 743 ms of "element render delay". Fix: entrance animations now move and un-blur but never start invisible. After deploy: mobile 1.5–2.7 s over four runs (noisy, throttled slow-4G profile), desktop 0.8–1.3 s. **The 1.5 s budget is met on desktop and not reliably on throttled mobile.**
- **Cause of the explorer CLS:** while the stack loads the page is short, so the footer and (on phones) the field notes sit inside the viewport and jump down when timeline and metadata mount. Fix: `main` reserves `100svh` and the notes render on phones only once the plate has frames. Local Lighthouse: 0.136 → 0.062.
- **Open:** explorer mobile TBT ~0.9 s (not investigated; candidates are stack decoding and WebGL upload on the main thread).
- **Explorer fold:** plate + playback controls now fit one screen (measured: controls end at 840/900, 657/720, 1021/1080 px); before, the timeline was below the fold at 1440×900.

## 15. Onboarding tour and visual redesign (2026-11-14)

- **Tour** (`Onboarding.svelte`): six steps (search, modes, plate, timeline, field notes, header). The rest of the page is darkened by one very large shadow around a rounded spotlight; a click-catcher stops the dimmed page from being operated. Keyboard: arrows, Escape, Tab is kept inside the card, focus returns to the opener. Steps whose element is not displayed are skipped (no Story/Lab switch on phones).
- **Offered, not forced:** a first visit shows a small dismissible card after 2.5 s (remembered in `localStorage`); `?tour=1` and the "How it works" button start it. A modal on every first load would also have blocked every existing E2E flow.
- **Redesign requested by the user:** Geist / Geist Mono replace Newsreader and IBM Plex (both OFL-1.1, checked in `node_modules`; the Latin Geist file is 29 KB against 129 KB for Newsreader); interface accent is a galaxy blue (`--accent`), pill buttons, rounded panels instead of hairlines, § numbers and the hero kicker removed, the hero grid replaced by `Starfield.svelte`.
- **Starfield cost:** static SVG dots and four hand-placed constellations drifting as whole layers with CSS transforms, plus seven twinkles; no canvas, no `requestAnimationFrame`, disabled under reduced motion.
- **Data colours (changed afterwards at the user's request):** the CO₂ band and positive Diff λ moved from orange to star yellow (`--co2` `#a88700` light / `#f2d24b` dark, `--co2-on-plate` `#f5d54a`). Yellow was chosen over pink because cyan–yellow stays distinguishable under red-green colour blindness, while cyan–pink does not. Changed in three places that must agree: the CSS tokens, the GL colour table (`src/lib/gl/renderer.ts`) and `pipelines/landing_media.py` (`GOLD`). The pipeline was re-run: only the two diverging Barnard plates and the manifest's date/byte counts changed; the other 26 files came out byte-identical. The Gaia marker in Lab (Aladin) and the blink arrow use the blue accent. `docs/BUILD.md` §design tokens still lists the old orange: that document was not edited, this is a recorded deviation.
- **Bug caught before commit:** a rule meant to lift header/main/footer above the starfield also matched the tour container and cancelled its `position: fixed`, making the tour invisible; the tour screenshots failed and the rule was narrowed.
- The explorer keeps a night-sky theme in both colour schemes (it displays dark plates). `/comets`, `/method`, `/about` and `/neo` inherit the new tokens and font but were **not** restyled panel by panel.
- Tests: `tour.spec.ts` (5 E2E). Local: svelte-check 0/0, Vitest 44, E2E 45 passed + the 2 live-API tests that only pass against production.
- **After the redesign, production Lighthouse (two runs each):** landing mobile LCP 1.5–1.6 s, perf 94–95; desktop 0.6–1.2 s; explorer mobile CLS 0.04, TBT 0.73–0.86 s (still open). Accessibility 100 on all. One audit flagged `label-content-name-mismatch` on the explorer language link (`aria-label="Language"`, visible text "ES"), which predates this work; the label now starts with the visible text. The "?" tour button keeps its full name through visually hidden text instead of an `aria-label`.
