"""Controlled synthetic counterexamples; never used as product observations."""

import asyncio, json, numpy as np
from unittest.mock import patch, AsyncMock
from astropy.wcs import WCS
from spxcore import cutout, sky, flags, comets
from scipy.integrate import quad


async def reprojection():
    w = WCS(naxis=2)
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    w.wcs.crval = [30, 10]
    w.wcs.crpix = [1021, 1021]
    w.wcs.cdelt = [-6.15 / 3600, 6.15 / 3600]
    header = w.to_header()
    header["MJD-AVG"] = 61000.0
    header["PSF_FWHM"] = 6.2
    # A real TAN reprojection, half a native pixel in both axes, samples four pixels equally.
    grid = {"nx": 3, "ny": 3, "crpix": [2, 2]}
    rows = {
        "IMAGE": np.zeros((2040, 2040), np.float32),
        "FLAGS": np.zeros((2040, 2040), np.int32),
        "VARIANCE": np.ones((2040, 2040), np.float32),
    }
    rows["IMAGE"][1021, 1021] = 100
    rows["FLAGS"][1021, 1021] = 1 << 2

    async def getrows(key, layout, y0, y1, names):
        return {k: rows[k][y0:y1] for k in names}

    maps = (
        np.full((2040, 2040), 4.0, np.float32),
        np.full((2040, 2040), 0.03, np.float32),
    )
    # Use the same input tangent point but shift the small output grid to fractional native pixels.
    out = WCS(naxis=2)
    out.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    out.wcs.crval = w.pixel_to_world_values(1020.49, 1020.49)
    out.wcs.crpix = [2, 2]
    out.wcs.cdelt = w.wcs.cdelt
    with (
        patch.object(
            cutout.fitsio,
            "read_hdu_layout",
            AsyncMock(return_value=[{"name": "IMAGE", "header": header}]),
        ),
        patch.object(cutout.fitsio, "read_rows", getrows),
        patch.object(cutout.calib, "load_maps", AsyncMock(return_value=maps)),
        patch.object(cutout, "output_grid", return_value=(out, grid)),
    ):
        _, meta, frame = await cutout._make_frame(
            {"obs_id": "AUDIT_SYNTHETIC", "det": 4, "visit": 0},
            30,
            10,
            0.05,
            True,
            "AUDIT_SYNTHETIC",
        )
    xx, yy = w.world_to_pixel_values(*out.wcs.crval)
    fx, fy = xx % 1, yy % 1
    weights = np.array([(1 - fx) * (1 - fy), fx * (1 - fy), (1 - fx) * fy, fx * fy])
    return {
        "synthetic": True,
        "input_fraction": [fx, fy],
        "output_flux": float(frame["flux"][1, 1]),
        "flagged_input_flux": 100.0,
        "output_flags": int(frame["flags"][1, 1]),
        "official_hard_flag_masked": bool(
            frame["flags"][1, 1]
            & int(flags.remap_flags(np.array([flags.HARD_ES21], dtype=np.int64))[0])
        ),
        "returned_variance": float(frame["var"][1, 1]),
        "independent_pixel_variance": float(weights @ weights),
        "variance_factor": float(frame["var"][1, 1] / (weights @ weights)),
    }


def bad_reference():
    grid = {"nx": 2, "ny": 2, "crpix": [1, 1]}
    meta = [
        {
            "mjd": 61000 + i * 3,
            "visit": i,
            "lam_um": 4.5,
            "bw_um": 0.1,
            "lam_poly": [4.5, 0, 0, 0, 0, 0],
        }
        for i in range(4)
    ]
    frames = [
        {
            "flux": np.full((2, 2), x, np.float32),
            "flags": np.full((2, 2), 4 if i == 1 else 0, np.uint16),
        }
        for i, x in enumerate([10.0, 100.0, 10.0, 10.0])
    ]
    info, result = sky.difference_stack(meta, frames, grid)
    return {
        "synthetic": True,
        "true_static_flux": 10.0,
        "invalid_reference_flux": 100.0,
        "invalid_reference_flags": 4,
        "result_flux": float(result[0]["flux"][0, 0]),
        "result_flags": int(result[0]["flags"][0, 0]),
        "diff_available": info[0]["diff_available"],
        "expected": "No valid three-reference result: only two unflagged references remain.",
    }


def unbracketed_color():
    wavelengths = [4.5, 4.52, 4.54, 4.56]
    meta = [
        {
            "mjd": 61000 + i * 3,
            "visit": i,
            "lam_um": x,
            "bw_um": 0.03,
            "lam_poly": [x, 0, 0, 0, 0, 0],
        }
        for i, x in enumerate(wavelengths)
    ]
    frames = [
        {
            "flux": np.full((2, 2), 10 + 100 * x, np.float32),
            "flags": np.zeros((2, 2), np.uint16),
        }
        for x in wavelengths
    ]
    info, result = sky.difference_stack(
        meta, frames, {"nx": 2, "ny": 2, "crpix": [1, 1]}
    )
    return {
        "synthetic": True,
        "sky_changes": False,
        "wavelengths_um": wavelengths,
        "returned_difference": float(result[0]["flux"][0, 0]),
        "diff_available": info[0]["diff_available"],
        "expected_same_color_difference": 0.0,
    }


def haser_check():
    checks = []
    for x in (0.001, 0.01, 0.1, 1.0, 10.0):
        # Integrate the spherical parent population inside a line-of-sight cylinder.
        # This is independent of the modified-Bessel identity in the product.
        integrand = lambda u: (
            np.exp(-u) * (x / u) ** 2 / (1 + np.sqrt(max(0.0, 1 - (x / u) ** 2)))
        )
        direct = (
            -np.expm1(-x)
            + quad(integrand, x, np.inf, epsabs=1e-12, epsrel=1e-10, limit=200)[0]
        )
        native = comets.haser_fraction(x)
        checks.append(
            {
                "aperture_over_scale": x,
                "direct_integral": direct,
                "product": native,
                "relative_error": abs(native / direct - 1),
            }
        )
    return checks


async def main():
    print(
        json.dumps(
            {
                "reprojection": await reprojection(),
                "bad_reference": bad_reference(),
                "unbracketed_color": unbracketed_color(),
                "haser_independent_integral": haser_check(),
            },
            indent=2,
        )
    )


asyncio.run(main())
