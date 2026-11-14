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
| 2 | Deployed skeletons | Partial | 7d7f4d9 | Static build passed; local and public Fly health HTTP 200 with ok true; single machine | Web type check blocked by unapproved @types/node; Pages and custom DNS require Cloudflare sign-in. |
| 3 | Static data | Done | Step 3 commit | 100 passed in 0.31s; du 364K; copied files byte-identical | No scientific results recalculated. |
| 4 | Scientific core | Pending | — | Not run | — |
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
