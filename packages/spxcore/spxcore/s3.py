"""Compact canonical keys and unsigned, bounded S3 range requests."""

import asyncio
from functools import lru_cache

import numpy as np
import obstore
from obstore.store import S3Store

from .config import INDEX_DIR

S3 = "https://nasa-irsa-spherex.s3.us-east-1.amazonaws.com/"
STORE = S3Store("nasa-irsa-spherex", region="us-east-1", skip_signature=True)
OMEGA_PIX = (6.15 / 206264.806) ** 2  # Used only by legacy regression fixtures.


@lru_cache(maxsize=1)
def _load_keys():
    with np.load(INDEX_DIR / "spherex_s3_keys_compact.npz", allow_pickle=False) as z:
        return z["ids"], z["code"], [str(x) for x in z["dirs"]]


def s3_key(obs_id, det):
    ids, code, dirs = _load_keys()
    detector = int(str(det)[-1])
    if detector not in range(1, 7):
        raise ValueError("Detector must be between 1 and 6")
    q = f"{obs_id}D{detector}".encode()
    i = int(np.searchsorted(ids, q))
    if i == len(ids) or ids[i] != q:
        raise KeyError(f"No canonical S3 key for {obs_id} D{detector}")
    directory = dirs[code[i]]
    return f"{directory}/{detector}/level2_{obs_id}D{detector}_spx_{directory.rsplit('/', 1)[1]}.fits"


def s3_url(collection, obs_id, det):
    """Collection is accepted for compatibility; the index sets release priority."""
    return S3 + s3_key(obs_id, det)


async def get_range(key, start, length):
    for attempt in range(3):
        try:
            async with asyncio.timeout(8):
                return bytes(await obstore.get_range_async(STORE, key, start=int(start), length=int(length)))
        except (TimeoutError, OSError):
            if attempt == 2:
                raise
            await asyncio.sleep(0.2 * 2**attempt)


async def get_ranges(key, starts, ends):
    async with asyncio.timeout(8):
        buffers = await obstore.get_ranges_async(STORE, key, starts=starts, ends=ends)
    return [bytes(b) for b in buffers]
