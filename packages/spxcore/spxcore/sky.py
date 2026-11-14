"""Same-wavelength reference images from independent visits."""

import warnings

import numpy as np

from .flags import NODATA


def wavelength_plane(meta, grid):
    yy, xx = np.indices((grid["ny"], grid["nx"]))
    dx, dy = xx-(grid["crpix"][0]-1), yy-(grid["crpix"][1]-1)
    c = meta["lam_poly"]
    return c[0]+c[1]*dx+c[2]*dy+c[3]*dx*dx+c[4]*dx*dy+c[5]*dy*dy


def difference_stack(metadata, frames, grid):
    result, info = [], []
    wavelengths = [wavelength_plane(m, grid) for m in metadata]
    for i, meta in enumerate(metadata):
        candidates = [j for j, other in enumerate(metadata) if other["visit"] != meta["visit"]
                      and abs(other["mjd"]-meta["mjd"]) > 2
                      and abs(other["lam_um"]-meta["lam_um"]) < 3*meta["bw_um"]]
        candidates = sorted(candidates, key=lambda j: abs(metadata[j]["lam_um"]-meta["lam_um"]))[:8]
        if len(candidates) < 3:
            result.append({"flux": np.full_like(frames[i]["flux"], np.nan),
                           "flags": np.full_like(frames[i]["flags"], NODATA)})
            info.append({**meta, "diff_available": False, "reference_count": len(candidates)})
            continue
        flux = np.stack([frames[j]["flux"] for j in candidates]).astype(float)
        delta = np.stack([wavelengths[j]-wavelengths[i] for j in candidates])
        valid = np.isfinite(flux) & np.isfinite(delta)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            for iteration in range(2):
                n = valid.sum(axis=0)
                sx = np.where(valid, delta, 0).sum(axis=0)
                sy = np.where(valid, flux, 0).sum(axis=0)
                sxx = np.where(valid, delta*delta, 0).sum(axis=0)
                sxy = np.where(valid, delta*flux, 0).sum(axis=0)
                denominator = n*sxx-sx*sx
                slope = np.divide(n*sxy-sx*sy, denominator, out=np.zeros_like(sx), where=np.abs(denominator) > 1e-18)
                intercept = np.divide(sy-slope*sx, n, out=np.full_like(sy, np.nan), where=n > 0)
                if iteration == 0:
                    residual = flux-(intercept+delta*slope)
                    mad = 1.4826*np.nanmedian(np.abs(np.where(valid, residual, np.nan)), axis=0)
                    valid &= np.abs(residual) <= np.maximum(3*mad, 1e-12)
            bracketed = (np.nanmin(np.where(valid, delta, np.nan), axis=0) <= 0) & (np.nanmax(np.where(valid, delta, np.nan), axis=0) >= 0)
            median = np.nanmedian(np.where(valid, flux, np.nan), axis=0)
            reference = np.where(bracketed, intercept, median)
            diff = frames[i]["flux"]-reference
            diff[n < 3] = np.nan
            sigma = float(1.4826*np.nanmedian(np.abs(diff-np.nanmedian(diff))))
        flags = frames[i]["flags"].copy()
        flags[~np.isfinite(diff)] |= NODATA
        result.append({"flux": diff.astype(np.float32), "flags": flags})
        info.append({**meta, "diff_available": bool(np.isfinite(diff).any()),
                     "reference_count": len(candidates), "diff_sigma": sigma if np.isfinite(sigma) else None})
    return info, result
