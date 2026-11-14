import gzip
import json

import numpy as np

MAGIC = b"SPXF"

def _shuffle(a: np.ndarray) -> bytes:
    b = np.ascontiguousarray(a, dtype="<f4").view(np.uint8).reshape(-1, 4)
    return b.T.copy().tobytes()

def _pad8(b: bytes) -> bytes:
    return b + b"\0" * ((-len(b)) % 8)

def write_spxf(path, header: dict, frames: list[dict], shuffle=True, gz=True):
    h = json.dumps(header, separators=(",", ":")).encode()
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
