# Breathing Comets

A public SPHEREx sky explorer for NASA Space Apps 2026: play real infrared
exposures, blink epochs, compare the sky at matched wavelengths, and inspect a
measured spectrum. English and Spanish are available throughout the site.

- **Live application:** https://breathingcomets.org
- **Method and limitations:** https://breathingcomets.org/method
- **Comet atlas:** https://breathingcomets.org/comets
- **Small-Body Lab:** https://breathingcomets.org/neo

## Run locally

Use Node 24 and Python 3.13. Dependencies are pinned in the lockfiles.

```sh
uv sync --frozen
cd apps/web
npm ci
npm run dev
```

The web app uses the public API by default. To run the backend from the repository
root, with the retained exposure/key indices in `data/`:

```sh
PYTHONPATH=packages/spxcore uv run granian --interface asgi --host 127.0.0.1 --port 8000 services.api.app.main:app
```

Set `VITE_API_BASE=http://127.0.0.1:8000` when building or starting the frontend
to use that backend. Local API data caches are stored in `data/cache`.

## Verification

```sh
uv run pytest
uv run pytest -m network
cd apps/web
npm run check
npx vitest run tests
npm run build
npx playwright test --trace off
```

Playwright requires its matching Chromium browser. To verify the deployed site,
set `PLAYWRIGHT_BASE_URL=https://breathingcomets.org`. Known failures and actual
verification results are recorded in [docs/STATUS.md](docs/STATUS.md); an existing
test failure is not a passing release check.

## Data and architecture

- `packages/spxcore`: canonical S3 access, physical FITS layout, spectral
  calibration, north-up cutouts, flags, visit sampling, photometry and ephemerides.
- `services/api`: bounded FastAPI requests, NDJSON spectra and persistent caches.
- `apps/web`: Svelte 5, a progressive SPXF worker, WebGL2 plates and lazy Aladin Lite.
- `pipelines`: reproducible packaging of retained measurements and real sky media.

Prepared target and comet packages work independently of the live API. Arbitrary
sky queries require available archive data and external services. Each product
keeps its uncertainty and observational caveats. The app does not issue alerts or
provide planetary-defense decisions.

Sky plates use SPHEREx data from NASA/JPL-Caltech/IRSA. Catalog overlays and
comparisons credit ESA/Gaia/DPAC, 2MASS, WISE/NEOWISE and JPL. Full attribution is on
[the About page](https://breathingcomets.org/about). This is an independent Space
Apps project, not a NASA product.

## Licence

Project code is licensed under **GNU GPL version 3**, provided in [LICENSE](LICENSE).
Third-party code, fonts and scientific data retain their own notices and terms;
see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
