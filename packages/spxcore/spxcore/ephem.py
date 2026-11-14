"""Catalog space motion, time-matched Horizons positions and spherical interpolation."""

import csv
import io

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

from .index import unit_vectors


class EphemerisUnavailable(RuntimeError):
    pass


def propagate(ra, dec, pmra, pmdec, ref_epoch, mjd, parallax=None):
    args = {"ra": ra*u.deg, "dec": dec*u.deg, "pm_ra_cosdec": pmra*u.mas/u.yr,
            "pm_dec": pmdec*u.mas/u.yr, "obstime": Time(ref_epoch, format="jyear")}
    if parallax is not None and parallax > 0:
        args["distance"] = (1000/parallax)*u.pc
        args["radial_velocity"] = 0*u.km/u.s
    coord = SkyCoord(**args).apply_space_motion(new_obstime=Time(mjd, format="mjd", scale="utc"))
    return coord.ra.deg, coord.dec.deg


def match_horizons_rows(request_jd, response_jd, tolerance=1e-5):
    request, response = np.atleast_1d(request_jd), np.asarray(response_jd)
    if not len(response):
        raise ValueError("Horizons returned no epochs")
    indices = np.array([int(np.argmin(np.abs(response-jd))) for jd in request])
    if np.any(np.abs(response[indices]-request) > tolerance):
        raise ValueError("Horizons epoch mismatch")
    return indices


# Horizons receives the epoch list in the URI; beyond ~100 JD values it is truncated and the
# query fails. Requests are therefore split into bounded chunks and concatenated in order.
HORIZONS_CHUNK = 40


def horizons_positions(designation, mjd):
    jd = Time(np.atleast_1d(mjd), format="mjd", scale="utc").jd
    if len(jd) <= HORIZONS_CHUNK:
        return _horizons_chunk(designation, jd)
    parts = [_horizons_chunk(designation, jd[i:i + HORIZONS_CHUNK]) for i in range(0, len(jd), HORIZONS_CHUNK)]
    return np.concatenate(parts)


def _horizons_chunk(designation, jd):
    from astroquery.jplhorizons import Horizons
    from requests.exceptions import RequestException

    query = Horizons(id=designation, location="500@-163182", epochs=jd.tolist())
    query.TIMEOUT = 8
    # The pinned client parser recognizes only CAL_FORMAT=BOTH. Keep the required
    # JD format and parse the documented CSV response from its raw async method.
    try:
        response = query.ephemerides_async(quantities="1", extra_precision=True, optional_settings={"CAL_FORMAT": "JD"})
        response.raise_for_status()
    except RequestException as exc:
        raise EphemerisUnavailable("Horizons is unavailable; retry later") from exc
    return parse_horizons_positions(response.text, jd)


def parse_horizons_positions(text, request_jd):
    if "$$SOE" not in text or "$$EOE" not in text:
        raise ValueError("Horizons returned no ephemeris for this target and observer")
    heading = next((line for line in text.splitlines() if line.startswith("Date") and "JDUT" in line), None)
    if heading is None:
        raise ValueError("Horizons JD header is missing")
    names = [name.strip() for name in next(csv.reader([heading]))]
    ri = next(i for i, name in enumerate(names) if name.startswith("R.A."))
    di = next(i for i, name in enumerate(names) if name.startswith("DEC"))
    body = text.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    data = [row for row in csv.reader(io.StringIO(body)) if row and row[0].strip()]
    if not data:
        raise ValueError("Horizons returned no epochs")
    jd = np.array([float(row[0]) for row in data])
    position = np.array([[float(row[ri]), float(row[di])] for row in data])
    if not np.isfinite(position).all() or np.any(np.abs(position[:, 1]) > 90):
        raise ValueError("Horizons returned invalid coordinates")
    return position[match_horizons_rows(request_jd, jd)]


def interpolate_positions(sample_mjd, ra, dec, mjd):
    # Observer ephemerides are timestamped in UTC; interpolation uses a uniform TDB scale.
    times = Time(sample_mjd, format="mjd", scale="utc").tdb.mjd
    target = Time(mjd, format="mjd", scale="utc").tdb.mjd
    order = np.argsort(times)
    times, vectors = np.asarray(times)[order], unit_vectors(ra, dec)[order]
    if np.any(np.diff(times) <= 0) or np.any(target < times[0]) or np.any(target > times[-1]):
        raise ValueError("Ephemeris interpolation requires distinct bracketing epochs")
    xyz = np.stack([np.interp(target, times, vectors[:, i]) for i in range(3)], axis=-1)
    xyz /= np.linalg.norm(xyz, axis=-1, keepdims=True)
    return np.rad2deg(np.arctan2(xyz[..., 1], xyz[..., 0])) % 360, np.rad2deg(np.arcsin(xyz[..., 2]))
