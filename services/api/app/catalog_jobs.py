"""Slow geocentric identifications run in bounded background jobs, never inline."""

import asyncio
import json
import logging
import time

import httpx
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

from .science import ScienceError, atomic_json, cache_path

LOG = logging.getLogger(__name__)
JOBS = {}
FAILURES = {}
JPL_LIMIT = asyncio.Semaphore(1)


async def identify(ra, dec, fov, mjd):
    coord = SkyCoord(ra, dec, unit="deg")
    rac = coord.ra.to_string(unit=u.hourangle, sep="-", precision=3, pad=True)
    decc = coord.dec.to_string(unit=u.deg, sep="-", precision=2, pad=True, alwayssign=True).replace("--", "M").replace("+", "")
    if dec < 0:
        decc = "M" + coord.dec.to_string(unit=u.deg, sep="-", precision=2, pad=True).lstrip("-")
    result = []
    async with JPL_LIMIT, httpx.AsyncClient(timeout=25) as client:
        for kind in ("a", "c"):
            parameters = {"sb-kind": kind, "mpc-code": "500", "obs-time": str(Time(mjd, format="mjd", scale="utc").jd),
                          "fov-ra-center": rac, "fov-dec-center": decc, "fov-ra-hwidth": fov/2,
                          "fov-dec-hwidth": fov/2, "two-pass": "true", "suppress-first-pass": "true", "req-elem": "false"}
            response = await client.get("https://ssd-api.jpl.nasa.gov/sb_ident.api", params=parameters)
            if response.status_code == 400:
                # Current API documentation excludes geocentric MPC 500.
                parameters.pop("mpc-code")
                parameters["xobs"] = "0,0,0,0,0,0"
                response = await client.get("https://ssd-api.jpl.nasa.gov/sb_ident.api", params=parameters)
            response.raise_for_status()
            data = response.json()
            if data.get("signature", {}).get("version") != "1.1":
                raise ValueError("Unrecognized SB Identification schema version")
            fields = data.get("fields_second", [])
            rows = data.get("data_second_pass", [])
            if "n_second_pass" not in data:
                raise ValueError("SB Identification omitted the result count")
            for values in rows:
                row = dict(zip(fields, values))
                position = SkyCoord(row["Astrometric RA (hh:mm:ss)"], row['Astrometric Dec (dd mm\'ss")'], unit=(u.hourangle, u.deg))
                magnitude = row.get("Visual magnitude (V)")
                vmag = float(magnitude) if magnitude not in (None, "", "n.a.") else None
                result.append({"name": row["Object name"], "ra": float(position.ra.deg), "dec": float(position.dec.deg),
                               "vmag": vmag if vmag is not None and np.isfinite(vmag) else None,
                               "kind": "comet" if kind == "c" else "asteroid", "observer": "geocentric", "source": "JPL SB Identification"})
    return result


async def fill(path, ra, dec, fov, epochs):
    try:
        result = {}
        for epoch in epochs:
            result[str(epoch)] = await identify(ra, dec, fov, epoch)
        atomic_json(path, result)
    except Exception:
        LOG.exception("JPL identification background job failed")
        FAILURES[str(path)] = time.monotonic()
    finally:
        JOBS.pop(str(path), None)


async def known_cached(ra, dec, fov, epochs):
    path = cache_path("known", [ra, dec, fov, epochs, "geocentric-v1.1"])
    if path.is_file() and time.time()-path.stat().st_mtime < 30*86400:
        return json.loads(path.read_text())
    if str(path) in FAILURES and time.monotonic()-FAILURES[str(path)] < 60:
        raise ScienceError("UPSTREAM_UNAVAILABLE", "jpl_sb_ident", "JPL identification is unavailable; images remain available", retry=60)
    if str(path) not in JOBS:
        if len(JOBS) >= 4:
            raise ScienceError("CATALOG_BUSY", "jpl_sb_ident", "Identification jobs are busy; retry later", retry=30)
        JOBS[str(path)] = asyncio.create_task(fill(path, ra, dec, fov, epochs))
    raise ScienceError("CATALOG_PENDING", "jpl_sb_ident", "Geocentric identifications are being cached; images remain available", retry=30)
