"""Forced-ePSF spectral measurements with propagated positions and quality flags."""

import asyncio

import numpy as np
from astropy.wcs import WCS
from obstore.exceptions import BaseError

from . import ephem, fitsio, psf, s3


async def measure(exposure, ra, dec, pm=None, neighbors=None):
    layout = await fitsio.read_hdu_layout(s3.s3_key(exposure["obs_id"], exposure["det"]), max_hdus=2)
    header = next(h["header"] for h in layout if h["name"] == "IMAGE")
    mjd = float(header["MJD-AVG"])
    if pm:
        ra, dec = ephem.propagate(pm["ra0"], pm["dec0"], pm["pmra_masyr"], pm["pmdec_masyr"],
                                 pm["ref_epoch_jyear"], mjd, pm.get("plx_mas"))
    elif "track_ra" in exposure:
        ra, dec = exposure["track_ra"], exposure["track_dec"]
    cutout = await psf.async_cutout_psf(exposure["collection"], exposure["obs_id"], exposure["det"], float(ra), float(dec))
    if neighbors:
        models = []
        for star in neighbors:
            sr, sd = star["ra"], star["dec"]
            if star["pmra"] is not None and star["pmdec"] is not None:
                sr, sd = ephem.propagate(sr, sd, star["pmra"], star["pmdec"], star["ref_epoch"], mjd, star.get("parallax"))
            x, y = WCS(header).celestial.world_to_pixel_values(sr, sd)
            x, y = float(x)-cutout["x0"], float(y)-cutout["y0"]
            distance = np.hypot(x-cutout["x"], y-cutout["y"])
            if 0.5 < distance < 5:
                models.append((x, y))
        cutout["neighbors"] = models
    flux, error, fraction = psf.psf_photometry(cutout)
    yy, xx = np.indices(cutout["img"].shape)
    core = np.hypot(xx-cutout["x"], yy-cutout["y"]) <= 2
    saturated = bool(np.any((cutout["flg"][core] & (1 << 1)) != 0))
    if not np.isfinite(flux) or not np.isfinite(error):
        raise ValueError("Insufficient valid pixels for forced photometry")
    return {**exposure, "collection": cutout["s3_key"].split("/", 1)[0], "mjd": cutout["mjd"], "lam_um": cutout["lam_um"], "bw_um": cutout["bw_um"],
            "flux_mjy": flux, "err_mjy": error, "sat": saturated, "edge": False,
            "psf_fraction": fraction, "s3_key": cutout["s3_key"]}


async def stream_spectrum(exposures, ra, dec, pm=None, concurrency=32, neighbors=None):
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded(exposure):
        async with semaphore:
            try:
                return await measure(exposure, ra, dec, pm, neighbors)
            except (ValueError, KeyError, RuntimeError, OSError, TimeoutError, BaseError, np.linalg.LinAlgError) as exc:
                return {"obs_id": exposure["obs_id"], "det": exposure["det"],
                        "error": {"code": "MEASUREMENT_UNAVAILABLE", "message": str(exc)}}

    tasks = [asyncio.create_task(bounded(e)) for e in exposures]
    try:
        for task in asyncio.as_completed(tasks):
            yield await task
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
