"""Build real, visit-stratified SPXF target packages without regenerating research."""

import argparse
import asyncio
import importlib.metadata
import json
from datetime import UTC, datetime

import httpx
import numpy as np
from astropy.coordinates import SkyCoord
from obstore.exceptions import BaseError
from spxcore import calib, cutout, ephem, known, sky, spxf
from spxcore.config import CACHE_DIR, STATIC_DIR
from spxcore.index import get_index, sample_visits

DEFAULT_DETECTORS = {"barnard": 4, "eps-indi-b": 6, "wise-0855": 6, "rw-aur": 6, "r-dra": 6}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False))
    temporary.replace(path)


def stack_header(target, grid, metadata, frames, detector, kind="stack"):
    samples = np.concatenate([f["flux"].ravel() for f in frames])
    samples = samples[np.isfinite(samples)]
    if not len(samples):
        raise ValueError("Stack contains no finite sky data")
    low, high = np.percentile(samples, [0.5, 99.5])
    visits = []
    for visit in sorted({m["visit"] for m in metadata}):
        dates = [m["mjd"] for m in metadata if m["visit"] == visit]
        visits.append({"visit": visit, "mjd_min": min(dates), "mjd_max": max(dates), "n": len(dates)})
    ra, dec = target["pos_2026_01_01"]
    return {"spxf": 1, "kind": kind, "target": {"name": target["name"], "slug": target["slug"],
            "ra": ra, "dec": dec, "frame": "ICRS", "track": None}, "grid": grid,
            "units": "MJy/sr", "has_var": False, "det": detector,
            "stretch_hint": {"p_lo": 0.5, "p_hi": 99.5, "lo": float(low), "hi": float(high)},
            "data_version": {"releases": ["dr1", "qr3"], "l2": "l2b-v27",
                             "s3_index": "spherex_s3_keys_compact.npz", "spectral_wcs": calib.SWCS},
            "frames": [{**m, "k": i} for i, m in enumerate(metadata)], "visits": visits,
            "provenance": {"generator": "spxcore 0.1.0", "created": datetime.now(UTC).isoformat(),
                           **{name: importlib.metadata.version(name) for name in ("astropy", "reproject")}}}


async def precompute(target, detectors, max_frames, fov, concurrency, catalog_only=False):
    slug = target["slug"]
    destination = STATIC_DIR / "targets" / slug
    destination.mkdir(parents=True, exist_ok=True)
    summary = json.loads((STATIC_DIR / "targets" / f"{slug}.json").read_text())
    ra, dec = target["pos_2026_01_01"]
    resolved = await known.resolve(slug)
    manifest = {"slug": slug, "name": target["name"], "ra": ra, "dec": dec, "pm": resolved["pm"],
                "fov_deg": fov, "default_det": DEFAULT_DETECTORS[slug], "default_mode": "blink",
                "stacks": {}, "diff": {}, "sizes_bytes": {}, "unavailable_detectors": {},
                "gaia": "gaia.json", "gaia_schema": 2, "field_notes": summary["notes"], "caveat": summary["caveat"]}
    if summary.get("spectrum"):
        write_json(destination / "spectrum.json", summary["spectrum"])
        manifest["spectrum"] = "spectrum.json"
    gaia_path = destination / "gaia.json"
    stars = None
    old_manifest = destination / "manifest.json"
    if catalog_only:
        if not old_manifest.exists():
            raise ValueError("Catalog refresh requires an existing target manifest")
        manifest = json.loads(old_manifest.read_text())
        manifest["gaia_schema"] = 2
        manifest.pop("gaia_target_id", None)
    gaia_schema_current = old_manifest.exists() and json.loads(old_manifest.read_text()).get("gaia_schema") == 2
    if gaia_path.exists() and gaia_schema_current and not catalog_only:
        previous = json.loads(gaia_path.read_text())
        if isinstance(previous, list):
            stars = previous
    if stars is None:
        try:
            stars = await known.gaia(ra, dec, radius=min(fov, 0.5))
            write_json(gaia_path, stars)
        except (httpx.HTTPError, ValueError) as exc:
            write_json(gaia_path, {"error": {"code": "GAIA_UNAVAILABLE", "message": str(exc)}})
    stars_with_motion = [s for s in (stars or []) if s["pmra"] is not None and s["pmdec"] is not None]
    if stars_with_motion:
        # Select a catalog counterpart only after propagating its actual Gaia solution.
        positions = [ephem.propagate(s["ra"], s["dec"], s["pmra"], s["pmdec"], s["ref_epoch"], 61041, s["parallax"])
                     for s in stars_with_motion]
        distances = SkyCoord([p[0] for p in positions], [p[1] for p in positions], unit="deg").separation(SkyCoord(ra, dec, unit="deg")).arcsec
        nearest = int(np.argmin(distances))
        if distances[nearest] < 2:
            manifest["gaia_target_id"] = stars_with_motion[nearest]["source_id"]
    if catalog_only:
        write_json(destination / "manifest.json", manifest)
        print(f"{slug}: refreshed Gaia catalog ({len(stars or [])} sources)", flush=True)
        return
    for detector in detectors:
        print(f"{slug} D{detector}: querying exposures", flush=True)
        candidates = get_index().query(ra, dec, detector)
        describing = asyncio.Semaphore(concurrency)
        async def describe(exposure, gate=describing):
            async with gate:
                try:
                    return await cutout.describe_exposure(exposure, ra, dec)
                except (ValueError, KeyError, OSError, TimeoutError, BaseError, httpx.HTTPError):
                    return None
        described = await asyncio.gather(*[describe(e) for e in candidates])
        exposures = sample_visits([e for e in described if e is not None], max_frames)
        semaphore = asyncio.Semaphore(concurrency)
        failures = []

        async def frame(exposure, gate=semaphore, errors=failures, current_detector=detector):
            async with gate:
                try:
                    return await cutout.make_frame(exposure, ra, dec, fov)
                except (ValueError, KeyError, OSError, TimeoutError, BaseError, httpx.HTTPError) as exc:
                    errors.append({"obs_id": exposure["obs_id"], "det": current_detector,
                                     "error": type(exc).__name__, "message": str(exc)})
                    return None

        results = await asyncio.gather(*[frame(e) for e in exposures])
        valid = sorted([r for r in results if r is not None], key=lambda r: r[1]["mjd"])
        write_json(CACHE_DIR / "precompute" / f"{slug}-D{detector}-failures.json", failures)
        if not valid:
            manifest["unavailable_detectors"][str(detector)] = "No usable exposures; see pipeline failures"
            print(f"{slug} D{detector}: unavailable ({len(failures)} failures)", flush=True)
            continue
        grid = valid[0][0]
        metadata, frames = [v[1] for v in valid], [v[2] for v in valid]
        filename = f"D{detector}.spxf.gz"
        header = stack_header(target, grid, metadata, frames, detector)
        spxf.write_spxf(destination / filename, header, frames)
        size = (destination / filename).stat().st_size
        if size > 6_000_000:
            raise ValueError(f"{slug} D{detector} exceeds the 6 MB budget")
        manifest["stacks"][str(detector)] = filename
        manifest["sizes_bytes"][str(detector)] = size
        if detector == manifest["default_det"]:
            if len(frames) < 10:
                raise ValueError(f"{slug} has fewer than 10 usable default frames")
            diff_meta, diff_frames = sky.difference_stack(metadata, frames, grid)
            diff_header = stack_header(target, grid, diff_meta, diff_frames, detector, kind="diff") if any(m["diff_available"] for m in diff_meta) else {**header, "kind": "diff", "frames": [{**m, "k": i} for i, m in enumerate(diff_meta)]}
            diff_file = f"D{detector}.diff.spxf.gz"
            spxf.write_spxf(destination / diff_file, diff_header, diff_frames)
            manifest["diff"][str(detector)] = diff_file
        print(f"{slug} D{detector}: {len(frames)} frames, {len(header['visits'])} visits, {size} bytes, {len(failures)} rejected", flush=True)
        write_json(destination / "manifest.json", manifest)
    total = sum(p.stat().st_size for p in destination.iterdir() if p.is_file())
    if total > 25_000_000:
        raise ValueError(f"{slug} exceeds the 25 MB target budget")
    write_json(destination / "manifest.json", manifest)
    print(f"{slug}: {total} bytes; available detectors {list(manifest['stacks'])}", flush=True)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=[t["slug"] for t in known.targets()])
    parser.add_argument("--detectors", default="1,2,3,4,5,6")
    parser.add_argument("--max-frames", type=int, default=24)
    parser.add_argument("--fov", type=float, default=0.25)
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--refresh-gaia-only", action="store_true")
    args = parser.parse_args()
    targets = [t for t in known.targets() if args.target is None or t["slug"] == args.target]
    detectors = [int(d) for d in args.detectors.split(",")]
    for target in targets:
        await precompute(target, detectors, args.max_frames, args.fov, args.concurrency, args.refresh_gaia_only)


if __name__ == "__main__":
    asyncio.run(main())
