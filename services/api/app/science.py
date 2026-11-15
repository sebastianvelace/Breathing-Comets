"""Bounded mission-image operations and persistent, parameter-keyed caches."""

import asyncio
import hashlib
import json
import logging
import tempfile
from pathlib import Path

import httpx
import numpy as np
from astropy.time import Time
from obstore.exceptions import BaseError
from spxcore import calib, cutout, ephem, known, sky, spxf
from spxcore.config import CACHE_DIR, STATIC_DIR
from spxcore.index import get_index, sample_visits

LOG = logging.getLogger(__name__)
IO_LIMIT = asyncio.Semaphore(32)
STACK_LIMIT = asyncio.Semaphore(2)


class ScienceError(Exception):
    def __init__(self, code, source, message, status=503, retry=10):
        super().__init__(message)
        self.code, self.source, self.status, self.retry = code, source, status, retry


def cache_path(kind, parameters, suffix=".json"):
    token = hashlib.sha256(json.dumps(parameters, sort_keys=True, allow_nan=False).encode()).hexdigest()
    return CACHE_DIR / "api" / kind / (token + suffix)


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".tmp", mode="w", delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(value, handle, separators=(",", ":"), allow_nan=False)
    temporary.replace(path)


def separation_arcsec(ra, dec, stars):
    a, d = np.deg2rad(ra), np.deg2rad(dec)
    aa, dd = np.deg2rad([s["ra"] for s in stars]), np.deg2rad([s["dec"] for s in stars])
    h = np.sin((dd-d)/2)**2 + np.cos(dd)*np.cos(d)*np.sin((aa-a)/2)**2
    return np.rad2deg(2*np.arcsin(np.sqrt(np.clip(h, 0, 1))))*3600


def local_field(ra, dec, radius=.01):
    for target in known.targets():
        tr, td = target["pos_2026_01_01"]
        if separation_arcsec(ra, dec, [{"ra": tr, "dec": td}])[0] < radius*3600:
            return target
    return None


async def catalog(ra, dec, radius, gmax=19):
    path = cache_path("gaia", [ra, dec, radius, gmax, 3])
    if path.is_file():
        return json.loads(path.read_text())
    target = local_field(ra, dec, max(.01, .24-radius)) if radius < .24 else None
    if target:
        original = STATIC_DIR / "targets" / target["slug"] / "gaia.json"
        if original.is_file():
            stars = json.loads(original.read_text())
            if isinstance(stars, list):
                distance = separation_arcsec(ra, dec, stars)
                return [s for s, sep in zip(stars, distance) if sep <= radius*3600 and s["g"] < gmax]
    stars = await known.gaia(ra, dec, radius, gmax)
    atomic_json(path, stars)
    return stars


async def describe_rows(ra, dec, det, t0=None, t1=None):
    key = cache_path("exposures", [ra, dec, str(det), t0, t1, calib.SWCS])
    if key.is_file():
        return json.loads(key.read_text())
    rows = await asyncio.to_thread(get_index().query, ra, dec, det, t0, t1)
    failures = []
    upstream_failed = False

    async def describe(row):
        nonlocal upstream_failed
        async with IO_LIMIT:
            try:
                return await cutout.describe_exposure(row, ra, dec)
            except (ValueError, KeyError, TimeoutError, OSError, BaseError, httpx.HTTPError) as exc:
                if not isinstance(exc, ValueError):
                    upstream_failed = True
                failures.append({"obs_id": row["obs_id"], "det": row["det"], "message": str(exc)})
                return None

    values = await asyncio.gather(*(describe(r) for r in rows))
    unique = {(r["obs_id"], r["det"], r["collection"]): r for r in values if r is not None}
    result = sorted(unique.values(), key=lambda r: (r["mjd"], r["det"]))
    if failures:
        LOG.warning("Exposure metadata unavailable for %d/%d rows", len(failures), len(rows))
        atomic_json(key.with_suffix(".failures.json"), failures)
    # Do not persist incomplete coverage as a complete successful query.
    if not upstream_failed:
        atomic_json(key, result)
    if rows and not result:
        raise ScienceError("EXPOSURES_UNAVAILABLE", "spherex_s3", "No exposure metadata could be read")
    return result


async def tracked_rows(ra, dec, detector, t0, t1, track):
    if not track:
        return await describe_rows(ra, dec, detector, t0, t1)
    if t0 is None or t1 is None or t1-t0 > 45:
        raise ScienceError("TRACK_INTERVAL_REQUIRED", "horizons", "Moving targets require an interval of at most 45 days", 400, 0)
    # A 3.5 degree detector field is much wider than the comet's motion in six hours.
    samples = np.linspace(t0, t1, max(2, int(np.ceil((t1-t0)*4))+1))
    positions = await asyncio.to_thread(ephem.horizons_positions, track, samples)
    candidates = {}
    for r, d in positions:
        for row in get_index().query(float(r), float(d), detector, t0, t1):
            candidates[row["obs_id"], row["det"]] = row
    rows = list(candidates.values())
    if not rows:
        return []
    # Header timestamps replace index estimates before querying observer ephemerides.
    from spxcore import fitsio, s3

    async def timestamp(row):
        async with IO_LIMIT:
            layout = await fitsio.read_hdu_layout(s3.s3_key(row["obs_id"], row["det"]), max_hdus=2)
            header = next(h["header"] for h in layout if h["name"] == "IMAGE")
            return {**row, "mjd": float(header["MJD-AVG"])}
    rows = await asyncio.gather(*(timestamp(r) for r in rows))
    exact = await asyncio.to_thread(ephem.horizons_positions, track, [r["mjd"] for r in rows])
    return [{**r, "track_ra": float(p[0]), "track_dec": float(p[1])} for r, p in zip(rows, exact)]


async def build_stack(ra, dec, fov, detector, t0, t1, max_frames, include_var, track, difference=False):
    path = cache_path("diff" if difference else "stack", [ra, dec, fov, detector, t0, t1, max_frames, include_var, track, calib.SWCS, 2], ".spxf.gz")
    if path.is_file():
        return path
    async with STACK_LIMIT:
        if path.is_file():
            return path
        exposures = await tracked_rows(ra, dec, detector, t0, t1, track)
        if not exposures:
            raise ScienceError("NO_COVERAGE", "spherex_index", "No usable SPHEREx exposures cover this position and interval", 404, 0)
        selected = sample_visits(exposures, max_frames)
        failures = []

        async def make(row):
            async with IO_LIMIT:
                try:
                    return await cutout.make_frame(row, row.get("track_ra", ra), row.get("track_dec", dec), fov, include_var)
                except (ValueError, KeyError, TimeoutError, OSError, BaseError, httpx.HTTPError) as exc:
                    failures.append({"obs_id": row["obs_id"], "message": str(exc)})
                    return None
        results = await asyncio.gather(*(make(r) for r in selected))
        valid = sorted([r for r in results if r is not None], key=lambda r: r[1]["mjd"])
        if not valid:
            raise ScienceError("PIXELS_UNAVAILABLE", "spherex_s3", "No usable image pixels could be read")
        grid = valid[0][0]
        metadata, frames = [r[1] for r in valid], [r[2] for r in valid]
        if difference:
            metadata, frames = await asyncio.to_thread(sky.difference_stack, metadata, frames, grid)
            if not any(m["diff_available"] for m in metadata):
                raise ScienceError("REFERENCE_UNAVAILABLE", "diff_lambda", "Fewer than three reference frames at a compatible wavelength", 422, 0)
        target = {"ra": ra, "dec": dec, "name": track or "Selected position", "frame": "ICRS", "track": track}
        header = spxf.stack_header(target, grid, metadata, frames, detector, "diff" if difference else "stack", include_var)
        header["rejected_exposures"] = failures
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
        await asyncio.to_thread(spxf.write_spxf, temporary, header, frames)
        temporary.replace(path)
        return path


async def point_motion(ra, dec, stars):
    target = local_field(ra, dec, radius=2/3600)
    if target:
        return (await known.resolve(target["slug"]))["pm"]
    measured = [s for s in stars if s["pmra"] is not None and s["pmdec"] is not None]
    if not measured:
        return None
    # The click is an ICRS sky position at the reference epoch stated by the API.
    positions = [ephem.propagate(s["ra"], s["dec"], s["pmra"], s["pmdec"], s["ref_epoch"], Time("2026-01-01", scale="utc").mjd, s.get("parallax")) for s in measured]
    distances = separation_arcsec(ra, dec, [{"ra": float(p[0]), "dec": float(p[1])} for p in positions])
    nearest = int(np.argmin(distances))
    if distances[nearest] > 2:
        return None
    star = measured[nearest]
    return {"ra0": star["ra"], "dec0": star["dec"], "pmra_masyr": star["pmra"], "pmdec_masyr": star["pmdec"], "plx_mas": star.get("parallax"), "ref_epoch_jyear": star["ref_epoch"]}
