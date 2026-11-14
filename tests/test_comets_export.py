"""The comet atlas is a faithful, honest export of the retained research CSVs."""

import csv
import json
import math
import subprocess
import sys

import pytest
from spxcore.config import ROOT

SRC = ROOT / "data/derived/comets"
INDEX = ROOT / "apps/web/static/data/comets/index.json"


@pytest.fixture(scope="module")
def atlas():
    return json.loads(INDEX.read_text())


def csv_rows(name):
    with open(SRC / name, newline="", encoding="utf-8") as handle:
        return {r["name"]: r for r in csv.DictReader(handle)}


def test_every_census_comet_is_exported_once(atlas):
    census = csv_rows("co2_census_physical.csv")
    assert {c["name"] for c in atlas["comets"]} == set(census)
    assert len({c["slug"] for c in atlas["comets"]}) == len(census) == atlas["counts"]["comets"]


def test_numbers_are_copied_from_the_csv(atlas):
    census = csv_rows("co2_census_physical.csv")
    for comet in atlas["comets"]:
        row = census[comet["name"]]
        assert comet["co2"]["q50"] == float(row["QA_50"])
        assert comet["co2"]["q16"] == float(row["QA_16"])
        assert comet["co2"]["q84"] == float(row["QA_84"])
        assert comet["co2"]["snr_det"] == float(row["snr_detect"])
        assert comet["co2"]["chi2_red"] == float(row["chi2_phys"])
        assert comet["r_au"] == float(row["r_au"])
        assert comet["co2"]["q16"] < comet["co2"]["q50"] < comet["co2"]["q84"]


def test_status_rule_and_honesty_flags(atlas):
    by = {c["name"]: c for c in atlas["comets"]}
    for comet in atlas["comets"]:
        snr, chi2 = comet["co2"]["snr_det"], comet["co2"]["chi2_red"]
        expected = ("detected" if chi2 < 50 else "with_systematics") if snr >= 5 else ("marginal" if snr >= 3 else "not_detected")
        assert comet["co2"]["status"] == expected
    assert by["3I/ATLAS"]["co2"]["status"] == "with_systematics"  # chi2 185
    assert by["C/2025 A6 (Lemmon)"]["co2"]["status"] == "with_systematics"  # chi2 72
    assert by["C/2022 N2 (PANSTARRS)"]["co2"]["snr_det"] > 60
    assert "far_unreliable" in by["C/2014 UN271 (Bernardinelli-Bernstein)"]["flags"]
    assert sum(atlas["counts"][s] for s in ("detected", "with_systematics", "marginal", "not_detected")) == len(by)


def test_velocity_systematic_is_about_forty_percent(atlas):
    values = [c["co2"]["sys_v"] for c in atlas["comets"]]
    assert all(0.55 < v < 0.65 for v in values)


def test_validation_rows_carry_sources_and_measured_values(atlas):
    rows = {v["id"]: v for v in atlas["validation"]}
    aug = rows["3i-atlas_co2_2025-08"]
    assert aug["measured"] == pytest.approx(1.17e27) and aug["chi2_red"] < 50
    assert aug["published_lo"] < aug["measured"] < aug["published_hi"]
    assert "2508.15469" in aug["source"] and "2512.07318" in aug["source"]
    co = csv_rows("co_census_final.csv")["29P/Schwassmann-Wachmann"]
    p29 = rows["29p_co_2025-12"]
    assert p29["measured"] == float(co["QCO_50"])
    assert p29["published_lo"] < p29["measured"] < p29["published_hi"]
    assert {p["id"] for p in atlas["pending"]} == {"3i-atlas_h2o_2025-08"}


def test_no_non_finite_numbers(atlas):
    def walk(x):
        if isinstance(x, float):
            assert math.isfinite(x)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(atlas)


def test_export_is_reproducible(atlas):
    before = json.loads(INDEX.read_text())
    subprocess.run([sys.executable, str(ROOT / "pipelines/export_comets.py")], check=True, capture_output=True)
    after = json.loads(INDEX.read_text())
    before.pop("generated"), after.pop("generated")
    assert before == after
