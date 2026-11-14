"""Acceptance contract for the published scientific data package."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "apps/web/static/data"


def read(name):
    return json.loads((DATA / name).read_text())


NEO = read("neo/index.json")
OBJECTS = NEO["objects"]
TARGET_POSITIONS = {
    "barnard": [269.446268, 4.768204],
    "eps-indi-b": [331.096669, -56.800649],
    "wise-0855": [133.759765, -7.242182],
    "rw-aur": [76.956587, 30.401291],
    "r-dra": [248.167233, 66.755024],
}


@pytest.mark.parametrize(
    ("key", "expected"),
    [("candidates", 86), ("fitted", 62), ("A", 11), ("B", 17),
     ("provisional", 6), ("pha_AB", 7)],
)
def test_neo_counts(key, expected):
    assert NEO["counts"][key] == expected


@pytest.mark.parametrize(
    ("key", "expected"),
    [("eta", 1.48), ("eta_sigma", 0.44), ("trail_max_px", 3),
     ("floor_fraction", 0.35), ("cv_n", 50), ("cv_p16", 0.67), ("cv_p84", 1.36)],
)
def test_neo_method(key, expected):
    assert NEO["method"][key] == expected


def test_neo_catalog_size_and_tiers():
    assert len(OBJECTS) == 34
    assert len({o["slug"] for o in OBJECTS}) == 34
    for tier in ("A", "B", "provisional"):
        assert sum(o["tier"] == tier for o in OBJECTS) == NEO["counts"][tier]
    assert all(o["tier"] in {"A", "B", "provisional"} for o in OBJECTS)


@pytest.mark.parametrize("obj", OBJECTS, ids=lambda obj: obj["slug"])
def test_each_neo_has_required_values_and_interval(obj):
    required = {
        "pdes", "slug", "tier", "pha", "H", "D_km", "D16", "D84",
        "pV", "snr", "n_exp", "n_visits", "single_visit",
    }
    assert required <= obj.keys()
    assert obj["D16"] <= obj["D_km"] <= obj["D84"]


@pytest.mark.parametrize("obj", OBJECTS, ids=lambda obj: obj["slug"])
def test_each_neo_has_measurements(obj):
    points = read(f"neo/{obj['slug']}.json")["points"]
    assert isinstance(points, list)
    if obj["tier"] in {"A", "B"}:
        assert len(points) >= 8


def test_2025_yh5_preserves_published_interval_and_warning():
    obj = next(o for o in OBJECTS if o["pdes"] == "2025 YH5")
    assert obj["tier"] == "A"
    assert obj["pha"] is True
    assert obj["D_km"] == 0.949
    assert obj["D16"] == 0.61
    assert obj["D84"] == 1.363
    assert obj["single_visit"] is True


def test_neo_validation_sample():
    assert len(read("neo/validation.json")["cv"]) == 50


def test_exactly_five_target_summaries():
    assert {p.stem for p in (DATA / "targets").glob("*.json")} == set(TARGET_POSITIONS)


@pytest.mark.parametrize("slug", TARGET_POSITIONS)
def test_field_notes_include_caveat(slug):
    target = read(f"targets/{slug}.json")
    assert isinstance(target["notes"], list) and target["notes"]
    assert isinstance(target["caveat"], str) and target["caveat"].strip()


def test_wise0855_deblended_spectrum():
    spectrum = read("targets/wise-0855.json")["spectrum"]
    blue = [s for s in spectrum if s["lam"] < 3.0]
    red = [s for s in spectrum if 4.2 <= s["lam"] <= 4.7]
    assert blue and red
    assert all(s["f"] < 0.1 for s in blue)
    assert all(s["f"] > 0.3 for s in red)


def test_calibration_bands_and_sample_size():
    calibration = read("calibration.json")
    bands = calibration["validation"]
    assert calibration["n_stars"] == 41
    assert len(bands) == 5
    assert {v["band"] for v in bands} == {"J", "H", "Ks", "W1", "W2"}
    assert all(0.97 <= v["ratio"] <= 1.02 for v in bands)


@pytest.mark.parametrize(("slug", "position"), TARGET_POSITIONS.items())
def test_reference_positions_at_2026_01_01(slug, position):
    targets = read("targets.json")["targets"]
    target = next(t for t in targets if t["slug"] == slug)
    assert target["pos_2026_01_01"] == position


def test_channels_cover_all_frames_in_order():
    channels = read("channels.json")["channels"]
    assert len(channels) == 102
    assert [c["frame"] for c in channels] == list(range(102))


def test_exported_json_package_is_smaller_than_one_megabyte():
    # Step 3's exported JSON budget is independent of step 5's binary target packages.
    files = [*DATA.glob("*.json"), *(DATA / "neo").glob("*.json"), *(DATA / "targets").glob("*.json")]
    assert sum(p.stat().st_size for p in files) < 1_000_000


def test_exposure_index_contract():
    from pyarrow.parquet import ParquetFile

    index = ParquetFile(ROOT / "data/spherex_exposures_d456_dr1_qr3.parquet")
    assert index.metadata.num_rows == 809_593
    assert set(index.schema.names) == {"obs_id", "coll", "det", "t_min", *[f"c{i}" for i in range(8)]}
