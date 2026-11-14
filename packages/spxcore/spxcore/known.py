"""Coordinate parsing, audited target aliases and bounded catalog queries."""

import csv
import io
import json
import re
from functools import lru_cache

import httpx
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

from .config import STATIC_DIR
from .ephem import propagate


@lru_cache(maxsize=1)
def targets():
    return json.loads((STATIC_DIR / "targets.json").read_text())["targets"]


def parse_coordinates(query):
    q = query.strip().replace("−", "-")
    galactic = re.fullmatch(r"l\s*=\s*([-+\d.]+)\s*[, ]+b\s*=\s*([-+\d.]+)", q, re.IGNORECASE)
    if galactic:
        coord = SkyCoord(l=float(galactic[1])*u.deg, b=float(galactic[2])*u.deg, frame="galactic").icrs
        return float(coord.ra.deg), float(coord.dec.deg)
    parts = q.replace(",", " ").split()
    if len(parts) == 2:
        try:
            ra, dec = map(float, parts)
        except ValueError:
            pass
        else:
            if not (np.isfinite(ra) and np.isfinite(dec) and 0 <= ra < 360 and -90 <= dec <= 90):
                raise ValueError("Coordinates outside valid bounds")
            return ra, dec
    coord = SkyCoord(q, unit=(u.hourangle, u.deg), frame="icrs")
    return float(coord.ra.deg), float(coord.dec.deg)


def _normalize(text):
    return re.sub(r"[^a-z0-9]", "", text.lower().replace("ε", "epsilon"))


def _resolved_target(target, warning=False):
    ra, dec = target["pos_2026_01_01"]
    result = {"ra": ra, "dec": dec, "name": target["name"], "kind": "fixed", "source": "local",
              "slug": target["slug"], "pm": {"ra0": target["ra_j2000"], "dec0": target["dec_j2000"],
              "pmra_masyr": target["pmra_masyr"], "pmdec_masyr": target["pmdec_masyr"],
              "plx_mas": target["plx_mas"], "ref_epoch_jyear": 2000.0}}
    if warning:
        result["epoch_warning"] = "Proper motion applied: " + target["challenge_coords"]
    return result


async def resolve(query):
    if not query or len(query) > 200:
        raise ValueError("Query must contain between 1 and 200 characters")
    coordinates = None
    try:
        coordinates = parse_coordinates(query)
    except ValueError:
        pass
    for target in targets():
        if "challenge_coords" in target and coordinates is not None:
            original = target["challenge_coords"].split(" (")[0]
            ra, dec = parse_coordinates(original)
            separation = SkyCoord(*coordinates, unit="deg").separation(SkyCoord(ra, dec, unit="deg")).arcsec
            if separation < 2:
                return _resolved_target(target, warning=True)
        names = [target["slug"], target["name"], target["simbad"]]
        if _normalize(query) in {_normalize(n) for n in names}:
            return _resolved_target(target, warning=target["slug"] == "wise-0855")
    if coordinates is not None:
        return {"ra": coordinates[0], "dec": coordinates[1], "name": query, "kind": "fixed", "source": "coordinates"}
    escaped = query.replace("'", "''")
    adql = ("SELECT b.main_id,b.ra,b.dec,b.pmra,b.pmdec,b.plx_value FROM basic b "
            f"JOIN ident i ON i.oidref=b.oid WHERE i.id='{escaped}'")
    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.get("https://simbad.harvard.edu/simbad/sim-tap/sync", params={
            "REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": adql})
        response.raise_for_status()
    rows = list(csv.DictReader(io.StringIO(response.text)))
    if not rows:
        raise ValueError("Object not resolved")
    row = rows[0]
    ra, dec = float(row["ra"]), float(row["dec"])
    pmra, pmdec = float(row.get("pmra") or 0), float(row.get("pmdec") or 0)
    parallax = float(row.get("plx_value") or 0)
    now_ra, now_dec = propagate(ra, dec, pmra, pmdec, 2000.0, Time.now().mjd, parallax)
    return {"ra": float(now_ra), "dec": float(now_dec), "name": row["main_id"], "kind": "fixed", "source": "SIMBAD",
            "pm": {"ra0": ra, "dec0": dec, "pmra_masyr": pmra, "pmdec_masyr": pmdec,
                   "plx_mas": parallax, "ref_epoch_jyear": 2000.0}}


async def gaia(ra, dec, radius=0.25, gmax=19):
    if not (0 <= ra < 360 and -90 <= dec <= 90 and 0 < radius <= 0.5):
        raise ValueError("Invalid Gaia cone")
    adql = ("SELECT source_id,ra,dec,pmra,pmdec,parallax,phot_g_mean_mag FROM gaiadr3.gaia_source "
            f"WHERE 1=CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{ra},{dec},{radius})) "
            f"AND phot_g_mean_mag<{float(gmax)}")
    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.get("https://gea.esac.esa.int/tap-server/tap/sync", params={
            "REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": adql})
        response.raise_for_status()
    stars = []
    for row in csv.DictReader(io.StringIO(response.text)):
        stars.append({"source_id": row["source_id"], "ra": float(row["ra"]), "dec": float(row["dec"]),
                      "pmra": float(row.get("pmra") or 0), "pmdec": float(row.get("pmdec") or 0),
                      "parallax": float(row.get("parallax") or 0), "g": float(row["phot_g_mean_mag"]), "ref_epoch": 2016.0})
    return stars
