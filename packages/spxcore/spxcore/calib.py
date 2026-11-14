"""Full-resolution spectral calibration and measured pixel solid angle."""

import asyncio
from functools import lru_cache

import numpy as np
from astropy.io import fits
from scipy.ndimage import map_coordinates

from . import s3
from .config import CACHE_DIR

SWCS = "cal-swcs-v5-2026-191"
_pending = {}


async def load_maps(det):
    token = (id(asyncio.get_running_loop()), det)
    if token not in _pending:
        _pending[token] = asyncio.create_task(_load_maps(det))
    task = _pending[token]
    try:
        return await asyncio.shield(task)
    finally:
        if task.done():
            _pending.pop(token, None)


async def _load_maps(det):
    path = CACHE_DIR / "calibration" / f"{SWCS}-D{det}.fits"
    if not path.exists():
        key = f"qr3/spectral_wcs/{SWCS}/{det}/spectral_wcs_D{det}_spx_{SWCS}.fits"
        import obstore

        async with asyncio.timeout(30):
            metadata = await obstore.head_async(s3.STORE, key)
            size = metadata["size"]
            block = 4 * 1024 * 1024
            pieces = await asyncio.gather(*[
                s3.get_range(key, start, min(block, size-start)) for start in range(0, size, block)
            ])
            data = b"".join(pieces)
            if len(data) != size:
                raise ValueError("Truncated spectral calibration map")
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(".tmp")
        temp.write_bytes(data)
        temp.replace(path)
    return _read_maps(str(path))


@lru_cache(maxsize=6)
def _read_maps(path):
    with fits.open(path, memmap=False) as hdus:
        return tuple(np.asarray(hdus[name].data, dtype=np.float32) for name in ("CWAVE", "CBAND"))


def sample_maps(maps, x, y):
    coords = np.array([np.atleast_1d(y).ravel(), np.atleast_1d(x).ravel()])
    shape = np.shape(x)
    return tuple(map_coordinates(a, coords, order=1, mode="constant", cval=np.nan, prefilter=False).reshape(shape)
                 for a in maps)


def omega_from_header(header):
    omega = float(header["OMEGA_MEDIAN"])
    if not np.isfinite(omega) or omega <= 0:
        raise ValueError("Invalid OMEGA_MEDIAN")
    return omega * (np.pi / (180 * 3600)) ** 2


def fit_lambda_polynomial(lam, crpix):
    yy, xx = np.indices(lam.shape)
    dx, dy = xx - (crpix[0] - 1), yy - (crpix[1] - 1)
    design = np.stack([np.ones_like(dx), dx, dy, dx * dx, dx * dy, dy * dy], axis=-1)
    good = np.isfinite(lam)
    if good.sum() < 6:
        raise ValueError("Insufficient wavelength pixels for polynomial")
    coeff = np.linalg.lstsq(design[good], lam[good], rcond=None)[0]
    return coeff.tolist(), float(np.max(np.abs(design[good] @ coeff - lam[good])))
