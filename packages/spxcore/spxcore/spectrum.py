"""Forced-ePSF spectral measurements with propagated positions and quality flags."""

import asyncio

import numpy as np
from obstore.exceptions import BaseError

from . import ephem, psf


async def measure(exposure, ra, dec, pm=None, neighbors=None):
    if pm:
        ra, dec = ephem.propagate(pm["ra0"], pm["dec0"], pm["pmra_masyr"], pm["pmdec_masyr"],
                                 pm["ref_epoch_jyear"], exposure["mjd"], pm.get("plx_mas"))
    cutout = await psf.async_cutout_psf(exposure["collection"], exposure["obs_id"], exposure["det"], float(ra), float(dec))
    if neighbors:
        cutout["neighbors"] = neighbors
    flux, error, fraction = psf.psf_photometry(cutout)
    yy, xx = np.indices(cutout["img"].shape)
    core = np.hypot(xx-cutout["x"], yy-cutout["y"]) <= 2
    saturated = bool(np.any((cutout["flg"][core] & (1 << 1)) != 0))
    if not np.isfinite(flux) or not np.isfinite(error):
        raise ValueError("Insufficient valid pixels for forced photometry")
    return {**exposure, "mjd": cutout["mjd"], "lam_um": cutout["lam_um"], "bw_um": cutout["bw_um"],
            "flux_mjy": flux, "err_mjy": error, "sat": saturated, "edge": False,
            "psf_fraction": fraction, "s3_key": cutout["s3_key"]}


async def stream_spectrum(exposures, ra, dec, pm=None, concurrency=64):
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded(exposure):
        async with semaphore:
            try:
                return await measure(exposure, ra, dec, pm)
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
