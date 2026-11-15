# Build status

All results below describe observed verification. The user confirmed that the recorded research-script execution was authorized. The current step table supersedes historical progress estimates below.

## Preflight

- Started 2026-11-14 at 09:04 COT; steps 1–7 retain their planned scope.
- Node 24.14.1; npm 11.11.0; uv 0.11.15; Git 2.43.0; Fly CLI 0.5.8.
- GitHub account verified: sebastianvelace. Product remote contains the preserved bootstrap commit baa2d91.
- System Python is 3.12.3; Python 3.13.13 installed and verified in /tmp/breathing-comets-python/cpython-3.13.13-linux-x86_64-gnu/bin/python3.13.
- The restricted filesystem initially exposed an empty .git directory and Git fell back to the parent. Rechecked outside restriction: the product has its own repository, correct origin and main branch. Never operate on the parent repository.

## Steps

| Step | Deliverable | Status | Commit | Verification | Open issues |
|---|---|---|---|---|---|
| 1 | Repository and templates | Done | d2faac2 | Push succeeded; identity exact; prohibited messages 0; only main; hooks .githooks | Approved bootstrap exception: retain baa2d91. |
| 2 | Deployed skeletons | Done | 7d7f4d9 | Static build passed; local and public Fly health HTTP 200 with ok true; single machine | Node types approved and installed; type check passes with 0 errors and 0 warnings. Pages build passed; apex active with SSL; API custom domain HTTP 200. www redirect enabled; HTTP 301 preserves path and query. |
| 3 | Static data | Done | 3d98b0a | 100 passed in 0.31s; du 364K; copied files byte-identical | No scientific results recalculated. |
| 4 | Scientific core | Done | 8f9b92b + c0b908b | Golden model passes; all 25 original assertions retained; full network suite 9 passed | Slow independent table acquisition is bounded and ETag-validated. |
| 5 | Five target precomputation | Partial | cfe29d7 | All five targets, six detectors each, plus five Diff λ stacks; real TypeScript parser passed | R Dra D6 baseline acceptance remains failing; source coverage ends June 2026. |
| 6 | Story Explorer | Done | 21ca8f1 + a2c5bb4 | 28 Vitest; check 0 errors/warnings; build; 3 local and 3 public E2E passed | Arbitrary pixel spectrum belongs to step 7. |
| 7 | Live API | Partial | 0cb0cc3 + bf9e845 | Deployed 29P resolve 200; real API stellar ratios and live-click checks pass | General cold acquisition >4 s; JPL asteroid identification unavailable. |
| 8 | Lab and Aladin | Done | 2c8ccc3 | Real frame-85 tiles, visible attribution and live pixel spectra verified | No current feature blocker. |
| 9 | Small-Body Lab | Done | 8f9b92b | All 50 absolute validation pairs; integrity and interval/tier E2E pass | Ratios retain original export rounding, stated in UI. |
| 10 | Landing | Partial | fdee401 + 8c78225 | Actual 3I plates; EN/ES and accessibility; deployed mobile LCP 1.410 s, performance 98 | No continuum-subtracted gas map; no invented substitute. |
| 11 | Comets, method, about and Spanish | Done | d7fe353 + follow-up | Atlas, 3I/29P details, method and about pages verified EN/ES | Unsupported 3I August H2O remains withheld. |
| 12 | Final tests | Partial | 56512f8 | 50 production browser checks; 9 network checks; 47 frontend unit checks pass | Known R Dra failure and cold-acquisition budget remain explicit. |
| 13 | Written submission | Prepared | a4526b6 | Generated from product JSON; one user-disclosure marker | Video is user-owned; user writes prior-work disclosure and supplies video URL. |
| 14 | Freeze | Pending | — | Not run | — |

## Step 1 verification and blocker

- `gh repo view` first reported an empty product repository. A subsequent inspection found published commit `baa2d91c67bc761f2edc677bea76f7cc2b7edf80` (`first commit`), containing only README.md. No product commit or push was made by this session.
- Initialization attempt stopped at `error: remote origin already exists.` No remote was changed.
- Existing author and committer: `sebasvelace <sebastianvelace@gmail.com> | sebasvelace <sebastianvelace@gmail.com>`.
- Existing commit message contains zero prohibited attribution matches.
- Remote heads: only `refs/heads/main`.
- Required templates and build guide are prepared; source Git section is unchanged.
- No application code, dependency packages, science calculations, or deployment changes made.

## Approved bootstrap exception

The user explicitly approved retaining published bootstrap commit `baa2d91` and continuing with required templates in the next commit. No history rewrite is authorized or needed.

## Step 2 attempts

- Local API smoke check: HTTP 200; `ok: true`, `index_rows: 0`, `index_built: false`, `collections: []`, `swcs: null`.
- Fly app accessible; volume `spx_cache` created in iad, size 5 GB. IPv4 and IPv6 allocated.
- First deployment failed before building: `Error: failed to fetch an image or build from source: dockerfile '/home/sebasvelace/Breathing-Comets/services/api/services/api/Dockerfile' not found`. Retry uses explicit root build context and absolute Dockerfile path.
- Cloudflare dashboard requires sign-in; no Cloudflare credentials are available in the current environment. Pages, DNS and custom-domain certificate verification remain pending.

- First web type check failed with `svelte-check found 6 errors and 0 warnings in 3 files`: generated Paraglide modules were missing before Vite compilation. Check/prepare scripts now explicitly run the installed Paraglide compiler first, with the same locale strategy as Vite. No checks were removed or relaxed.

- Second web type check failed with `svelte-check found 1 error and 0 warnings in 1 file`: `src/lib/paraglide/server.js:105:50 Error: Cannot find name 'async_hooks'. Do you need to install type definitions for node? Try npm i --save-dev @types/node and then add node to the types field in your tsconfig.` The generated server module needs Node type declarations. `@types/node` is outside the approved dependency list; not installed. Type checks remain failing; no exclusion, stub declaration or relaxed assertion was added. Continue with the next independent step as instructed.

- Second Fly deployment succeeded: one app machine `847222a27700d8`, image `deployment-01M7D6NVJMD9KWJD2SGT5CWWSN`. Public `https://breathing-comets-api.fly.dev/v1/health` returned HTTP 200 and `{ "ok": true, "index_rows": 0, "index_built": false, "collections": [], "swcs": null }`; data-version header present.
- `npm run build` passed and wrote the static site to `apps/web/build`. This does not resolve the failing type check.
- The custom-domain certificate was created; DNS setup is pending: A api → 66.241.125.132 and AAAA api → 2a09:8280:1::1fc:6fed:0, DNS only.

## Step 3 verification

- Copied the published static result package, reference positions and channels, plus the compact exposure and S3 key indices. No scientific scripts executed.
- `python -m pytest tests/test_static_data.py -q`: `100 passed in 0.31s`. All expected values from the task remain unchanged.
- `du -sh apps/web/static/data`: `364K`; logical size 261,480 bytes.
- Every original exported file was verified byte-identical to its source after copying.
- Step 2 push checks: exact identity, prohibited messages 0, sole remote branch main.
- Exact custom-domain probes failed: `curl: (6) Could not resolve host: breathingcomets.org` and `curl: (6) Could not resolve host: api.breathingcomets.org`. The working Fly hostname is distinct from the pending custom domain.

## Step 3 repository verification (historical)

After push `3d98b0a`:

```text
sebasvelace <sebastianvelace@gmail.com> | sebasvelace <sebastianvelace@gmail.com>
0
3d98b0a1915f04fdf0eafb53b3355ae246944db0 refs/heads/main
```

Working tree was clean. All 25 approved direct npm dependencies are pinned exactly. A registry lookup confirmed `@types/node@24.19.2` exists; adding it as a development dependency requires user approval because it is outside BUILD §3.2. No extra package was installed.

Next: obtain approval for the Node type declarations, restore a passing web type check, finish Pages/DNS after Cloudflare sign-in, then implement step 4.

## Approved Node type declarations

The user approved `@types/node@24.19.2` as an additional development dependency. Installed exactly that version. `npm run check`: `svelte-check found 0 errors and 0 warnings`. Cloudflare account access is now authenticated and verified; no sign-in blocker remains.

## Step 4 in progress

- Implemented the eleven required core modules plus ePSF helpers and path configuration; added resolve endpoint integration. No research scripts executed.
- Ported all reference assertions unchanged (AST comparison: 25 of 25). Independent Astropy reads use the approved HTTPX transport instead of fsspec HTTP, which otherwise requires an additional aiohttp package; removed an unused pandas import. No additional dependencies installed.
- Fast suite: `131 passed, 7 deselected in 4.29s`.
- First network suite: `3 failed, 4 passed, 131 deselected in 152.30s (0:02:32)`. Exact failures: `tests/test_core.py::test_lam_poly[5-0.001] - TimeoutError`; `tests/test_reference.py::test_epsf_row_read_equals_full_table - TimeoutError`; `tests/test_reference.py::test_epsf_row_detector3_uses_11x41_grid - TimeoutError`. All failed at calibration map download `data = bytes(await response.bytes_async())` within the 30-second acquisition bound. Switching calibration acquisition to concurrent byte ranges; calibration resolution and acceptance thresholds remain unchanged.
- Verified real DR1 physical HDU layout: FLAGS RICE_1, EPSF 441 rows in D4; raw IMAGE and decompressed FLAGS row reads returned shape (3, 2040).
- Pages GitHub connection is prepared for only sebastianvelace/Breathing-Comets. The install screen requests read/write administration, checks, code, deployments and pull requests. Installation has NOT been confirmed; action-time approval is required.

- Second network suite: `2 failed, 5 passed, 131 deselected in 116.64s (0:01:56)`. Exact failures: `tests/test_core.py::test_lam_poly[5-0.001] - TimeoutError` and `tests/test_reference.py::test_epsf_row_read_equals_full_table - TimeoutError`, both on D5 calibration byte-range acquisition (4,194,304-byte ranges). D3 acquisition and EPSF grid comparison passed on the second run. No acceptance assertion or threshold was changed. After two unsuccessful suite runs, step 4 remains partial; further acquisition work is deferred to step 5 preparation as instructed.
- Verified D3 and D5 calibration keys exist: S3 returns HTTP 206 for bytes 0–79 and confirms 33,312,960 bytes each; listing the v5 prefix returns all six detector maps. No replacement or invented calibration is used.
- Most recent fast suite: `131 passed, 7 deselected in 3.28s`; Ruff: `All checks passed!`. This includes Python-to-TypeScript SPXF round trips with/without shuffle, gzip and variance, gnomonic coverage, visit sampling, proper motion, exact WISE coordinate resolution, and interpolation checks.
- Still pending in step 4: independently verify a legacy QR2 layout and implement the slow golden 3I physical-model acceptance check when the comet model is available. Horizons integration has not yet been exercised live.

## Deployment follow-up

- User completed GitHub installation in the browser. Cloudflare confirmed access to the selected product repository.
- Created CNAME `api` → `breathing-comets-api.fly.dev` with proxy off (DNS only). Fly certificate is issued, verified and active. `https://api.breathingcomets.org/v1/health` returned `ok: true`, `index_rows: 809593`, `index_built: true`, collections dr1/qr3.
- Deployed core commit d707949 as image `deployment-01M7D8WWTB6NXT3VJASY8ZT82J`. Public WISE coordinate resolve returned the expected 2026 position and epoch_warning.
- First Pages build failed before the configured npm command: automatic Python dependency discovery ran `pip install .` at the monorepo root and returned `error: Multiple top-level packages discovered in a flat-layout: ['data', 'apps', 'packages', 'services']`. Preparing the documented setting that disables automatic dependency installation; the requested build command already explicitly runs npm ci.
- Preparing step 5: HTTPX fetched the exact D5 bytes 0–4194303 successfully (HTTP 206, 4,194,304 bytes, 4.669 s). This supports a bounded HTTPX transport fallback for the stalled bulk calibration acquisition; no data substitution.

## Step 5 findings and fixes

- Bulk calibration acquisition through validated HTTPX ranges succeeded for all six detectors, each 2040×2040. D5 completed in 5.26 s. The following network suite passed: `7 passed, 131 deselected in 54.42s`.
- Barnard generated all six detector stacks; default D4 has 24 frames from 7 visits, 2025-08-27 through 2026-09-02. Actual Gaia counterpart 4472832130942575872 shifts 1.7167855535980503 output pixels between those epochs.
- First real-stack TypeScript parse failed: `SyntaxError: Unexpected token N ... lam_um:NaN ... is not valid JSON`. Root cause: source intensity NaN at saturated pixels was incorrectly applied to the wavelength map and the edge flag. Fixed by sampling center CWAVE/CBAND independently of flux, using detector geometry for edge, upgrading cached metadata from the full maps, and rejecting nonfinite header JSON. Pixel data are preserved.
- Added regression coverage for saturated-center wavelength and edge handling, plus invalid SPXF header rejection. Fast suite: `133 passed, 7 deselected in 3.54s`.
- The step 3 one-megabyte check now explicitly measures the original exported JSON files; step 5 binary media have their separate 6 MB/detector and 25 MB/target budgets. The one-megabyte expected value and all scientific expected values remain unchanged.
- First Pages retry using documented SKIP_DEPENDENCY_INSTALL=1 succeeded. Pages hostname returned HTTP 200. Apex domain is active with SSL in the dashboard; live HTTP probes pending confirmation.

## Step 5 full-package acceptance

- Full-package suite initially failed one acceptance: `1 failed, 142 passed, 8 deselected in 2.56s`. Exact assertion: `test_r_dra_samples_full_baseline`: last selected date `2026-06-12` was before required `2026-09-01`. Expected baseline unchanged.
- Found a sampling edge case: a visit receiving one frame used linspace with one sample, always selecting its first exposure. The selector now preserves global temporal endpoints and uses actual CWAVE metadata before choosing frames within visits. Added a regression for a long continuous last visit; rebuilding R Dra.
- Refreshed Gaia catalogs preserve missing proper motion/parallax as null, rather than inventing zero measurements. Counterpart matching only propagates stars with measured proper motion.
- All 25 original reference assertions remain unchanged. Latest core fast suite before adding visit regression: `134 passed, 8 deselected in 3.20s`; latest network suite: `8 passed, 133 deselected in 44.95s`, including independent QR2 PSF-cube and DR1 compressed-FLAGS comparisons.
- Live probes to `https://breathingcomets.org` and `/es` both returned HTTP 200.

## Step 5 completed artifacts and remaining acceptance

- All five target jobs finished with actual-lambda sampling: Barnard 12,174,027 bytes; eps-indi-b 11,117,865; WISE 0855 11,111,673; RW Aur 11,637,931. All per-detector files are below 6 MB and target totals below 25 MB. All 35 real stacks parse in TypeScript and contain finite mission pixels.
- Repeated R Dra baseline acceptance after endpoint and actual-lambda fixes still fails: `assert '2026-06-12' >= '2026-09-01'`. The local source D6 coverage ends in June, while another detector reaches September. The expected assertion remains unchanged. After two unsuccessful attempts, step 5 remains partial and work proceeds to step 6 under the requested rule.
- Full latest suite: `1 failed, 143 passed, 8 deselected in 2.43s`; sole failure `tests/test_precomputed_targets.py::test_r_dra_samples_full_baseline`. Network suite most recently: `8 passed, 133 deselected in 44.95s`. Golden 3I acceptance still pending.
- Apex and www Pages custom domains are Active with SSL. Enabled the www-only Single Redirect with query preservation. Live HTTPS probe returned HTTP 301 and `location: https://breathingcomets.org/es?target=barnard`.

## Step 6 implementation and verification

- Added progressive SPXF decoding in a Comlink Worker, R32F/R16UI WebGL2 texture arrays, fixed stack stretch, warm and divergent LUTs, saturation-before-NaN handling, pan/zoom and TAN SVG annotation alignment.
- Added Epoch/Blink/Diff λ controls, time ruler, A/B dates, playback controls, real Gaia proper motion by frame, source field notes with adjacent caveats, English/Spanish Paraglide messages with scientific values supplied at runtime from source JSON, and explicitly labelled deblended reference spectra.
- Added shareable URL state, embed route and exact binary delivery headers. The arbitrary-pixel spectrum remains step 7, visibly separate from a target reference.
- First web check: 20 errors and 2 warnings (extensionless package imports, unsupported top-level uPlot font option, readonly URL input and two accessibility/style warnings). Corrected source imports/options and retained full checking. Second check: `svelte-check found 0 errors and 0 warnings`.
- First build failed `ENOENT: no such file or directory, open '@fontsource-variable/newsreader/latin.css'`. Corrected the import to the installed standard font entrypoints. Second build passed.
- Browser verification found double gzip decoding with Vite preview's Content-Encoding response. The reader now detects gzip magic bytes; both compressed and browser-decoded actual data pass regression tests. Reference parser remains unchanged.
- Initial E2E could not bind a local listener under restriction; approved execution then found the installed Playwright browser absent. Downloaded its matching browser into /tmp without adding dependencies. A stale preview process failed after a build replaced its asset manifest (`ENOENT ... app.C31Q-d5W.js`); restarting preview resolved that environment issue.
- First complete E2E run: 2 passed, 1 failed because test innerText was compared to default textContent. Comparing rendered text explicitly preserves the intended assertion. Latest run: `3 passed (3.9s)` (Barnard frames/Gaia motion, WISE deblended reference S/N, shared URL in a fresh context).
- Vitest latest: `28 passed (28)` in 253 ms, including 20 TAN round trips, URL state, Barnard proper motion, real Python packet parsing and both gzip transport cases. Manual browser observed the actual Barnard plate, Gaia cross, Blink A/B and real Diff λ. Screenshot /tmp/breathing-comets-story-diff.jpg.
- Post-push cfe29d7 checks: exact sole author/committer identity; prohibited commit-message matches 0; only refs/heads/main.

- Final SPXF transport type check initially found the TypeScript 6 ArrayBufferLike/BufferSource mismatch. Narrowed the stream element type to the actual ArrayBuffer-backed bytes; no casts or disabled checks.

- Repeated stale-preview failure confirmed that reusing the manual preview across builds was unsafe. E2E now owns a separate port 4183 with reuseExistingServer false. Fresh final run: `3 passed (4.0s)`. Final type check: 0 errors, 0 warnings.

- Production verification attempt 1 ran while Pages was still compiling Python and served the previous skeleton: 3 failed. After 21ca8f1 deployed, attempt 2: 1 passed, 2 failed on direct URLs. Live HTTP proved /explore rewrite to /200.html returned 308 Location /200, so client navigation worked but direct/shared links did not. Corrected rewrite targets to extensionless canonical /200; acceptance remains unchanged.

- Production after a2c5bb4: `3 passed (9.5s)` on https://breathingcomets.org. Manual browser confirmed all 24 Barnard frames and the Gaia overlay on the public domain. The earlier permanent redirect remained cached in the existing browser tab; a fresh URL/context confirmed the corrected route.
- Step 7 first cold-stack probe (local actual S3 data, D4, 24 frames, fov 0.05): `status=200 first_byte=8.435993 total=8.436298`, failing the four-second bound. No cache-hit substitution was used.

## Step 7 current evidence

- Implemented the full route surface, exact JSON error envelopes, version headers, shared 30 requests/minute/IP limit, canonical S3 redirects, full-resolution exposure metadata, parameter-keyed stack/Diff caches, NDJSON forced-ePSF spectra, and cached/background JPL identifications. Moving-object and Sesame resolution follow-up still in progress.
- Fast API contracts: `12 passed, 1 warning in 1.41s` (approved HTTPX/Starlette combination emits an upstream deprecation warning; no unapproved replacement dependency installed). A first restricted TestClient run stalled and was terminated; unrestricted verification passed.
- Three actual stellar spectra requested from the local API: 208/208/200 valid points, with 9/7/7 explicitly rejected exposures retained in the evidence files. Median comparisons use the reference Ks 2.00–2.31 µm and W2 4.10–5.00 µm windows and their reference Vega zero points. Replaying the captured API responses with scripts/validate-api-spectra.py passes all six ±5% checks.
- J100141.19+013730.4: Ks 1.0014414263870293; W2 1.0160269484141908.
- J100203.40+031558.5: Ks 1.0251600774764664; W2 1.0107559193440256.
- J100226.29+020658.4: Ks 1.0160327655232988; W2 0.9817009937637698.
- These are local API measurements, not yet proof of the deployed Fly API. Recorded first-byte stack failure remains open. Optimizing independent raw/FLAGS reads to run concurrently and distinguishing permanent geometric rejection from transient upstream failure in metadata caching; network regression suite running.

- Concurrent raw/FLAGS network regression suite: `8 passed, 156 deselected, 1 warning in 33.84s`. Subsequent fast API/core/reference: `47 passed, 8 deselected, 1 warning in 2.86s`.
- Second cold-stack probe, fresh API process and a different validation star, D4/24 frames/fov 0.05: `status=200 first_byte=4.397537 total=4.397810`. Still above four seconds. After two failures, this acceptance remains open and work continues.
- Local actual click integration plus Story regressions: `4 passed (17.2s)`. This proves the live Story click path; the requested Lab-context E2E is still to be completed with step 8.
- Live 3I resolution exposed a pinned astroquery parser incompatibility: with required CAL_FORMAT=JD, it searches only for a calendar-format header and raises `Query failed with error message: 2461359.200525472, , , 106.029347905, 19.303506284,`. The core now uses the supported raw response method and parses named CSV columns, retaining spacecraft observer and JD matching tolerance. Stored the real response as a regression fixture; live JD test passes.
- Sesame endpoint currently redirects to its IDIA mirror; enabled redirect following and verified actual XML coordinate tags against its response. Missing proper motion remains explicitly unknown.
- First background SB Identification lookup hit its 25-second ReadTimeout; endpoint returned pending in 0.009671 s without delaying images. A source failure is now distinct from a pending lookup. Second attempt remains under observation; no objects are invented or inferred from failure.

- Second SB Identification background attempt also reached ReadTimeout at the 25-second bound; retain source-unavailable behavior and continue after two failures. No empty successful catalog is cached.
- Fixed JD parser verified through local /resolve?q=3I: returns kind moving, actual spacecraft position, track designation and JPL source. No fallback calendar date format was introduced.
- Step 7 final fast suite before handoff: `1 failed, 157 passed, 9 deselected, 1 warning in 3.45s`, sole known R Dra acceptance. Frontend `29 passed`; svelte-check 0 errors/0 warnings. Added variance propagation for Diff λ (independent-reference linear coefficients and selected median statistics); targeted core/API/Horizons tests `38 passed, 5 deselected, 1 warning in 2.81s`.
- Final local integration repeat: `4 passed (21.5s)` including the actual live click; feature-label, dark-theme and locale refinements were subsequently checked and will be verified again in deployment.
- User assigned the landing to a separate agent and requested a prompt. Created docs/landing-agent-prompt.md with explicit ownership and no Git/deployment mutations. Configured independent Paraglide message paths for landing EN/ES after verifying that the existing plugin supports pathPattern arrays. Coordinator will not edit homepage/landing-owned paths while that work proceeds. Defined the future 3I landing-packet interface in that prompt; the scientific packet remains coordinator responsibility.

## Step 7 deployment

- Deployed 2f79833 to Fly image deployment-01M7DGJWPHVZMF02KQ5YX8AG7E; single existing machine healthy. Public custom-domain health HTTP 200 with 809,593 index rows. Calibration readiness was initially null before acquisition, reported honestly.
- Repeated all three stellar measurements against https://api.breathingcomets.org using scripts/validate-api-spectra.py. All six ratios pass: Ks/W2 1.001441426387029/1.0160269484141913; 1.0251600774764664/1.0107559193440254; 1.0160327655232988/0.9817009937637687. Valid points 208/208/200, rejected exposures 9/7/7. Response evidence now records the deployed API and elapsed times 17.804/26.596/13.320 seconds.
- Public response-cache-cold Barnard stack probe (default fov 0.25, max_frames 80) returned HTTP 200: first_byte=5.177167, total=6.562423. Performance acceptance remains failing; no further optimization loop before step 8.
- Pushed 7f28b96 and 2f79833 together. Post-push checks: sole exact sebasvelace identity; prohibited-message count 0; sole remote main branch at 2f79833.
- Step 8 investigation: inspected the installed Aladin 3.8.2 implementation and live DR1 HiPS properties. newImageSurvey successCallback runs only after the layer is added; calling setFrequency before that is ineffective. No public destroy method was found. Plan to isolate the lazily imported Aladin viewer in a same-origin iframe, whose document lifetime releases its render loop when Lab closes, rather than inventing a cleanup API. Keep its real logo/link visible.

## Step 8 in progress

- Added a same-origin, client-only Aladin document and explicit origin/source-checked messages. The existing library is dynamically imported only inside Lab's iframe; removing that document releases its render loop. No unsupported destroy method is called.
- Read live HiPS properties into hips.json; channel labels remain sourced from channels.json. The required frequency encoding uses the published spectral bounds and actual channel count. setFrequency runs after successCallback confirms that the layer is added.
- Added Lab controls, layer tree, pixel/flag/variance inspector, canonical full-FITS link, 2MASS opacity, and spectral cube channel selection. Gaia in the photographic plate remains propagated per frame; the HiPS reference catalog is explicitly labelled at its catalog epoch.
- Fixed a progressive-loading mismatch: the renderer clamped requested frame indices to uploaded textures but the Gaia annotation could still use a later, not-yet-uploaded epoch. Both annotation and displayed metadata now follow the actually available frame.
- Initial Lab type check: 2 errors (showCube prop not declared) and 4 warnings (helper named state conflicted with the Svelte rune). Renamed helper and declared the prop; verification in progress.
- Step 7 deployed integration completed: `4 passed (24.3s)` on breathingcomets.org, including an actual live click returning at least 50 points.

- Second Lab type check: `svelte-check found 1 error and 0 warnings in 1 file`: `ModeSwitch.svelte: Cannot find name showCube`. The first scripted edit changed the type but missed the multiline destructuring declaration. Applied the explicit destructuring fix. After two failed checks, step 8 remains partial and work proceeds to step 9; the next integration build must still verify this fix before publication.

## Step 9 implementation and source blocker

- Built the uncertainty-attached catalog, D versus H plot with explicitly assumed albedo curves, selectable retained photometry, all 50 out-of-sample ratios and a log diameter comparison using the five absolute references available in the retained validation pairs. The page visibly states 5/50; no missing diameters are fabricated.
- IRSA TAP attempt 1, targeted 50-object query: `httpx.HTTPStatusError: 502 Proxy Error`. Attempt 2, documented REQUEST=doQuery NEO catalog query, 50-second bound: `httpx.ReadTimeout: The read operation timed out`. After two failures the full absolute comparison remains partial; continue step 11 after integration checks.
- Full Svelte check now passes: `svelte-check found 0 errors and 0 warnings`, including the explicit step 8 prop correction and landing changes.

## Integration verification (2026-11-14, after steps 8–10 landed in the working tree)

- Web: `npm run check` 0 errors / 0 warnings (1742 files); `npm run build` passed; Vitest `39 passed (39)`.
- Python: `1 failed, 157 passed, 9 deselected`; sole failure is the known `test_r_dra_samples_full_baseline` (unchanged assertion).
- Full local E2E against the default build: `17 passed, 2 failed`. Both failures (`lab.spec.ts` pixel click, `spectrum.spec.ts`) were `canvas` never appearing. Console showed `blocked by CORS policy ... api.breathingcomets.org/v1/gaia` from `http://127.0.0.1:4191`: `services/api/fly.toml` sets `SPX_ALLOWED_ORIGINS` to prod + `localhost:5173` only, overriding the code default that includes `127.0.0.1:4183`. Not a product defect.
- Rebuilt with `VITE_API_BASE=http://127.0.0.1:8000` and reran: `3 passed (22.1s)` (Lab frame 85 + Aladin attribution, Lab pixel click ≥ 50 points, free-sky click ≥ 50 points).
- Decision pending: add `http://127.0.0.1:4183` to the `fly.toml` allowlist (would make the public-API E2E runnable locally) — not changed.

## Production verification after push 6337571

- Pushed 2f79833..6337571 (four commits: Lab/Aladin, Small-Body Lab, landing, STATUS). Remote has only `refs/heads/main`; prohibited-attribution matches 0.
- Pages deployed after about 8 polls of 20 s. HTTP 200 on `/`, `/es`, `/explore?target=barnard`, `/neo`, `/es/neo`, `/aladin` and a landing plate.
- Full E2E against https://breathingcomets.org: `19 passed (1.4m)` (lab 2, landing 11, neo 2, spectrum 1, story 3). This also shows the public API allows the production origin.

## Step 11 first slice: comet atlas (2026-11-14)

- Copied the retained CSVs into `data/derived/comets/` (`co2_census_physical`, `co_census_final`, `h2o_census`, `q_vs_aperture`, `3I_aug2025_bandfits`, `3I_aug2025_spectrum`) and `pipelines/export_comets.py` writes `apps/web/static/data/comets/index.json` (20 comets). Every number is copied from a CSV; the old `co2_census_final.csv` is not used.
- Status rule (BUILD 8.9): detected S/N ≥ 5 and χ²ᵣ < 50 (17); with systematics S/N ≥ 5 and χ²ᵣ ≥ 50 (2: C/2025 A6 Lemmon χ²ᵣ 71.6, 3I/ATLAS December χ²ᵣ 185); marginal 3 ≤ S/N < 5 (1: P/2021 N1); not detected 0. C/2014 UN271 (15 au) is flagged unreliable.
- 3I August CO₂ validation: the retained `3I_aug2025_bandfits.csv` is the earlier Gaussian fit without sky subtraction (3 px: 1.11e27, χ²ᵣ 278, strong aperture dependence) and does NOT support the guide's 1.17e27. Re-ran `research/11_band_physical.py` (read-only, system Python with pandas) on `3I_aug2025_D5_skysub.csv`: best no-evolution fit `χ²r=27.5 T=100 σx=0.005 n=0.0 Q(r=3.2au)=1.17e+27 ± 3.0e+25` (statistical). The 16–84% range 0.86–1.38e27 comes from the research notes and was not re-run; the page says so. Evidence stored in `data/derived/comets/3i_aug2025_physical.json`.
- 29P CO validation uses `co_census_final.csv` (Q(CO) 4.504e28; CO/CO₂ 43.8 [36.6, 51.9]) against 2.9–5.6e28 (Bockelée-Morvan et al. 2022). Per PENDIENTES P3 this is a research result, not an independent re-measurement.
- Withheld: 3I August H₂O (guide: 4.0e26 against 3.2e26). No CSV or reproducible script output for it was retained; the page shows it as pending with the reason. The "29P in outburst" legend of BUILD 10.6 was also not published: nothing retained verifies it.
- Verification: `npm run check` 0 errors / 0 warnings; Vitest 39 passed; `pytest -m "not network and not slow"` 164 passed, 1 failed (known R Dra); full E2E built against the local API `26 passed (44.0s)` (comets 7, landing 11, lab 2, neo 2, spectrum 1, story 3).

## 3I/ATLAS packet (2026-11-14)

- **API bug found and fixed:** tracked stacks sampled the Horizons ephemeris every hour, so any window beyond ~4 days sent more than ~100 JD values in the URI; astroquery warned "uri ... very long and might have been truncated" and Horizons calls failed as `EphemerisUnavailable` / HTTP 503 `UPSTREAM_UNAVAILABLE` (reproduced: 5 and 60 epochs ok; 150 and 409 failed in ≤ 1 s). `ephem.horizons_positions` now splits epochs into chunks of 40 and concatenates them, and `science.tracked_rows` samples every 6 h (the 3.5° D5 field is far wider than 6 h of comet motion). `tests/test_horizons_chunks.py`: 2 passed. **Not yet deployed to Fly**, so the public API still has the bug.
- With the fix, the local API returned real tracked D5 stacks of 3I (`track=2025 N1`, fov 0.05°, 31×31 px, 6.15″/px): August 2025 `200 46,500 B in 16.6 s` (14 frames) and December 2025 `200 35,510 B in 20.5 s` (10 frames). Stored in `apps/web/static/data/comets/3i-atlas/` with `provenance.json` and `_headers` entries for raw delivery.
- `pipelines/landing_3i.py` renders 12 August frames (≥ 95% valid pixels) plus a poster at 4.236 µm with the stack's own stretch and writes `landing.json` (agreed contract plus optional `pixel_arcsec`, `nx`, `north_up`, image sizes, Spanish labels and caveats). No gas map and no continuum subtraction exist, so none is shown; the hero caption says so.
- The packet is bundled at build time (validated; fallback to the deferred fetch and pending state if invalid) so the prerendered page starts with 3I and the `preload` targets the right frame. Initial JS rose from 70.4 to **80.8 KB gz** (budget 90).
- Headline figure is August Q(CO₂) 1.17e27 (χ²ᵣ 27.5); December 3.42e27 carries its "fits poorly, χ²ᵣ 185" caveat. The H₂O comparison stays withheld.
- Verification: `npm run check` 0/0; Vitest 42 passed (3 new packet tests: contract, stack/obs_id/stretch match, atlas equality); full local E2E against the local API `26 passed (44.4s)`; pytest `1 failed (known R Dra), 166 passed`.

## Detail pages, landing redesign and progress (2026-11-14)

- `/comets/3i-atlas` and `/comets/29p-schwassmann-wachmann` (EN/ES): real tracked frames ordered by wavelength with sweep animation, D5 and D6 spectra (census filters, Jy → mJy), diagnostics, comparisons with published values and provenance. 29P stack: 34 frames, 16–21 Dec 2025 (`track=90000393`). Tests: 6 pytest (`test_comet_pages.py`) and 5 E2E (`comet-detail.spec.ts`).
- Landing redesign: dark plate hero with word-by-word headline, scan line and pointer parallax; 102-channel ribbon from `channels.json` (bar height = resolving power R); alternating dark/paper bands; sticky masthead with section tracking and scroll progress; CSS scroll-driven reveals; sticky figures; card micro-interactions. All animation is disabled under `prefers-reduced-motion`.
- Verification: `npm run check` 0/0; Vitest 43 passed; full local E2E (built against the local API) 31 passed; initial JS 88.5 KB gz.
- All findings, deviations from BUILD 10.4 and their justifications: `docs/FINDINGS.md`.

### Historical completion estimate (superseded; use the current step table)

| Step | Weight | Done | Note |
|---|---|---|---|
| 1 Repository | 2 | 100% | |
| 2 Deployed skeletons | 3 | 100% | |
| 3 Static data | 3 | 100% | |
| 4 Core | 10 | 90% | golden 3I model test and R Dra baseline pending |
| 5 Five targets | 8 | 90% | R Dra baseline fails |
| 6 Story Explorer | 12 | 100% | |
| 7 Live API | 10 | 80% | cold stack 5.2 s; Horizons fix deployed 2026-11-14; JPL identification |
| 8 Lab + Aladin | 8 | 90% | |
| 9 Small-Body Lab | 8 | 80% | absolute references 5/50 |
| 10 Landing | 8 | 85% | redesign done; Lighthouse and gas-map animation pending |
| 11 Comets / method / about / ES | 8 | 55% | atlas and two pages done; `/method` and about missing |
| 12 Final tests and budgets | 6 | 40% | Lighthouse, a11y audit, E2E 5–7 partly |
| 13 Submission | 8 | 10% | video, summary, Use of AI not produced |
| 14 Freeze | 2 | 0% | |

Weighted total **75%** of the planned build (72.2 / 96); **83%** counting only the product steps 1–12.

## /method (2026-11-14)

- `/method` and `/es/method`: ten sections (data, observer, wavelength, Diff λ, photometry, comet gas, validation, nulls, limits, reproducibility) with data-driven tables and `build.json` (new). Tests: 3 pytest (`test_build_info.py`), 5 E2E (`method.spec.ts`), 1 Vitest (note table). Full local E2E 36 passed; Vitest 44 passed; check 0/0; pytest 175 passed + known R Dra.
- Landing initial JS **75.1 KB gz** after removing the dynamic message lookup (see FINDINGS section 8).
- Step 11 now lacks only the "about" page; step 11 estimate raised from 55% to about 80%, which moves the weighted total from 75% to about 77%.

## Fly deployment (2026-11-14)

- Deployed the Horizons chunking fix to `breathing-comets-api` (image `deployment-01M7DQ56PM0SKP62HE6VB2C19N`). Public health 200 (cold start 18.0 s). Tracked 3I (17 days) 200 in 6.8 s and 29P (11 days) 200 in 4.3 s, content identical to the stored stacks. Full production E2E `36 passed` twice. Details and the intermittent-test finding: `docs/FINDINGS.md` section 9.
- Still open: 29P through `/v1/resolve`, cold-stack latency target (4 s), JPL SB identification, Lighthouse, about page, submission.

## 29P resolver (2026-11-14)

- Resolver now handles numbered periodic comets (`DES=<des>; CAP`) and ambiguous SBDB answers (HTTP 300). Local API: `29P` → `DES=29P; CAP`, `240P-B` ok, `240P` explicit error. Tests: 5 new pytest; full fast suite `1 failed (known R Dra), 180 passed`. **Not deployed to Fly yet.** Details: `docs/FINDINGS.md` section 10.

## /about (2026-11-14)

- `/about` and `/es/about` published with credits, challenge and use of AI. Full local E2E `40 passed (58.4s)`, check 0/0, landing initial JS 73.6 KB gz. Step 11 is complete apart from texts only the user can write (prior-work declaration, team members). Open item: no `LICENSE` in the repo and Aladin Lite is GPL-3 (`docs/FINDINGS.md` section 11). Weighted progress is now about 80%.

## Closure work authorized 2026-11-14

- User confirmed the prior research-script execution was authorized and permitted justified flexibility. Video is being produced by the user; coordinator owns the remaining technical work and written submission. No video files will be changed.
- Added independent product implementation of the CO2 even-J P/R profile and parent Haser conversion, checking the retained August D5 data rather than asserting a stored Q. `tests/test_comet_model.py`: 2 passed, including `test_golden_3I_co2` in the unchanged published [0.94, 1.6]e27 range. This is verification, not a replacement census or regenerated uncertainty interval.
- API resolver/Horizons contracts: 19 passed. Deployed existing periodic-comet resolver fix plus explicit local test origin http://127.0.0.1:4183 to Fly image deployment-01M7EB5KQ7HN7ATFSM988W2HM8. Public verification is running.

- Public deployment confirmed: /v1/resolve?q=29P HTTP 200 (track DES=29P; CAP); health HTTP 200 with 809,593 rows and v5 maps; Access-Control-Allow-Origin matches http://127.0.0.1:4183. Post-push 0cb0cc3 checks passed: sole exact identity, 0 prohibited messages, sole remote main.
- Recovered the complete NEOWISE reference table through documented Gator after TAP timed out. 1,523 catalog rows, all 50 CV designations matched; the five previously retained medians agree exactly. Export now contains all 50 absolute diameter pairs, retains the original rounded CV ratios, and records source query and SHA-256. New reference integrity test passes.
- R Dra diagnostic: D4 index ends 2026-09-25 (starts June in the retained stack), D6 ends 2026-06-12 (starts April). Attempting a September D6 file at the corresponding D4 observation raises `ValueError: Source outside the reliable detector interior`. The D6 September acceptance remains unchanged and failing; no detector or date is relabelled.

- New resilience tests first failed on incorrect test locators (ModeSwitch uses radio semantics; two mobile Play controls) and a wrong expected 3I media path. Corrected selectors from the captured accessibility snapshot; iPhone playback/share check then passed. Tightened the offline Diff check to require an actually rendered Diff stack. Direct target URLs defaulted to D4 even for targets whose prepared Diff is D6; the parser now matches the existing target-picker defaults while respecting an explicit det parameter.

- Added GPL v3 project licence, retained both Aladin licence texts (the package has LGPL in LICENSE and GPL in COPYING/metadata) plus Geist OFL notices, an operational README and data-driven written submission. Video remains user-owned and untouched; the submission keeps only the user disclosure marker.
- JPL documentation now explicitly rejects MPC 500 for a geocentric observer. Switched directly to xobs=0,0,0,0,0,0; live comet-only query returned HTTP 200 in 8.11 s with the documented explicit no-matching-records warning but no result count. Parser now accepts only that explicit empty case; two schema/observer tests pass. Asteroid query still hit ReadTimeout at 32.86 s, so general availability is not claimed.
- FITS reader now extends a cached PRIMARY/IMAGE prefix rather than re-reading it for selected cutouts. A physical in-memory FITS test verifies all offsets and that only the third header is fetched during extension. Numerical values and row decoding are unchanged.

- Offline prepared-target and iPhone tests now pass, including actual Diff-stack rendering for every target: combined with Story regressions, `5 passed (13.7s)`. Frontend unit tests: `45 passed`; type check 0 errors/0 warnings.
- Full Python run initially gave 186 passed and two failures: known R Dra plus the comet-export provenance list, which changed when the new retained August CSV was added. Regenerated the manifest; targeted export/submission suite now passes 8 tests. No scientific values or assertions were changed.
- Network run 1 was interrupted after 309.30 s blocked in SSL: `5 passed, 186 deselected`; it is not reported as a full pass. A verbose run is locating the upstream stall.

- API after bf9e845 (Fly image deployment-01M7EC711QWV25MCJ5A08RPN3R): response/cutout-cold stack at fov 0.06 gave first_byte=1.330658, total=2.035162; default fov 0.25/max_frames 80 at the same field gave first_byte=2.847200, total=4.146271 with warm metadata. A distinct epsilon Indi field with cold metadata gave first_byte=8.115480, total=16.904957. The general cold-acquisition budget remains unmet; the warm-metadata result is not substituted for it.
- Full browser run passed all 49 tests in 53.0 s; Python fast suite 187 passed, known R Dra 1 failed, 9 network deselected.
- Standalone Lighthouse 13.6.0 installed in a temporary audit cache (no application dependency change). Production mobile landing: performance 94, accessibility/best-practices/SEO 100, LCP 1549.672 ms, TBT 201 ms, CLS 0. Explorer: same category scores, LCP 1060.3695 ms, TBT 230 ms, CLS 0.03994.
- Reducing render-blocking requests using the installed Kit inlineStyleThreshold option. First check rejected an obsolete kit namespace (`config_kit_namespace`); corrected to the documented direct plugin option. This trades some cross-page CSS caching for earlier first paint; browser and deployed measurements must verify it.

- Independent reference-table transfer stalled twice because the HTTPX read timeout bounded idle reads, not the entire streamed body. Added validated 512 KiB parallel ranges for large reference tables and a total transfer deadline, plus transport tests. A standalone unchanged D5 EPSF/full-table comparison now passes in 67.63 s; the complete network run has acquisition failures still under investigation.
- Updated About wording to distinguish real scientific plates from the decorative SVG background and to remove vendor names from product copy. Two browser text assertions initially failed because they expected the old blanket wording; updated them to assert the precise scientific-data statement.
- Added client-side motion matching at the displayed epoch before asking the spectrum API for its 2026-01-01 reference position. The actual clicked pixel stays in the inspector; matched-source tracking is explicitly stated with the streamed spectrum. Unknown motion remains unknown.

- Running Vitest concurrently with Svelte checking caused Paraglide to replace generated files while the checker enumerated them: 0 errors but 1,076 missing-generated-file warnings. Do not run web build/check/Vitest concurrently in this shared checkout; rerun sequentially. No generated-file exclusions or warning suppressions were added.

- Complete network run with bounded reference transport finished: `2 failed, 7 passed, 190 deselected, 1 warning in 451.24s`. Both independent EPSF/full-table comparisons exceeded the 30-second total transfer deadline on 512 KiB table pieces. A standalone unchanged D5 comparison passed in 67.63 s. This points to variable acquisition throughput, not permission to change EPSF assertions.

- Reference assertion audit: all 25 original assertions remain present and unchanged; the file additionally has five stricter legacy-QR2 layout assertions from earlier work. Direct list equality is therefore not the right preservation check; comparing original assertion multiplicities confirms none were removed or altered.
- Reference-table acquisition now uses smaller 64 KiB pieces and retains successful pieces keyed by the ETag obtained from a fresh real S3 header. Object changes invalidate those bytes. This addresses observed slow continuous transfers without increasing the deadline or changing an assertion; API user-path timeouts remain unchanged.

- Published 1f0a783 (motion-aware clicked spectra), a4526b6 (written submission and licences), and 8c78225 (inlined route styles); post-push checks passed: sole exact identity, zero prohibited commit messages, sole remote main. Public Pages now serves the new inline styles and all 50 NEOWISE pairs. Manual browser inspection verified the published catalog, filtered 2025 YH5 with its interval/tier/single-visit caveat, and recorded /tmp/breathing-comets-neo-verified.png.
- Latest full network attempt with retained small-range transport ended with exit 143 after partial pass/failure output; no final test summary was emitted. Do not count it as a full pass. Earlier complete acquisition failures and the standalone successful D5 comparison remain the recorded evidence.

- Latest minimal-extension reader deployed as Fly image deployment-01M7EDNA1A37H0PQEGEQKMM91C, then warm single-machine configuration as deployment-01M7EDX1KCR4H0YRRXX9RP1CP7. Exactly one existing machine remains; min_machines_running=1 removes suspend/start delay at the cost of continuous running usage.
- Distinct RW Aur D6/fov 0.25/max_frames 80 cold-field acquisition returned HTTP 200: first_byte=19.939791, total=22.316882. General cold acquisition remains an explicit release limitation despite faster warm-metadata construction.
- Post-inline deployed mobile Lighthouse: performance 98, accessibility/best-practices/SEO 100, LCP 1410.203 ms, TBT 137 ms, CLS 0. Raw-derived metrics and hashes are retained in docs/verification/performance.json.
- Full production browser run: 48 passed, 1 failed (NEO photometry selection). Snapshot showed the SSR catalog still unselected after an early click. Fixed the product by disabling scripted NEO controls until mount; added a script-disabled readability/disabled-control regression instead of increasing the assertion timeout. Verification in progress.

## Closure verification history

- Fast Python acceptance: 191 passed, sole unchanged R Dra failure, 9 network deselected. Frontend: 47 unit tests; type check 0 errors/0 warnings; production build passes. Ruff passes outside the deliberately untouched reference-test file.
- Full local browser coverage: 49 passed before the final NEO readiness correction. Deployed run: 48 passed, 1 early-click failure now fixed in product; a script-disabled catalog regression was added. Final deployed rerun is pending publication.
- API warm configuration is deployed; written submission and complete NEOWISE validation are published. Cold arbitrary-field acquisition remains variable and above the four-second budget in distinct-field probes.
- The user produces the video and writes the prior-work disclosure. Video files remain untouched. The Sunday 2026-11-15 21:00 COT freeze has not been executed early.

- Final complete network run: `9 passed, 192 deselected, 1 warning in 457.50s`. All real-data assertions were executed; successful independent table pieces were retained only with the freshly obtained source ETag. No assertion was skipped, removed or relaxed.
- NEO readiness correction: `3 passed (2.4s)` locally, including unchanged per-object diameter/interval/tier checks and script-disabled catalog readability. Type check 0/0 and build pass.
- Commits c0b908b and 2147f95 are pushed; mandatory checks: sole exact identity, 0 prohibited messages, sole remote main. Exactly one API machine is kept running; its continuing resource usage is an explicit availability tradeoff.

- Static NEO readiness guard is now confirmed in the deployed HTML; the full production suite is being rerun with 50 cases. Fly status confirms one started iad machine, 2 shared CPUs, 2 GiB RAM, encrypted 5 GiB cache and passing health check.

- Production rerun after the NEO fix: 49 passed, 1 landing keyboard failure; the captured Blink state stayed at A after Enter before hydration. Extended the existing hero readiness pattern to the Blink, Diff slider and band controls; the keyboard test now waits for the visible enabled state before focusing, with the original B-epoch assertion unchanged. This fixes the product readiness state rather than retrying the keypress.

- Applied the same mounted-control guard to the comet atlas and detail controls, which had previously needed interaction retries. The 3I detail SSR fallback now selects the intended August epoch instead of flashing December before mount. Removed the old repeated-keypress workaround from the detail test: it waits for the actual enabled state and sends one Home/End sequence with the same wavelength assertion.

- Readiness patch 56512f8: local landing/comet browser suite `25 passed (17.7s)`; build passes. Exact Git identity, zero prohibited message matches, sole remote main verified after push. Final production run waits for the new Pages build.
- Final local frontend verification after readiness patch: Vitest `47 passed (47)`; `npm run check` reports `0 errors and 0 warnings`; production build passes. Data and submission checks: `101 passed in 0.10s`. Independent AST comparison: 25 original assertions, 30 current, zero missing or altered.
- Latest landing build references 21 initial JavaScript modules, totalling 75,398 bytes with gzip level 9, below the 90,000-byte budget; lazy Lab imports remain separate.

## Final observed checkpoint

- Application commit: `56512f8`, confirmed published on https://breathingcomets.org before the run.
- Full deployed Chromium suite: **`50 passed (2.9m)`**. Includes real API clicks, Aladin frame 85, five prepared targets with the API blocked, mobile EN/ES, restored URLs, NEO intervals and scripted-control readiness. Retained output: `docs/verification/production-e2e.txt`.
- Python fast acceptance: **191 passed, 1 failed, 9 deselected**; the unchanged failure is `test_r_dra_samples_full_baseline` (latest available D6 frame `2026-06-12`, required `>= 2026-09-01`). Full real-network suite: **9 passed, 192 deselected**. Original 25 reference assertions remain unchanged; five additional checks are retained.
- Frontend unit tests: **47 passed**; `svelte-check`: **0 errors / 0 warnings**; production build passed. Static data/submission consistency: **101 passed**.
- Public API health: HTTP 200, `ok: true`, 809,593 exposure rows, DR1/QR3, spectral maps v5. The single existing Fly machine stays running; no replica was added.
- Mobile Lighthouse landing: performance 98; accessibility/best-practices/SEO 100; LCP 1.410 s. Initial referenced JavaScript: 75,398 gzip bytes. Full measurements and raw-report hashes: `docs/verification/performance.json`.
- The general four-second cold-field budget, R Dra D6 September coverage, intermittent JPL identification, continuum-subtracted gas maps and fully supported August H2O validation remain open. None is counted as passed.
- Written deliverable: `docs/SUBMISSION.md`; freeze instructions: `docs/RELEASE.md`. User owns the video and prior-work declaration. The future Sunday freeze is pending.
- Git publication of the application passed all three checks: exact required author/committer, zero prohibited commit-message matches, only remote `main`. This record and regenerated provenance are committed in the following documentation checkpoint.

## Experience revision: view integrity

- Manual production review reproduced stale locale rendering, lost Explorer parameters on language change and copying the preceding field during acquisition.
- Language changes now request the localized document and serialize the live observation state, rather than depending on a stale route URL. NEO uses the same full-navigation locale boundary.
- Sharing requires the completed acquisition key to match the requested field/detector. Each copy serializes the current observation; pending acquisitions cannot reuse an old link. Superseded name resolution is aborted.
- Regression browser checks: `4 passed (5.6s)`; type check 0 errors/0 warnings; build passed. No scientific expected values changed.
