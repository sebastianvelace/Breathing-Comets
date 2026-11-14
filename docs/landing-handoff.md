# Landing handoff (BUILD §10, step 10)

Status as of 2026-11-14 ~12:30 COT. Nothing committed, pushed or deployed by the landing agent.

## Approved vs pending at a glance

| Item | Status | Evidence |
|---|---|---|
| Landing sections: hero, §1–§6, footer (EN default + full ES at `/es`) | Done | Visual check desktop 1440×900 and mobile 375×812, EN/ES, light and dark |
| Primary link "Open the sky" → `/explore?target=barnard&ui=story` (`/es/explore?…` in ES via `localizeHref`) | Done | E2E `hero opens the Barnard story…` and existing `story.spec.ts` (3/3) |
| Five targets → real Explorer stacks | Done | E2E opens all five `/explore?target=<slug>&ui=story` and waits for frames |
| Real plates rendered from the published packages | Done | `pipelines/landing_media.py`; unit tests compare stretch, grid and obs_id against the SPXF headers |
| `npm run check` on landing files | 0 errors / 0 warnings | See "Verification" (current full run fails in coordinator Aladin files) |
| `npm run build` | Passed | `✔ done`, prerendered `index.html` and `es.html` |
| Initial JS < 90 KB gz | **70.4 KB gz measured** (13 modules referenced by `index.html` / `es.html`, gzip -9) | Not the Rollup visualizer: measured by summing the modules the prerendered HTML loads |
| LCP < 1.5 s (Lighthouse mobile) | **Not verified with Lighthouse** (not installed; no install authorised) | Proxy only: 0.79–0.90 s, see below |
| Hero with 3I/ATLAS plate | **Pending (coordinator)** | Barnard stand-in, labelled on the page as not 3I |
| §4 comet gas, §5 comet validation | **Pending (coordinator packet)** | Honest pending states; auto-fill tested with a mocked packet |
| GSAP ScrollTrigger CO₂ ink-in on hero | **Not implemented** | Needs the 3I gas map; no data, and GSAP would add initial JS |

## Files created or modified (all inside the assigned scope)

- `apps/web/src/routes/+page.svelte` — composes the page; `<head>` with title, description, canonical, `hreflang` en/es/x-default, preload of the hero plate, OG tags; masthead with section nav and EN/ES switch; shared section grammar scoped under `.landing`.
- `apps/web/src/lib/components/landing/`
  - `landing.ts` — media manifest typing, `isoDate`, `fmtLam`, `fmtSciUnicode` (decimal point, Unicode exponents), `gaiaPixel` (reuses Explorer `propagate`/`worldToPixel`), 3I packet contract, strict validator and lazy loader.
  - `Plate.svelte` — framed plate: `--plate` field, 1 px `--rule` frame, registration "+" marks, angular scale bar computed from `pixel_arcsec`, N↑ E← mark only when orientation is known, mono caption + credit.
  - `Hero.svelte` — "The sky is breathing."; one real frame per visit, 6 s loop, Pause/Play button, paused when off-screen, never autoplays with `prefers-reduced-motion`; remaining frames preloaded only after `load` + idle. Swaps to 3I frames automatically when the packet is valid.
  - `BlinkSection.svelte` (§1) — A/B/Blink buttons on a 28 px crop around Barnard's Star; Gaia DR3 4472832130942575872 propagated to each date (open reticles with dark halo, open-head arrow drawn once in 520 ms); SVG images mounted only near the viewport.
  - `DiffSection.svelte` (§2) — before/after range slider: raw B − A (largest λ mismatch among well-covered frames) versus the published Diff λ frame; same ±5σ map and σ for both; discrete legend swatches (no gradients).
  - `SpectrumSection.svelte` (§3) — lazily fetched ε Indi B deblended spectrum (`/data/targets/eps-indi-b.json`), bands from `bands.json` (§12.3) as accessible toggle buttons; each band links to an object or to §4. No uPlot.
  - `CometsSection.svelte` (§4), `ValidationSection.svelte` (§5) — comet parts render from the 3I packet only; §5 also shows the real photometric check from `calibration.json` (J/H/Ks/W1/W2, n, ratio ± σ, method string).
  - `TargetsSection.svelte` (§6) — five mini-plates in a horizontal scroll rail inside the container; field notes via the existing `noteText` translations, each card with its caveat.
  - `LandingFooter.svelte` — data credits, "not a NASA product" statement, Use of AI note, provenance of the plates, links (Explorer, §5, GitHub, EN/ES).
- `apps/web/messages/landing/en.json`, `es.json` — 114 keys each, all `landing_`; identical key and parameter sets (unit-tested).
- `apps/web/static/media/landing/` — 14 lossless WebP (147×147, 251,829 bytes total incl. JSON) + `landing-media.json`.
- `pipelines/landing_media.py` — generator for the above (Ruff: all checks passed).
- `apps/web/tests/landing.test.ts` — 10 Vitest cases.
- `apps/web/e2e/landing.spec.ts` — 11 Playwright cases.
- `docs/landing-handoff.md` — this report.

## Data and media rules followed

- Plates come only from `static/data/targets/<slug>/` (manifest, default-detector stack, `D4.diff.spxf.gz`, `gaia.json`). No research script was run; the five packages were not modified.
- Each stack uses its own common `stretch_hint` with the Explorer mapping `asinh(20x)/asinh(20)`; OVERFLOW (bit 1) is painted white **before** NaN/NODATA; north up, east left (grid row 0 is south, so rows are flipped); lossless WebP and `image-rendering: pixelated`, so no smoothing or resampling.
- Poster frame = the frame with the most valid pixels; hero/§1 frames = best-covered frame per visit (7 visits, D4).
- The raw subtraction is labelled "Raw B − A" everywhere and never called Diff λ; Diff λ is the coordinator's published product for the same frame (`diff_available: true`, `reference_count` 5).
- No measurement is written by hand: field-note values, caveats, calibration ratios, frame metadata, Gaia ids and positions are read from JSON and passed as Paraglide parameters. A unit test rejects standalone numbers in the landing messages except narrative/instrument facts (102 colors, 1930, 1–5 µm, 1.35 µm, 4.5 µm, 0.7, §12.3).
- No `toLocaleString`; decimals via `toFixed`/`toPrecision`; no CSS `text-transform: uppercase` (uppercase strings are written as such and contain no µ).
- Credits: "SPHEREx: NASA/JPL-Caltech/IRSA (DR1 + QR3, L2 l2b-v27)" and "Gaia DR3: ESA/Gaia/DPAC" on plates and footer; SIMBAD for positions; explicit "independent Space Apps project, not a NASA product". No NASA logos.

## Verification observed

- `npm run check` with only my changes present: `COMPLETED 1603 FILES 0 ERRORS 0 WARNINGS 0 FILES_WITH_PROBLEMS`.
  - Latest full run (after the coordinator added Aladin files): `COMPLETED 1611 FILES 11 ERRORS 4 WARNINGS 2 FILES_WITH_PROBLEMS`, all in `src/lib/components/AladinView.svelte` and `AladinFrame.svelte` (missing messages such as `reference_sky`, `hips_channel`, `aladin_loading`; `store_rune_conflict` warnings). None in landing files. Not touched.
- `npm run build`: passed (`✔ done`).
- `npx vitest run tests`: `2 passed (2)` files, `39 passed (39)` tests (10 landing + 29 existing). Note: a bare `npx vitest run` also collects `e2e/*.spec.ts` and fails with "Playwright Test did not expect test() to be called here" — pre-existing configuration, not changed.
- `PLAYWRIGHT_BROWSERS_PATH=/tmp/breathing-comets-browsers npx playwright test e2e/landing.spec.ts`: `11 passed (13.4s)`. The default browser cache is missing (`Executable doesn't exist at ~/.cache/ms-playwright/chromium_headless_shell-1248/…`); the coordinator's earlier download in `/tmp` was reused, nothing installed.
- Existing `e2e/story.spec.ts` against the new landing: `3 passed (8.9s)`.
- Covered by E2E: CTA name/href and navigation to ≥ 10 Barnard frames; five Explorer entries load frames; every field-note card has a caveat; all internal links return 200 and anchors exist; 3I missing → `data-status="missing"`, no comet image, stand-in label, PENDING in §5; 3I mocked → measurement `2.50 × 10²⁶`, caveat, within/outside range rows, hero switches to 3I alt; hero loop advances, Pause freezes it, reduced motion keeps frame 0; keyboard: blink B, slider Home, CH₄ band → `/explore?target=eps-indi-b&ui=story`; focus ring `solid 2px`; `/es` lang, Spanish H1, `/es/explore` CTA, `10.6 ± 0.4″/año`, no decimal commas; mobile 375 px `scrollWidth ≤ clientWidth` on `/` and `/es`.
- Visual (in-app browser, production preview): desktop EN light and dark, mobile ES light. Fixed during review: Gaia crosses invisible on the saturated core (now haloed open reticles), `.num` class collision in §5, mobile horizontal overflow (absolutely positioned `sr-only` text escaping the rail; cards are now `position: relative`).
- LCP proxy (not Lighthouse): Playwright + CDP on the local preview, 412×823 mobile, 150 ms RTT, 1.44 Mbps down, CPU ×4, cache disabled, 3 runs each: `/` 816–900 ms, `/es` 792–816 ms; LCP element is the hero paragraph (the 147 px plate is upscaled, so its intrinsic area is smaller). Real Lighthouse on Pages/CDN is still required.

## Pending contracts and integration dependencies (coordinator)

1. **3I packet** `/data/comets/3i-atlas/landing.json` (contract in `landing.ts` → `CometPacket`, validated strictly; any mismatch is shown as pending). When published, the hero, §4 and §5 fill in without code changes. Requested additions to the contract:
   - `plates.pixel_arcsec` and `plates.north_up` (or a `grid`) — without them the 3I plate has no scale bar or N/E mark (deliberately hidden rather than guessed);
   - `width`/`height` per image to avoid layout shift;
   - optional `lead` index if the first `measurements` entry should not be the big figure;
   - packet labels/caveats are shown verbatim (English) in `/es`: add `label_es`/`caveat_es` or message keys if they must be translated.
2. **3I gas map / CO₂ ink-in** (§10.5 hero ScrollTrigger and §4 "plate with gas map"): not implemented; no data. Would need a gas-map image in the packet; GSAP should be loaded lazily to keep initial JS < 90 KB.
3. **29P CO** row of §5 is expected to arrive inside `validation`; nothing is hard-coded.
4. **Pages headers**: consider long cache for `/media/landing/*` (immutable per generation) in `static/_headers` (outside my scope).
5. **`/comets` and `/method`**: "Meet the comets" points to `#comets` and the footer "How we check" to `#validation` because those routes do not exist yet. Re-point when step 11 ships.
6. **H I lines** in §3 have no demonstration target among the five; the copy says so. If a target with Paβ/Brα is added, map it in `SpectrumSection.svelte` `info()`.
7. **check**: restore 0/0 by adding the coordinator's Aladin messages (not a landing issue).
8. **Regenerate media** after any change to a target package: `python pipelines/landing_media.py` (reads only `static/data/targets/`).
9. Tooling notes: the visual check used a temporary `vite preview` on port 4190 (stopped). Restart `vite preview` after every build: a stale server serves an old asset manifest (unstyled page).
