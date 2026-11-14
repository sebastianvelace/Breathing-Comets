# Build status

All results below describe observed verification. No research scripts have been executed.

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
| 2 | Deployed skeletons | Partial | 7d7f4d9 | Static build passed; local and public Fly health HTTP 200 with ok true; single machine | Node types approved and installed; type check passes with 0 errors and 0 warnings. Pages and custom DNS setup in progress. |
| 3 | Static data | Done | 3d98b0a | 100 passed in 0.31s; du 364K; copied files byte-identical | No scientific results recalculated. |
| 4 | Scientific core | Partial | Scientific core implementation commit | Fast suite 131 passed; second network run 5 passed and 2 failed; Ruff passed | D5 calibration acquisition still times out. Legacy QR2 layout acceptance and golden 3I check remain to be completed. |
| 5 | Five target precomputation | Pending | — | Not run | — |
| 6 | Story Explorer | Pending | — | Not run | — |
| 7 | Live API | Pending | — | Not run | — |
| 8 | Lab and Aladin | Pending | — | Not run | — |
| 9 | Small-Body Lab | Pending | — | Not run | — |
| 10 | Landing | Pending | — | Not run | — |
| 11 | Comets, method, about and Spanish | Pending | — | Not run | — |
| 12 | Final tests | Pending | — | Not run | — |
| 13 | Submission | Pending | — | Not run | — |
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

## Latest repository verification

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
