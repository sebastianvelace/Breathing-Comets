"""Scientific and binary acceptance checks with explicit synthetic fixtures."""

import asyncio
import gzip
import json
import struct
import subprocess
from pathlib import Path

import numpy as np
import pytest
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from spxcore import calib, cutout, ephem, fitsio, flags, known, s3, sky, spxf
from spxcore.index import polygon_contains, sample_visits

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("shuffle", [False, True])
@pytest.mark.parametrize("gz", [False, True])
@pytest.mark.parametrize("has_var", [False, True])
def test_spxf_roundtrip(tmp_path, shuffle, gz, has_var):
    header = {"spxf": 1, "grid": {"nx": 3, "ny": 3}, "has_var": has_var, "frames": [{"k": 0}]}
    flux = np.arange(9, dtype=np.float32).reshape(3, 3)
    flux[1, 1] = np.nan
    variance = np.ones((3, 3), np.float32)
    mask = np.arange(9, dtype=np.uint16).reshape(3, 3)
    path = tmp_path / "fixture.spxf"
    spxf.write_spxf(path, header, [{"flux": flux, "flags": mask, "var": variance}], shuffle=shuffle, gz=gz)
    payload = gzip.decompress(path.read_bytes()) if gz else path.read_bytes()
    magic, version, bitflags, length, reserved = struct.unpack("<4sHHII", payload[:16])
    assert (magic, version, bitflags, reserved) == (b"SPXF", 1, int(shuffle), 0)
    assert length % 8 == 0
    assert json.loads(payload[16:16+length]) == header
    offset = 16+length
    raw = np.frombuffer(payload[offset:offset+36], np.uint8)
    restored = (raw.reshape(4, 9).T.copy().reshape(-1) if shuffle else raw).view("<f4").reshape(3, 3)
    np.testing.assert_equal(restored, flux)
    uncompressed = tmp_path / "raw.spxf"
    uncompressed.write_bytes(payload)
    # Exercise the real browser parser against bytes produced by Python.
    script = """
      import { readFileSync } from 'node:fs';
      import { parseSpxf } from './apps/web/src/lib/data/spxf.ts';
      const b = readFileSync(process.argv[1]);
      const p = parseSpxf(b.buffer.slice(b.byteOffset, b.byteOffset+b.byteLength));
      if(p.frames.length !== 1 || p.frames[0].flux[8] !== 8 || !Number.isNaN(p.frames[0].flux[4])) throw Error('float roundtrip');
      if(p.frames[0].flags[8] !== 8) throw Error('flags roundtrip');
      if(p.header.has_var && p.frames[0].var[0] !== 1) throw Error('variance roundtrip');
    """
    subprocess.run(["node", "--input-type=module", "-e", script, str(uncompressed)], cwd=ROOT, check=True, capture_output=True)


def test_reproject_identity():
    wcs, grid = cutout.output_grid(ra=120, dec=30, fov=0.05)
    n = grid["nx"]
    fixture = np.random.default_rng(12).uniform(1, 10, (n, n))
    result = cutout.reproject_array(fixture, wcs, wcs, fixture.shape)
    assert np.max(np.abs(result[2:-2, 2:-2]/fixture[2:-2, 2:-2]-1)) < 1e-5


def test_spxf_rejects_nonfinite_json_header(tmp_path):
    with pytest.raises(ValueError, match="Out of range float"):
        spxf.write_spxf(tmp_path / "bad.spxf", {"lam_um": float("nan")}, [])


def test_saturated_flux_does_not_invalidate_wavelength_or_edge(monkeypatch):
    wcs = WCS(naxis=2)
    wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    wcs.wcs.crval = [120, 30]
    wcs.wcs.crpix = [1020.5, 1020.5]
    wcs.wcs.cdelt = [-6.15/3600, 6.15/3600]
    header = wcs.to_header()
    header["MJD-AVG"], header["PSF_FWHM"] = 61041.0, 6.0

    async def layout(key):
        return [{"name": "IMAGE", "header": header}]

    async def rows(key, layout, y0, y1, names):
        image = np.ones((y1-y0, 2040), np.float32)
        image[1020-y0, 1020] = np.nan
        return {"IMAGE": image, "FLAGS": np.zeros(image.shape, np.int64)}

    async def maps(det):
        return np.full((2040, 2040), 4.0, np.float32), np.full((2040, 2040), 0.05, np.float32)

    monkeypatch.setattr(fitsio, "read_hdu_layout", layout)
    monkeypatch.setattr(fitsio, "read_rows", rows)
    monkeypatch.setattr(calib, "load_maps", maps)
    grid, meta, frame = asyncio.run(cutout._make_frame(
        {"obs_id": "synthetic-fixture", "det": 4, "visit": 0}, 120, 30, 0.05, False, "fixture"))
    center = grid["nx"]//2
    assert np.isnan(frame["flux"][center, center])
    assert meta["lam_um"] == 4.0
    assert meta["bw_um"] == pytest.approx(0.05)
    assert meta["edge"] is False
    json.dumps(meta, allow_nan=False)


def test_reproject_vs_pkg():
    from reproject import reproject_interp

    wcs, grid = cutout.output_grid(ra=120, dec=30, fov=0.05)
    shifted = wcs.deepcopy()
    shifted.wcs.crpix += [0.35, -0.2]
    fixture = np.random.default_rng(5).uniform(1, 10, (grid["ny"], grid["nx"]))
    ours = cutout.reproject_array(fixture, wcs, shifted, fixture.shape)
    expected, _ = reproject_interp((fixture, wcs), shifted, shape_out=fixture.shape, order="bilinear")
    assert np.nanmax(np.abs(ours[2:-2, 2:-2]/expected[2:-2, 2:-2]-1)) < 1e-4


def test_flags_remap():
    for bit, original in enumerate(flags.DISPLAY_BITS):
        source = np.array([1 << original], np.int64)
        assert flags.remap_flags(source)[0] == 1 << bit
        assert flags.restore_display_flags(flags.remap_flags(source))[0] == source[0]
    assert flags.remap_flags(np.array([0]), np.array([True]))[0] == 1 << 13
    for bit in (26, 27, 28, 29):
        assert flags.remap_flags(np.array([1 << bit]))[0] == 1 << 14
    assert flags.remap_flags(np.array([1 << 1]))[0] == 2


def test_pm_barnard():
    t = next(t for t in known.targets() if t["slug"] == "barnard")
    ra, dec = ephem.propagate(t["ra_j2000"], t["dec_j2000"], t["pmra_masyr"], t["pmdec_masyr"], 2000, 61041.0, t["plx_mas"])
    assert SkyCoord(ra, dec, unit="deg").separation(SkyCoord(*t["pos_2026_01_01"], unit="deg")).arcsec < 0.1


def test_wise0855_challenge_coords():
    import httpx

    from services.api.app.main import app

    async def check():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/v1/resolve", params={"q": "08h55m10.831s −07°14′42.53″"})
            assert response.status_code == 200
            result = response.json()
            assert result["epoch_warning"]
            assert SkyCoord(result["ra"], result["dec"], unit="deg").separation(SkyCoord(133.759765, -7.242182, unit="deg")).arcsec < 2
    asyncio.run(check())


def test_index_dedupe():
    import duckdb

    connection = duckdb.connect()
    path = str(ROOT / "data/spherex_exposures_d456_dr1_qr3.parquet")
    count, unique = connection.execute("SELECT count(*), count(DISTINCT (obs_id, det, coll)) FROM read_parquet(?)", [path]).fetchone()
    assert count == unique
    assert connection.execute("SELECT count(*) FROM read_parquet(?) WHERE ends_with(coll, '_cal')", [path]).fetchone()[0] == 0
    connection.close()


def test_gnomonic_wrap_and_margin():
    polygon = np.array([[[359.9, -0.1], [0.1, -0.1], [0.1, 0.1], [359.9, 0.1]]])
    assert polygon_contains(polygon, 0, 0)[0]
    assert not polygon_contains(polygon, 0.105, 0)[0]
    assert polygon_contains(polygon, 0.105, 0, margin_arcsec=18*6.15)[0]
    assert not polygon_contains(polygon, 180, 0)[0]


def test_visit_sampling_spans_time():
    fixture = [{"obs_id": str(v*100+i), "visit": v, "mjd": v*30+i/1000}
               for v in range(6) for i in range(100)]
    selected = sample_visits(fixture, 12)
    assert len(selected) == 12
    assert {r["visit"] for r in selected} == set(range(6))
    assert selected[-1]["mjd"]-selected[0]["mjd"] > 149


def test_visit_sampling_keeps_end_of_long_continuous_visit():
    fixture = [{"obs_id": str(i), "visit": i, "mjd": i*30, "lam_um": 4.1} for i in range(6)]
    fixture += [{"obs_id": f"long-{i}", "visit": 6, "mjd": 180+i, "lam_um": 4.1+(i % 10)/100} for i in range(100)]
    selected = sample_visits(fixture, 7)
    assert len(selected) == 7
    assert selected[0]["mjd"] == 0
    assert selected[-1]["mjd"] == 279
    assert {row["visit"] for row in selected} == set(range(7))


def test_horizons_matches_jd_instead_of_position():
    assert ephem.match_horizons_rows([3, 1, 2], [1, 2, 3]).tolist() == [2, 0, 1]
    with pytest.raises(ValueError, match="epoch mismatch"):
        ephem.match_horizons_rows([1.1], [1.0])


def test_ephemeris_interpolation_wraps_ra():
    ra, dec = ephem.interpolate_positions([60000, 60001], [359, 1], [0, 0], [60000.5])
    assert min(abs(ra[0]), abs(ra[0]-360)) < 0.001
    assert abs(dec[0]) < 1e-8
    with pytest.raises(ValueError, match="bracketing"):
        ephem.interpolate_positions([60000, 60001], [359, 1], [0, 0], [59999])


def test_omega_uses_header():
    assert calib.omega_from_header({"OMEGA_MEDIAN": 40}) == pytest.approx(40*(np.pi/(180*3600))**2)
    with pytest.raises(KeyError):
        calib.omega_from_header({})


def test_missing_catalog_values_remain_missing():
    assert known._nullable_number("") is None
    assert known._nullable_number(None) is None
    assert known._nullable_number("nan") is None
    assert known._nullable_number("0") == 0
    assert known._nullable_number("-0.1") == -0.1


def test_same_lambda_reference_removes_color():
    grid = {"nx": 5, "ny": 5, "crpix": [3, 3]}
    metadata, frames = [], []
    for i in range(12):
        lam = 4+0.002*i
        metadata.append({"mjd": 60000+10*i, "visit": i, "lam_um": lam, "bw_um": 0.03,
                         "lam_poly": [lam, 0, 0, 0, 0, 0]})
        frames.append({"flux": np.full((5, 5), 10+3*lam, dtype=np.float32), "flags": np.zeros((5, 5), np.uint16)})
    info, result = sky.difference_stack(metadata, frames, grid)
    assert info[5]["diff_available"]
    assert np.max(np.abs(result[5]["flux"])) < 1e-4
    info, result = sky.difference_stack(metadata[:2], frames[:2], grid)
    assert not any(i["diff_available"] for i in info)
    assert all(np.isnan(f["flux"]).all() for f in result)


@pytest.mark.network
def test_fits_layout_dr1():
    async def check():
        for det, rows in [(4, 441), (3, 451)]:
            key = s3.s3_key("2026W19_2A_1286_1", det)
            layout = await fitsio.read_hdu_layout(key)
            hdus = {h["name"]: h for h in layout}
            assert hdus["FLAGS"]["header"]["ZIMAGE"]
            assert hdus["FLAGS"]["header"]["ZCMPTYPE"] == "RICE_1"
            assert hdus["EPSF"]["header"]["NAXIS2"] == rows
            data = await fitsio.read_rows(key, layout, 1000, 1003, ("IMAGE", "FLAGS"))
            with fitsio.open_l2(s3.S3+key) as independent:
                for name in ("IMAGE", "FLAGS"):
                    np.testing.assert_equal(data[name], independent[name].section[1000:1003, :])
                assert hdus["IMAGE"]["dat_loc"] == independent["IMAGE"].fileinfo()["datLoc"]
    asyncio.run(check())


@pytest.mark.network
@pytest.mark.parametrize(("det", "tolerance"), [(4, 0.006), (5, 0.001), (6, 0.0025)])
def test_lam_poly(det, tolerance):
    async def check():
        key = s3.s3_key("2026W19_2A_1286_1", det)
        layout = await fitsio.read_hdu_layout(key)
        header = next(h["header"] for h in layout if h["name"] == "IMAGE")
        ra, dec = WCS(header).celestial.pixel_to_world_values(1020, 1020)
        exposure = {"obs_id": "2026W19_2A_1286_1", "det": det, "collection": "spherex_dr1", "visit": 0}
        grid, meta, frame = await cutout.make_frame(exposure, float(ra), float(dec))
        assert grid["nx"] == grid["ny"] == 147
        assert np.isfinite(frame["flux"]).any()
        assert meta["lam_poly_max_error_um"] < tolerance
    asyncio.run(check())
