"""Comet detail packets are faithful exports of stored stacks and spectra."""

import csv
import json
import math

import pytest
from spxcore.config import ROOT

DATA = ROOT / "apps/web/static/data/comets"
SPECTRA = ROOT / "data/derived/comets/spectra"
SLUGS = ["3i-atlas", "29p-schwassmann-wachmann"]


def packet(slug):
    return json.loads((DATA / f"{slug}.json").read_text())


@pytest.mark.parametrize("slug", SLUGS)
def test_frames_exist_ordered_by_wavelength_and_match_stack(slug):
    import sys

    sys.path.insert(0, str(ROOT / "pipelines"))
    from landing_media import read_stack

    p = packet(slug)
    for epoch in p["epochs"]:
        header, _ = read_stack(ROOT / "apps/web/static" / epoch["stack"].lstrip("/"))
        by_obs = {f["obs_id"]: f for f in header["frames"]}
        lams = [f["lam_um"] for f in epoch["frames"]]
        assert lams == sorted(lams) and len(lams) >= 10
        assert epoch["stretch"]["lo"] == header["stretch_hint"]["lo"]
        for f in epoch["frames"]:
            assert (ROOT / "apps/web/static" / f["src"].lstrip("/")).is_file()
            src = by_obs[f["obs_id"]]
            assert f["mjd"] == src["mjd"] and f["lam_um"] == src["lam_um"]
            assert f["in_co2_band"] == (4.21 <= f["lam_um"] <= 4.31)
            assert (f["width"], f["height"]) == (header["grid"]["nx"], header["grid"]["ny"])


def test_spectra_follow_census_filters_and_convert_jy_to_mjy():
    p = packet("29p-schwassmann-wachmann")
    with open(SPECTRA / "29P_Schwassmann-Wachmann.skysub.csv.txt", newline="", encoding="utf-8") as handle:
        all_rows = list(csv.DictReader(handle))
    rows = [r for r in all_rows
            if r["det"] == "D5" and float(r["e3_jy"]) > 0 and float(r["f3_jy"]) != 0
            and math.isfinite(float(r["f3_jy"])) and 3.85 <= float(r["lam_um"]) <= 4.42]
    exported = p["spectrum"]["by_epoch"]["2025-12"]["d5"]
    assert len(exported) == len(rows) == 32
    assert sorted(x["f"] for x in exported) == pytest.approx(sorted(float(r["f3_jy"]) * 1e3 for r in rows))
    assert all(3.85 <= x["lam"] <= 4.42 and x["e"] > 0 for x in exported)


def test_3i_august_spectrum_is_the_validated_epoch_and_has_no_co_spectrum():
    p = packet("3i-atlas")
    aug = p["spectrum"]["by_epoch"]["2025-08"]
    assert len(aug["d5"]) == 23 and aug["d6"] is None
    assert p["spectrum"]["by_epoch"]["2025-12"]["d6"]


@pytest.mark.parametrize("slug", SLUGS)
def test_census_block_equals_atlas(slug):
    atlas = json.loads((DATA / "index.json").read_text())
    entry = next(c for c in atlas["comets"] if c["slug"] == slug)
    assert packet(slug)["census"]["co2"] == entry["co2"]
    assert packet(slug)["validation"] == [v for v in atlas["validation"] if v["comet"] == entry["name"]]
