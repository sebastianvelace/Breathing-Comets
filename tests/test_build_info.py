"""build.json is generated from product files, not typed."""

import gzip
import json
import struct
import subprocess
import sys

import pyarrow.parquet as pq
from spxcore.config import ROOT

STATIC = ROOT / "apps/web/static/data"


def build():
    return json.loads((STATIC / "build.json").read_text())


def test_values_match_their_sources():
    b = build()
    assert b["exposure_index"]["rows_d4_d6"] == pq.ParquetFile(ROOT / "data/spherex_exposures_d456_dr1_qr3.parquet").metadata.num_rows
    raw = gzip.decompress((STATIC / "targets/barnard/D4.spxf.gz").read_bytes())
    length = struct.unpack_from("<4sHHII", raw)[3]
    assert b["data_version"] == json.loads(raw[16:16 + length])["data_version"]
    cal = json.loads((STATIC / "calibration.json").read_text())
    assert b["photometry"]["n_stars"] == cal["n_stars"] and b["photometry"]["ratio_mean"] == cal["ratio_mean"]
    assert b["products"]["stacks"] == len(list(STATIC.rglob("*.spxf.gz")))
    assert b["channels"]["n"] == 102
    atlas = json.loads((STATIC / "comets/index.json").read_text())
    assert b["products"]["comets"] == atlas["counts"]["comets"]


def test_git_commit_is_a_real_commit():
    commit = build()["git"]["commit"]
    assert len(commit) == 40
    assert subprocess.run(["git", "cat-file", "-t", commit], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip() == "commit"


def test_regeneration_changes_only_time_and_commit():
    before = build()
    subprocess.run([sys.executable, str(ROOT / "pipelines/build_info.py")], check=True, capture_output=True)
    after = build()
    for doc in (before, after):
        doc.pop("generated"), doc.pop("git")
    assert before == after
