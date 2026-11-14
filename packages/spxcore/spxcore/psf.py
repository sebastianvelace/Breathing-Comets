"""Sampled ePSF models, spatial grid selection and weighted forced photometry."""

import asyncio

import numpy as np
from astropy.wcs import WCS
from scipy.ndimage import map_coordinates, shift

from . import calib, fitsio, s3
from .flags import HARD_ES21

HARD = HARD_ES21
OMEGA_PIX = s3.OMEGA_PIX
APPLY_APCOR = False
PSF_MODE = "sample"


def apcor(det):
    return 1.0


def epsf_row(nrows, x, y):
    if nrows == 441:
        nx, ny = 21, 21
    elif nrows == 451:
        nx, ny = 11, 41
    else:
        raise ValueError(f"Unknown EPSF grid: {nrows} rows")
    return int(min(max(y // (2040 / ny), 0), ny - 1)) * nx + int(min(max(x // (2040 / nx), 0), nx - 1))


async def read_epsf(key, hdu, x, y):
    h = hdu["header"]
    if h["NAXIS1"] != 8752:
        raise ValueError("Unexpected EPSF row byte length")
    zone = epsf_row(h["NAXIS2"], x, y)
    raw = await s3.get_range(key, hdu["dat_loc"] + zone * h["NAXIS1"], h["NAXIS1"])
    xc, yc, xw, yw = np.frombuffer(raw[8:24], ">f4")
    if abs(x - xc) > xw / 2 + 1 or abs(y - yc) > yw / 2 + 1:
        raise ValueError(f"EPSF row {zone} does not contain pixel ({x}, {y})")
    psf = np.frombuffer(raw[40:], ">f8").reshape(33, 33).astype(np.float32)
    return psf, int(h.get("OVSMPX", 5)), zone


async def async_cutout_psf(collection, obs_id, det, ra, dec, half=12, cache_dir=None,
                           ra_end=None, dec_end=None, ra_start=None, dec_start=None):
    key = s3.s3_key(obs_id, det)
    layout = await fitsio.read_hdu_layout(key)
    hdus = {h["name"]: h for h in layout}
    header = hdus["IMAGE"]["header"]
    wcs = WCS(header).celestial
    x, y = (float(v) for v in wcs.world_to_pixel_values(ra, dec))
    if not (20 <= x <= 2019 and 20 <= y <= 2019):
        raise ValueError("Source outside the reliable detector interior")
    if "EPSF" not in hdus:
        raise ValueError("Legacy optical PSF exposure excluded from sampled-ePSF photometry")
    xi, yi = round(x), round(y)
    x0, x1, y0, y1 = max(xi-half, 0), min(xi+half+1, 2040), max(yi-half, 0), min(yi+half+1, 2040)
    rows, epsf, maps = await asyncio.gather(
        fitsio.read_rows(key, layout, y0, y1, names=("IMAGE", "FLAGS", "VARIANCE")),
        read_epsf(key, hdus["EPSF"], x, y), calib.load_maps(int(str(det)[-1])),
    )
    lam, bw = calib.sample_maps(maps, x, y)
    psf, osamp, zone = epsf
    out = {"img": rows["IMAGE"][:, x0:x1].astype(np.float32),
               "flg": rows["FLAGS"][:, x0:x1].astype(np.int64),
               "var": rows["VARIANCE"][:, x0:x1].astype(np.float32),
               "psf": psf, "osamp": osamp, "zone": zone, "x": x-x0, "y": y-y0, "x_full": x, "y_full": y,
               "lam_um": float(lam), "bw_um": float(bw), "omega_sr": calib.omega_from_header(header),
               "mjd": float(header["MJD-AVG"]), "s3_key": key, "wcs": wcs, "x0": x0, "y0": y0}
    for tag, rr, dd in (("s", ra_start, dec_start), ("e", ra_end, dec_end)):
        if rr is not None:
            xx, yy = (float(v) for v in wcs.world_to_pixel_values(rr, dd))
            out[f"x{tag}"], out[f"y{tag}"] = xx-x0, yy-y0
    return out


def cutout_psf(*args, **kwargs):
    return asyncio.run(async_cutout_psf(*args, **kwargs))


def psf_model(c, nsteps=1, mode=None):
    mode = mode or PSF_MODE
    psf, osamp = c["psf"].astype(float), int(c["osamp"])
    total = psf.sum()
    if not np.isfinite(total) or total <= 0:
        raise ValueError("Invalid ePSF normalization")
    psf = psf / total
    center = (np.array(psf.shape)-1)/2
    ny, nx = c["img"].shape
    yy, xx = np.indices((ny, nx), dtype=float)
    if "xs" in c and "xe" in c and nsteps > 1:
        points = [(c["xs"]+(c["xe"]-c["xs"])*t, c["ys"]+(c["ye"]-c["ys"])*t)
                  for t in np.linspace(0, 1, nsteps)]
    else:
        points = [(c["x"], c["y"])]
    model = np.zeros((ny, nx))
    for px, py in points:
        if mode == "sample":
            u, v = center[1]+(xx-px)*osamp, center[0]+(yy-py)*osamp
            model += map_coordinates(psf, [v.ravel(), u.ravel()], order=3, mode="constant", cval=0).reshape(ny, nx)*osamp**2
        elif mode == "integrate":
            # Retained for the regression proving the sampled ePSF is sharper.
            big = np.zeros((ny*osamp, nx*osamp))
            sx, sy = (px+0.5)*osamp-0.5-center[1], (py+0.5)*osamp-0.5-center[0]
            ix, iy = int(np.floor(sx)), int(np.floor(sy))
            shifted = shift(psf, (sy-iy, sx-ix), order=1, mode="constant")
            y0, x0 = max(iy, 0), max(ix, 0)
            y1, x1 = min(iy+psf.shape[0], big.shape[0]), min(ix+psf.shape[1], big.shape[1])
            if y1 > y0 and x1 > x0:
                big[y0:y1, x0:x1] += shifted[y0-iy:y1-iy, x0-ix:x1-ix]
            model += big.reshape(ny, osamp, nx, osamp).sum(axis=(1, 3))
        else:
            raise ValueError("Unknown PSF sampling mode")
    return model/len(points)


def psf_photometry(c, R=4.0, nsteps=1):
    image, flags, variance = c["img"].astype(float), c["flg"], c["var"].astype(float)
    model = psf_model(c, nsteps)
    yy, xx = np.indices(image.shape)
    radius = np.hypot(xx-c["x"], yy-c["y"])
    if "xs" in c:
        vx, vy = c["xe"]-c["xs"], c["ye"]-c["ys"]
        t = np.clip(((xx-c["xs"])*vx+(yy-c["ys"])*vy)/max(vx*vx+vy*vy, 1e-9), 0, 1)
        radius = np.hypot(xx-(c["xs"]+t*vx), yy-(c["ys"]+t*vy))
    good = (radius <= R) & ((flags & HARD) == 0) & np.isfinite(image) & np.isfinite(variance) & (variance > 0)
    if good.sum() < 8:
        return np.nan, np.nan, 0.0
    models = [model]
    for neighbor in c.get("neighbors", []):
        models.append(psf_model({**c, "x": neighbor[0], "y": neighbor[1]}))
    design = np.column_stack([m[good] for m in models] + [np.ones(good.sum())])
    weights = 1/variance[good]
    covariance = np.linalg.inv(design.T @ (design*weights[:, None]))
    beta = covariance @ (design.T @ (weights*image[good]))
    omega = c.get("omega_sr", OMEGA_PIX)
    flux = float(beta[0]*omega*1e9)
    error = float(np.hypot(np.sqrt(covariance[0, 0])*omega*1e9, 0.03*flux))
    return flux, error, float(model[good].sum()/max(model.sum(), 1e-12))
