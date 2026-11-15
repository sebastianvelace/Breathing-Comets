import gzip
import json

import numpy as np

MAGIC = b"SPXF"


def stack_header(target, grid, metadata, frames, detector, kind="stack", include_var=False):
    """Describe actual frames and a single fixed stretch for the entire stack."""
    from datetime import UTC, datetime

    from .calib import SWCS

    samples = np.concatenate([f["flux"].ravel() for f in frames])
    samples = samples[np.isfinite(samples)]
    if not len(samples):
        raise ValueError("Stack contains no finite sky data")
    low, high = np.percentile(samples, [0.5, 99.5])
    visits = []
    for visit in sorted({m["visit"] for m in metadata}):
        dates = [m["mjd"] for m in metadata if m["visit"] == visit]
        visits.append({"visit": visit, "mjd_min": min(dates), "mjd_max": max(dates), "n": len(dates)})
    return {"spxf": 1, "kind": kind, "target": target, "grid": grid, "units": "MJy/sr",
            "has_var": include_var, "det": detector,
            "stretch_hint": {"p_lo": 0.5, "p_hi": 99.5, "lo": float(low), "hi": float(high)},
            "data_version": {"releases": ["dr1", "qr3"], "l2": "l2b-v27", "spectral_wcs": SWCS},
            "frames": [{**m, "k": i} for i, m in enumerate(metadata)], "visits": visits,
            "provenance": {"generator": "spxcore 0.1.0", "created": datetime.now(UTC).isoformat()}}

def _shuffle(a: np.ndarray) -> bytes:
    b = np.ascontiguousarray(a, dtype="<f4").view(np.uint8).reshape(-1, 4)
    return b.T.copy().tobytes()

def _pad8(b: bytes) -> bytes:
    return b + b"\0" * ((-len(b)) % 8)

def read_spxf(path):
    """Read an SPXF v1 file written by write_spxf; returns (header, frames)."""
    raw = open(path, "rb").read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    if raw[:4] != MAGIC:
        raise ValueError("Not an SPXF file")
    shuffled = int(np.frombuffer(raw[6:8], "<u2")[0]) & 1
    length = int(np.frombuffer(raw[8:12], "<u4")[0])
    header = json.loads(raw[16:16+length])
    ny, nx = header["grid"]["ny"], header["grid"]["nx"]
    pixels, offset, frames = nx*ny, 16+length, []

    def take(nbytes):
        nonlocal offset
        chunk = raw[offset:offset+nbytes]
        offset += nbytes + (-nbytes) % 8
        return chunk

    def plane():
        a = np.frombuffer(take(pixels*4), np.uint8)
        if shuffled:
            a = a.reshape(4, pixels).T.copy().ravel()
        return a.view("<f4").reshape(ny, nx).copy()

    for _ in header["frames"]:
        frame = {"flux": plane()}
        if header.get("has_var"):
            frame["var"] = plane()
        frame["flags"] = np.frombuffer(take(pixels*2), "<u2").reshape(ny, nx).copy()
        frames.append(frame)
    return header, frames


def write_spxf(path, header: dict, frames: list[dict], shuffle=True, gz=True):
    h = json.dumps(header, separators=(",", ":"), allow_nan=False).encode()
    h += b" " * ((-len(h)) % 8)
    out = [MAGIC, np.uint16(1).tobytes(), np.uint16(1 if shuffle else 0).tobytes(),
           np.uint32(len(h)).tobytes(), np.uint32(0).tobytes(), h]
    for f in frames:
        flux = f["flux"].astype("<f4")
        out.append(_pad8(_shuffle(flux) if shuffle else flux.tobytes()))
        if header.get("has_var"):
            var = f["var"].astype("<f4")
            out.append(_pad8(_shuffle(var) if shuffle else var.tobytes()))
        out.append(_pad8(f["flags"].astype("<u2").tobytes()))
    data = b"".join(out)
    with (gzip.open(path, "wb", compresslevel=9) if gz else open(path, "wb")) as fh:
        fh.write(data)
