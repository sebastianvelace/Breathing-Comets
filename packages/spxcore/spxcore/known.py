"""Coordinate parsing, audited target aliases and bounded catalog queries."""

import csv
import io
import json
import re
import xml.etree.ElementTree as ET
from functools import lru_cache

import httpx
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

from . import ephem
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


def _nullable_number(value):
    if value is None or value == "":
        return None
    number = float(value)
    return number if np.isfinite(number) else None


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
    if re.match(r"^\d+[PI]\b|^[CPDAXI]/\d{4}\s?[A-Z]", query, re.IGNORECASE):
        return await resolve_moving(query)
    escaped = query.replace("'", "''")
    adql = ("SELECT b.main_id,b.ra,b.dec,b.pmra,b.pmdec,b.plx_value FROM basic b "
            f"JOIN ident i ON i.oidref=b.oid WHERE i.id='{escaped}'")
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get("https://simbad.harvard.edu/simbad/sim-tap/sync", params={
                "REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": adql})
            response.raise_for_status()
    except httpx.HTTPError:
        return await resolve_sesame(query)
    rows = list(csv.DictReader(io.StringIO(response.text)))
    if not rows:
        try:
            return await resolve_sesame(query)
        except ValueError:
            return await resolve_moving(query)
    row = rows[0]
    ra, dec = float(row["ra"]), float(row["dec"])
    pmra, pmdec = _nullable_number(row.get("pmra")), _nullable_number(row.get("pmdec"))
    parallax = _nullable_number(row.get("plx_value"))
    if pmra is None or pmdec is None:
        return {"ra": ra, "dec": dec, "name": row["main_id"], "kind": "fixed", "source": "SIMBAD",
                "epoch_warning": "Proper motion unavailable; catalog position at epoch J2000"}
    now_ra, now_dec = propagate(ra, dec, pmra, pmdec, 2000.0, Time.now().mjd, parallax)
    return {"ra": float(now_ra), "dec": float(now_dec), "name": row["main_id"], "kind": "fixed", "source": "SIMBAD",
            "pm": {"ra0": ra, "dec0": dec, "pmra_masyr": pmra, "pmdec_masyr": pmdec,
                   "plx_mas": parallax, "ref_epoch_jyear": 2000.0}}


async def resolve_sesame(query):
    from urllib.parse import quote

    async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
        response = await client.get("https://cds.unistra.fr/cgi-bin/nph-sesame/-oxp/SNV?"+quote(query, safe=""))
        response.raise_for_status()
    root = ET.fromstring(response.text)
    resolver = next((r for r in root.iter("Resolver") if r.findtext("jradeg") and r.findtext("jdedeg")), None)
    if resolver is None:
        raise ValueError("Object not resolved")
    ra, dec = float(resolver.findtext("jradeg")), float(resolver.findtext("jdedeg"))
    return {"ra": ra, "dec": dec, "name": query, "kind": "fixed", "source": "Sesame",
            "epoch_warning": "Proper motion unavailable; Sesame ICRS catalog position at epoch J2000"}


async def resolve_moving(query):

    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.get("https://ssd-api.jpl.nasa.gov/sbdb.api", params={"sstr": query})
        if response.status_code == 300:
            # SBDB answers 300 when several records match (e.g. fragments 240P and 240P-B).
            response = await client.get("https://ssd-api.jpl.nasa.gov/sbdb.api",
                                        params={"des": pick_sbdb_match(response.json().get("list", []), query)})
        response.raise_for_status()
    data = response.json()
    obj = data.get("object")
    if not obj or "des" not in obj:
        raise ValueError("Moving object is unresolved or ambiguous")
    track, position = await first_working_track(track_candidates(obj), Time.now().mjd)
    return {"ra": float(position[0, 0]), "dec": float(position[0, 1]), "name": obj.get("fullname", obj["des"]),
            "kind": "moving", "source": "JPL SBDB / Horizons", "track": track, "observer": "SPHEREx"}


def pick_sbdb_match(matches, query):
    """Choose the single SBDB record whose primary designation equals the query; never guess."""
    exact = [m["pdes"] for m in matches if m.get("pdes", "").lower() == query.strip().lower()]
    if len(exact) != 1:
        names = ", ".join(m.get("name") or m.get("pdes", "?") for m in matches)
        raise ValueError(f"Moving object is ambiguous: {names}")
    return exact[0]


def track_candidates(obj):
    """Horizons identifiers to try, most specific last resort. A numbered periodic comet such as
    ``29P`` has several apparition records, so its bare designation is ambiguous and Horizons answers
    "no ephemeris"; ``DES=<des>; CAP`` selects the apparition closest to the requested time."""
    des = obj["des"]
    candidates = [des]
    if obj.get("prefix") == "P" or des.endswith("P") or "P/" in des:
        candidates.append(f"DES={des}; CAP")
    if obj.get("spkid"):
        candidates.append(str(obj["spkid"]))
    return list(dict.fromkeys(candidates))


async def first_working_track(candidates, mjd):
    """Return ``(identifier, position)`` for the first identifier Horizons resolves. Only an
    "unresolved" answer moves on to the next candidate; an unavailable service is raised as is."""
    import asyncio

    last = None
    for candidate in candidates:
        try:
            return candidate, await asyncio.to_thread(ephem.horizons_positions, candidate, [mjd])
        except ValueError as exc:
            last = exc
    raise ValueError("Moving object has no unique Horizons ephemeris (tried "
                     + ", ".join(candidates) + "); a fragment designation such as 240P-B may be required") from last


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
                      "pmra": _nullable_number(row.get("pmra")), "pmdec": _nullable_number(row.get("pmdec")),
                      "parallax": _nullable_number(row.get("parallax")), "g": float(row["phot_g_mean_mag"]), "ref_epoch": 2016.0})
    return stars
