"""Render lightweight landing plates from the precomputed SPXF target packages.

Reads only ``apps/web/static/data/targets/<slug>/`` (manifest, stacks, Diff λ and
Gaia) and writes lossless WebP plates plus ``landing-media.json`` to
``apps/web/static/media/landing/``. No science is recalculated:

* stacks use their own common ``stretch_hint`` with the Explorer mapping
  ``asinh(20 x) / asinh(20)`` (identical across epochs of one stack);
* OVERFLOW (SPXF bit 1) is painted white BEFORE NaN / NODATA is considered;
* north is up and east is left (row 0 of the grid is the southern edge);
* Diff λ uses the Explorer mapping ``0.5 + 0.5 v / (5 σ)`` with the frame's own
  ``diff_sigma``. The raw subtraction is rendered with the same σ and is always
  labelled as a raw difference, never as Diff λ;
* pixels are never resampled or smoothed: the browser scales them as blocks.

Usage: ``python pipelines/landing_media.py``
"""

import gzip
import json
import struct
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "apps/web/static/data"
OUT = ROOT / "apps/web/static/media/landing"
SLUGS = ["barnard", "eps-indi-b", "wise-0855", "rw-aur", "r-dra"]
OVERFLOW, NODATA = 1 << 1, 1 << 13
PLATE = np.array([11, 11, 10], float)
PLATE_INK = np.array([236, 231, 220], float)
CYAN = np.array([127, 212, 230], float)
OCHRE = np.array([242, 160, 61], float)
CREDITS = [
    "SPHEREx: NASA/JPL-Caltech/IRSA (DR1 + QR3, L2 l2b-v27)",
    "Gaia DR3: ESA/Gaia/DPAC",
]


def _reject_constant(value):
    raise ValueError(f"Invalid JSON constant: {value}")


def read_stack(path):
    raw = gzip.decompress(path.read_bytes())
    magic, version, bitflags, length, reserved = struct.unpack_from("<4sHHII", raw)
    if (magic, version, reserved) != (b"SPXF", 1, 0):
        raise ValueError(f"{path}: not SPXF v1")
    header = json.loads(raw[16:16 + length], parse_constant=_reject_constant)
    nx, ny = header["grid"]["nx"], header["grid"]["ny"]
    pixels, offset = nx * ny, 16 + length

    def plane():
        nonlocal offset
        data = np.frombuffer(raw[offset:offset + pixels * 4], np.uint8)
        offset += (pixels * 4 + 7) // 8 * 8
        if bitflags & 1:
            data = data.reshape(4, pixels).T.copy().ravel()
        return data.view("<f4").reshape(ny, nx)

    frames = []
    for _ in header["frames"]:
        flux = plane()
        if header.get("has_var"):
            plane()
        flags = np.frombuffer(raw[offset:offset + pixels * 2], "<u2").reshape(ny, nx)
        offset += (pixels * 2 + 7) // 8 * 8
        frames.append((flux, flags))
    if offset != len(raw):
        raise ValueError(f"{path}: trailing bytes")
    return header, frames


def _paint(t, lut_low, lut_high, flux, flags):
    rgb = lut_low + (lut_high - lut_low) * t[..., None]
    empty = ~np.isfinite(flux) | ((flags & NODATA) != 0)
    rgb[empty] = PLATE
    rgb[(flags & OVERFLOW) != 0] = 255  # saturation has priority over NaN
    return rgb


def stretch_rgb(flux, flags, lo, hi):
    x = np.clip((np.nan_to_num(flux, nan=lo) - lo) / max(hi - lo, 1e-10), 0, 1)
    return _paint(np.arcsinh(20 * x) / np.arcsinh(20), PLATE, PLATE_INK, flux, flags)


def diverging_rgb(value, flags, sigma):
    t = np.clip(0.5 + 0.5 * np.nan_to_num(value) / (5 * max(sigma, 1e-10)), 0, 1)
    low = np.where(t[..., None] < 0.5, CYAN, PLATE)
    high = np.where(t[..., None] < 0.5, PLATE, OCHRE)
    u = np.where(t < 0.5, t * 2, (t - 0.5) * 2)
    rgb = low + (high - low) * u[..., None]
    empty = ~np.isfinite(value) | ((flags & NODATA) != 0)
    rgb[empty] = PLATE
    rgb[(flags & OVERFLOW) != 0] = 255
    return rgb


def save(rgb, name):
    # Grid row 0 is south: flip so north is up. Columns already run east → west.
    image = Image.fromarray(np.flipud(np.round(rgb)).astype(np.uint8), "RGB")
    path = OUT / name
    image.save(path, "WEBP", lossless=True, quality=100, method=6)
    return {"src": f"/media/landing/{name}", "width": image.width, "height": image.height,
            "bytes": path.stat().st_size}


def frame_meta(frame, det, kind):
    keep = ("obs_id", "date", "mjd", "lam_um", "bw_um", "collection", "visit", "k")
    meta = {key: frame[key] for key in keep}
    meta.update(det=det, kind=kind)
    return meta


def valid_fraction(flux, flags):
    return float(np.mean(np.isfinite(flux) & ((flags & NODATA) == 0)))


def best_frame(frames, indices):
    return max(indices, key=lambda k: (valid_fraction(*frames[k]), -k))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plates, sources = {}, []
    for slug in SLUGS:
        folder = DATA / "targets" / slug
        manifest = json.loads((folder / "manifest.json").read_text())
        det = manifest["default_det"]
        stack_path = folder / manifest["stacks"][str(det)]
        header, frames = read_stack(stack_path)
        sources.append(str(stack_path.relative_to(ROOT)))
        lo, hi = header["stretch_hint"]["lo"], header["stretch_hint"]["hi"]
        k = best_frame(frames, range(len(frames)))
        entry = {
            "slug": slug, "name": manifest["name"], "det": det, "grid": header["grid"],
            "stretch": {"lo": lo, "hi": hi, "map": "asinh(20x)/asinh(20)"},
            "n_frames": len(frames), "n_visits": len(header["visits"]),
            "pm": manifest.get("pm"),
            "poster": {**save(stretch_rgb(*frames[k], lo, hi), f"{slug}-d{det}-poster.webp"),
                       **frame_meta(header["frames"][k], det, "stack")},
        }
        if slug == "barnard":
            epochs = []
            for visit in header["visits"]:
                members = [i for i, f in enumerate(header["frames"]) if f["visit"] == visit["visit"]]
                i = best_frame(frames, members)
                epochs.append({**save(stretch_rgb(*frames[i], lo, hi),
                                      f"barnard-d{det}-visit{visit['visit']}.webp"),
                               **frame_meta(header["frames"][i], det, "stack")})
            entry["epochs"] = epochs

            diff_path = folder / manifest["diff"][str(det)]
            diff_header, diff_frames = read_stack(diff_path)
            sources.append(str(diff_path.relative_to(ROOT)))
            last = epochs[-1]["k"]
            target_frame = diff_header["frames"][last]
            if not target_frame.get("diff_available"):
                raise ValueError("Diff λ unavailable for the selected frame")
            sigma = target_frame["diff_sigma"]
            # Raw comparison partner: the frame from another visit with the
            # largest wavelength mismatch, which is exactly what Diff λ avoids.
            # Only well-covered frames qualify, so the comparison is not dominated by NODATA.
            others = [i for i, f in enumerate(header["frames"])
                      if f["visit"] != header["frames"][last]["visit"]
                      and valid_fraction(*frames[i]) >= 0.95]
            partner = max(others, key=lambda i: abs(header["frames"][i]["lam_um"]
                                                     - header["frames"][last]["lam_um"]))
            flux_b, flags_b = frames[last]
            flux_a, flags_a = frames[partner]
            raw = flux_b - flux_a
            entry["difference"] = {
                "sigma": sigma, "map": "0.5 + 0.5 v / (5 sigma)",
                "reference_count": target_frame.get("reference_count"),
                "diff_lambda": {**save(diverging_rgb(diff_frames[last][0], diff_frames[last][1], sigma),
                                       f"barnard-d{det}-difflambda-k{last}.webp"),
                                **frame_meta(target_frame, det, "diff_lambda")},
                "raw": {**save(diverging_rgb(raw, flags_a | flags_b, sigma),
                               f"barnard-d{det}-raw-k{last}-minus-k{partner}.webp"),
                        "kind": "raw_subtraction",
                        "a": frame_meta(header["frames"][partner], det, "stack"),
                        "b": frame_meta(header["frames"][last], det, "stack")},
            }
            gaia_id = manifest.get("gaia_target_id")
            gaia = json.loads((folder / manifest["gaia"]).read_text())
            star = next((s for s in gaia if s["source_id"] == gaia_id), None)
            entry["gaia_counterpart"] = None if star is None else {
                key: star[key] for key in ("source_id", "ra", "dec", "pmra", "pmdec", "ref_epoch")}
            sources.append(str((folder / manifest["gaia"]).relative_to(ROOT)))
        plates[slug] = entry
    out = {"generated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ"),
           "generator": "pipelines/landing_media.py", "sources": sources,
           "credits": CREDITS, "orientation": "north up, east left; pixels not resampled",
           "plates": plates}
    (OUT / "landing-media.json").write_text(json.dumps(out, indent=1, allow_nan=False))
    total = sum(p.stat().st_size for p in OUT.iterdir())
    print(f"wrote {len(list(OUT.iterdir()))} files, {total} bytes to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
