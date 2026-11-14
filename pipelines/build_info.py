"""Write ``apps/web/static/data/build.json``: the provenance record shown on /method.

Every value is read from a product file at generation time (stack header, parquet and npz
indices, calibration and atlas JSON) or from git. Nothing is typed in.

Usage: ``python pipelines/build_info.py``
"""

import gzip
import json
import struct
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "apps/web/static/data"
OUT = STATIC / "build.json"


def header(path):
    raw = gzip.decompress(path.read_bytes())
    length = struct.unpack_from("<4sHHII", raw)[3]
    return json.loads(raw[16:16 + length])


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def main():
    import numpy as np

    stack = header(STATIC / "targets/barnard/D4.spxf.gz")
    calibration = json.loads((STATIC / "calibration.json").read_text())
    atlas = json.loads((STATIC / "comets/index.json").read_text())
    neo = json.loads((STATIC / "neo/index.json").read_text())
    channels = json.loads((STATIC / "channels.json").read_text())["channels"]
    index = pq.ParquetFile(ROOT / "data/spherex_exposures_d456_dr1_qr3.parquet")
    keys = np.load(ROOT / "data/spherex_s3_keys_compact.npz", allow_pickle=False)
    stacks = sorted(p.relative_to(STATIC).as_posix() for p in STATIC.rglob("*.spxf.gz"))
    out = {
        "generated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ"),
        "generator": "pipelines/build_info.py",
        "git": {"commit": git("rev-parse", "HEAD"),
                "note": "commit that was HEAD when this file was generated; the file itself is committed afterwards"},
        "data_version": stack["data_version"],
        "exposure_index": {"rows_d4_d6": index.metadata.num_rows, "file": "data/spherex_exposures_d456_dr1_qr3.parquet",
                           "s3_keys": int(keys["ids"].shape[0])},
        "channels": {"n": len(channels), "wavelength_um": [channels[0]["wavelength_um"], channels[-1]["wavelength_um"]]},
        "photometry": {"rule": calibration["rule"], "n_stars": calibration["n_stars"], "fields": calibration["fields"],
                       "ratio_mean": calibration["ratio_mean"], "ratio_min": calibration["ratio_min"],
                       "ratio_max": calibration["ratio_max"]},
        "products": {"targets": 5, "stacks": len(stacks), "comets": atlas["counts"]["comets"],
                     "neo": {k: neo["counts"][k] for k in ("A", "B", "provisional", "pha_AB")}},
    }
    OUT.write_text(json.dumps(out, indent=1, allow_nan=False))
    print(f"wrote {OUT.relative_to(ROOT)}: {out['exposure_index']['rows_d4_d6']} index rows, {len(stacks)} stacks")


if __name__ == "__main__":
    main()
