"""Catalog space motion, time-matched Horizons positions and spherical interpolation."""

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

from .index import unit_vectors


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


def horizons_positions(designation, mjd):
    from astroquery.jplhorizons import Horizons

    jd = Time(np.atleast_1d(mjd), format="mjd", scale="utc").jd
    query = Horizons(id=designation, location="500@-163182", epochs=jd.tolist())
    query.TIMEOUT = 8
    table = query.ephemerides(quantities="1", extra_precision=True, optional_settings={"CAL_FORMAT": "JD"})
    rows = match_horizons_rows(jd, table["datetime_jd"])
    return np.column_stack([np.asarray(table["RA"])[rows], np.asarray(table["DEC"])[rows]])


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
