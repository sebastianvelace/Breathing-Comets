"""Public API for SPHEREx sky exploration."""

import asyncio
import json
import logging
import os
import tempfile
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import httpx
from fastapi import FastAPI, Query
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    RedirectResponse,
    StreamingResponse,
)
from spxcore import calib, ephem, known, s3, spectrum
from spxcore.index import get_index, sample_visits
from starlette.exceptions import HTTPException
from starlette.requests import Request

from . import science

LOG = logging.getLogger(__name__)
DATA_VERSION = "dr1+qr3;l2b-v27;cal-swcs-v5-2026-191"
RATE_LIMITS = defaultdict(deque)
Ra = Annotated[float, Query(ge=0, lt=360, allow_inf_nan=False)]
Dec = Annotated[float, Query(ge=-90, le=90, allow_inf_nan=False)]
Mjd = Annotated[float | None, Query(ge=40000, le=100000, allow_inf_nan=False)]


@asynccontextmanager
async def lifespan(app):
    await asyncio.to_thread(get_index)
    yield


app = FastAPI(title="Breathing Comets API", version="0.1.0", lifespan=lifespan)


def error_response(code, source, message, status=503, retry=10):
    return JSONResponse(status_code=status, content={"error": {
        "code": code, "source": source, "message": message, "retry_after_s": retry}},
        headers={"X-SPX-Data-Version": DATA_VERSION, **({"Retry-After": str(retry)} if retry else {})})


@app.middleware("http")
async def boundary(request: Request, call_next):
    if request.method == "GET" and request.url.path in ("/v1/stack", "/v1/spectrum"):
        # Fly Proxy supplies this header in production; local requests use the peer IP.
        ip = request.headers.get("Fly-Client-IP") if os.getenv("FLY_APP_NAME") else None
        ip = ip or (request.client.host if request.client else "unknown")
        now = time.monotonic()
        if len(RATE_LIMITS) > 10000:
            for key in list(RATE_LIMITS):
                if not RATE_LIMITS[key] or RATE_LIMITS[key][-1] < now-60:
                    del RATE_LIMITS[key]
        history = RATE_LIMITS[ip]
        while history and history[0] <= now-60:
            history.popleft()
        if len(history) >= 30:
            return error_response("RATE_LIMITED", "api", "Request limit reached; retry after the indicated delay", 429, max(1, int(61-(now-history[0]))))
        history.append(now)
    try:
        response = await call_next(request)
    except Exception:
        LOG.exception("Unhandled API failure on %s", request.url.path)
        response = error_response("INTERNAL_ERROR", "api", "The request could not be completed", 500, 10)
    response.headers["X-SPX-Data-Version"] = DATA_VERSION
    return response


app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware,
    allow_origins=os.getenv("SPX_ALLOWED_ORIGINS", "https://breathingcomets.org,https://www.breathingcomets.org,http://localhost:5173,http://127.0.0.1:4173,http://127.0.0.1:4183").split(","),
    allow_origin_regex=r"https://(?:[a-zA-Z0-9-]+\.)+pages\.dev",
    allow_methods=["GET"], allow_headers=["Content-Type"], expose_headers=["X-SPX-Data-Version", "Retry-After"])


@app.exception_handler(science.ScienceError)
async def science_error(request, exc):
    return error_response(exc.code, exc.source, str(exc), exc.status, exc.retry)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return error_response("INVALID_PARAMETERS", "api", "; ".join(str(e["loc"][-1])+": "+e["msg"] for e in exc.errors()), 422, 0)


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return error_response("HTTP_ERROR", "api", str(exc.detail), exc.status_code, 0)


@app.exception_handler(httpx.HTTPError)
async def upstream_error(request, exc):
    return error_response("UPSTREAM_TIMEOUT" if isinstance(exc, httpx.TimeoutException) else "UPSTREAM_UNAVAILABLE", "catalog", "The external data source did not respond successfully", 503, 10)


@app.exception_handler(ephem.EphemerisUnavailable)
async def ephemeris_error(request, exc):
    return error_response("UPSTREAM_UNAVAILABLE", "horizons", str(exc), 503, 10)


@app.get("/v1/health")
async def health():
    ready = [d for d in range(1, 7) if (science.CACHE_DIR / "calibration" / f"{calib.SWCS}-D{d}.fits").is_file()]
    return {"ok": True, "index_rows": get_index().table.num_rows, "index_built": True,
            "collections": ["dr1", "qr3"], "swcs": calib.SWCS if len(ready) == 6 else None}


@app.get("/v1/resolve")
async def resolve(q: str = Query(min_length=1, max_length=200)):
    path = science.cache_path("resolve", q)
    if path.is_file() and time.time()-path.stat().st_mtime < 30*86400:
        return JSONResponse(json.loads(path.read_text()), headers={"Cache-Control": "public, max-age=2592000"})
    try:
        result = await known.resolve(q)
    except ValueError as exc:
        raise science.ScienceError("RESOLVE_FAILED", "resolver", str(exc), 400, 0) from exc
    science.atomic_json(path, result)
    return JSONResponse(result, headers={"Cache-Control": "public, max-age=2592000"})


@app.get("/v1/exposures")
async def exposures(ra: Ra, dec: Dec, fov: Annotated[float, Query(ge=.05, le=.5)] = .25,
                    det: str = Query(default="all", pattern="^(all|[1-6])$"), t0: Mjd = None, t1: Mjd = None):
    validate_interval(t0, t1)
    rows = await science.describe_rows(ra, dec, det, t0, t1)
    return JSONResponse(rows, headers={"Cache-Control": "public, max-age=3600"})


def validate_interval(t0, t1):
    if t0 is not None and t1 is not None and t0 > t1:
        raise science.ScienceError("INVALID_INTERVAL", "api", "t0 must not exceed t1", 422, 0)


async def image_response(ra, dec, fov, det, t0, t1, max_frames, var, track, difference):
    validate_interval(t0, t1)
    path = await science.build_stack(ra, dec, fov, det, t0, t1, max_frames, bool(var), track, difference)
    return FileResponse(path, media_type="application/octet-stream", headers={
        "Cache-Control": "public, max-age=31536000, immutable", "Content-Encoding": "gzip"})


@app.get("/v1/stack")
async def stack(ra: Ra, dec: Dec, fov: Annotated[float, Query(ge=.05, le=.5)] = .25,
                det: Annotated[int, Query(ge=1, le=6)] = 4, t0: Mjd = None, t1: Mjd = None,
                max_frames: Annotated[int, Query(ge=1, le=80)] = 80,
                var: Annotated[int, Query(ge=0, le=1)] = 0, track: str | None = Query(default=None, max_length=100)):
    return await image_response(ra, dec, fov, det, t0, t1, max_frames, var, track, False)


@app.get("/v1/diff")
async def diff(ra: Ra, dec: Dec, fov: Annotated[float, Query(ge=.05, le=.5)] = .25,
               det: Annotated[int, Query(ge=1, le=6)] = 4, t0: Mjd = None, t1: Mjd = None,
               max_frames: Annotated[int, Query(ge=1, le=80)] = 80,
               var: Annotated[int, Query(ge=0, le=1)] = 0, track: str | None = Query(default=None, max_length=100)):
    return await image_response(ra, dec, fov, det, t0, t1, max_frames, var, track, True)


@app.get("/v1/spectrum")
async def forced_spectrum(ra: Ra, dec: Dec, t0: Mjd = None, t1: Mjd = None,
                         track: str | None = Query(default=None, max_length=100)):
    validate_interval(t0, t1)
    path = science.cache_path("spectrum", [ra, dec, t0, t1, track, calib.SWCS, 2], ".ndjson")
    if path.is_file():
        return FileResponse(path, media_type="application/x-ndjson", headers={"Cache-Control": "public, max-age=86400", "Content-Encoding": "identity"})

    async def stream():
        records = []

        def encode(value):
            line = json.dumps(value, separators=(",", ":"), allow_nan=False)+"\n"
            records.append(line)
            return line
        yield encode({"type": "status", "stage": "querying_index", "position_epoch": "2026-01-01", "method": "sampled_ePSF_amplitude_plus_constant", "aperture_correction": False})
        try:
            rows = await science.tracked_rows(ra, dec, "all", t0, t1, track) if track else await asyncio.to_thread(get_index().query, ra, dec, "all", t0, t1)
            selected = [r for detector in range(1, 7) for r in sample_visits([r for r in rows if r["det"] == detector], 80)]
            if not selected:
                yield encode({"error": {"code": "NO_COVERAGE", "source": "spherex_index", "message": "No exposures cover this position", "retry_after_s": 0}})
                return
            neighbors = []
            if not track:
                try:
                    neighbors = await science.catalog(ra, dec, .012)
                except httpx.HTTPError:
                    yield encode({"type": "warning", "source": "gaia", "message": "Gaia unavailable; neighboring sources could not be fitted"})
            pm = None if track else await science.point_motion(ra, dec, neighbors)
            yield encode({"type": "status", "stage": "reading_pixels", "exposures": len(selected), "proper_motion_applied": pm is not None})
            count, rejected = 0, 0
            async for point in spectrum.stream_spectrum(selected, ra, dec, pm, neighbors=neighbors):
                if "error" in point:
                    rejected += 1
                else:
                    count += 1
                yield encode(point)
            yield encode({"type": "complete", "points": count, "rejected": rejected})
            if count and not rejected:
                path.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".tmp", mode="w", delete=False) as handle:
                    temporary = Path(handle.name)
                    handle.writelines(records)
                temporary.replace(path)
        except Exception as exc:
            LOG.exception("Spectrum failed")
            yield encode({"error": {"code": "SPECTRUM_UNAVAILABLE", "source": "spherex_s3", "message": str(exc), "retry_after_s": 10}})
    return StreamingResponse(stream(), media_type="application/x-ndjson", headers={"Cache-Control": "public, max-age=86400", "Content-Encoding": "identity", "X-Accel-Buffering": "no"})


@app.get("/v1/gaia")
async def gaia(ra: Ra, dec: Dec, radius: Annotated[float, Query(gt=0, le=.5)] = .25,
               gmax: Annotated[float, Query(ge=0, le=22)] = 19):
    return JSONResponse(await science.catalog(ra, dec, radius, gmax), headers={"Cache-Control": "public, max-age=2592000"})


@app.get("/v1/known")
async def known_objects(ra: Ra, dec: Dec, fov: Annotated[float, Query(ge=.05, le=.5)], mjd: str = Query(max_length=1000)):
    from .catalog_jobs import known_cached

    try:
        epochs = [float(v) for v in mjd.split(",")]
    except ValueError as exc:
        raise science.ScienceError("INVALID_EPOCHS", "api", "mjd must contain comma-separated epochs", 422, 0) from exc
    if not 1 <= len(epochs) <= 40 or any(not 40000 <= t <= 100000 for t in epochs):
        raise science.ScienceError("INVALID_EPOCHS", "api", "Provide between one and forty finite MJD epochs", 422, 0)
    return JSONResponse(await known_cached(ra, dec, fov, epochs), headers={"Cache-Control": "public, max-age=2592000"})


@app.get("/v1/fits")
async def fits(obs_id: str = Query(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_]+$"),
               det: Annotated[int, Query(ge=1, le=6)] = 4,
               collection: str = Query(default="dr1", pattern=r"^(?:spherex_)?(?:dr1|qr3|qr2)(?:_deep)?$")):
    try:
        key = s3.s3_key(obs_id, det)
    except KeyError as exc:
        raise science.ScienceError("EXPOSURE_NOT_FOUND", "spherex_index", "Exposure is not present in the public key index", 404, 0) from exc
    return RedirectResponse(s3.S3+key, status_code=302)
