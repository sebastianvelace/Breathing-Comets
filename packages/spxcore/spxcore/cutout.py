"""North-up TAN reprojection, full-resolution wavelengths and frame metadata."""

import asyncio

import numpy as np
from astropy.time import Time
from astropy.wcs import WCS
from scipy.ndimage import map_coordinates

from . import calib, fitsio, s3
from .flags import remap_flags


def output_grid(ra, dec, fov=0.25):
    if not 0.05 <= fov <= 0.5:
        raise ValueError("Field of view must be between 0.05 and 0.5 degrees")
    n = 2*round(fov/(2*(6.15/3600)))+1
    wcs = WCS(naxis=2)
    wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    wcs.wcs.crval = [ra, dec]
    wcs.wcs.crpix = [(n+1)/2, (n+1)/2]
    wcs.wcs.cdelt = [-6.15/3600, 6.15/3600]
    return wcs, {"ctype": list(wcs.wcs.ctype), "crval": [ra, dec], "crpix": wcs.wcs.crpix.tolist(),
                 "cdelt_deg": wcs.wcs.cdelt.tolist(), "nx": n, "ny": n, "north_up": True, "pixel_arcsec": 6.15}


def reproject_array(array, input_wcs, output_wcs, shape, order=1, origin=(0, 0)):
    yy, xx = np.indices(shape)
    ra, dec = output_wcs.pixel_to_world_values(xx, yy)
    xs, ys = input_wcs.world_to_pixel_values(ra, dec)
    result = map_coordinates(array.astype(float), [ys-origin[1], xs-origin[0]], order=order,
                             mode="constant", cval=np.nan, prefilter=False)
    return result


async def make_frame(exposure, ra, dec, fov=0.25, include_var=False):
    key = s3.s3_key(exposure["obs_id"], exposure["det"])
    layout = await fitsio.read_hdu_layout(key)
    header = next(h["header"] for h in layout if h["name"] == "IMAGE")
    win = WCS(header).celestial
    cx, cy = (float(v) for v in win.world_to_pixel_values(ra, dec))
    if not (20 <= cx <= 2019 and 20 <= cy <= 2019):
        raise ValueError("Cutout center outside the reliable detector interior")
    wout, grid = output_grid(ra, dec, fov)
    yy, xx = np.indices((grid["ny"], grid["nx"]))
    wr, wd = wout.pixel_to_world_values(xx, yy)
    xs, ys = win.world_to_pixel_values(wr, wd)
    y0, y1 = max(0, int(np.floor(np.nanmin(ys)))-3), min(2040, int(np.ceil(np.nanmax(ys)))+4)
    names = ("IMAGE", "FLAGS", "VARIANCE") if include_var else ("IMAGE", "FLAGS")
    rows, maps = await asyncio.gather(fitsio.read_rows(key, layout, y0, y1, names), calib.load_maps(exposure["det"]))
    coords = [ys-y0, xs]
    flux = map_coordinates(rows["IMAGE"].astype(float), coords, order=1, cval=np.nan, mode="constant", prefilter=False)
    raw_flags = map_coordinates(rows["FLAGS"].astype(float), coords, order=0, cval=0, mode="constant", prefilter=False).astype(np.int64)
    nodata = (xs < 20) | (xs > 2019) | (ys < 20) | (ys > 2019) | ~np.isfinite(flux)
    flux[nodata] = np.nan
    lam, bandwidth = calib.sample_maps(maps, xs, ys)
    lam[nodata] = np.nan
    poly, max_error = calib.fit_lambda_polynomial(lam, grid["crpix"])
    mid = grid["ny"]//2
    meta = {**exposure, "mjd": float(header["MJD-AVG"]),
            "date": Time(header["MJD-AVG"], format="mjd", scale="utc").isot+"Z",
            "lam_um": float(lam[mid, mid]), "bw_um": float(bandwidth[mid, mid]),
            "lam_poly": poly, "lam_poly_max_error_um": max_error,
            "psf_fwhm_arcsec": float(header["PSF_FWHM"]), "src_pix": [cx, cy],
            "edge": bool(nodata.any()), "s3_key": key,
            "flag_counts": {name: int(np.count_nonzero(raw_flags & (1 << bit)))
                            for name, bit in (("OUTLIER", 19), ("TRANSIENT", 0), ("OVERFLOW", 1))}}
    frame = {"flux": flux.astype(np.float32), "flags": remap_flags(raw_flags, nodata)}
    if include_var:
        variance = map_coordinates(rows["VARIANCE"].astype(float), coords, order=1, cval=np.nan, mode="constant", prefilter=False)
        variance[nodata] = np.nan
        frame["var"] = variance.astype(np.float32)
    return grid, meta, frame
