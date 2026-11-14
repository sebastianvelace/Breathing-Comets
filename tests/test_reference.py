"""Pruebas de regresión de la investigación (referencia para portar a `spxcore`).

Fijan lo verificado el 12–13 nov 2026 para que el código del producto no repita los errores 35–48 de BUILD.md §17.
  pytest tests/                      # rápidas, sin red
  pytest tests/ -m network           # además lee archivos reales del bucket público (≈ 1 min)
"""
import json, sys
from pathlib import Path
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
from spxcore import s3, psf as SP, fitsio


# ---------------- claves S3 (error 35/36) ----------------
def test_canonical_key_prefers_dr1():
    u = s3.s3_url("spherex_qr2", "2026W19_2A_1286_1", "D4")
    assert u.endswith("dr1/level2/2026W19_2A/l2b-v27-2026-245/4/level2_2026W19_2A_1286_1D4_spx_l2b-v27-2026-245.fits")


def test_canonical_key_qr3_and_retry_dirs():
    u = s3.s3_url("x", "2026W31_2A_0016_1", "D5")
    assert "/qr3/level2/2026W31_2A/" in u and u.endswith("level2_2026W31_2A_0016_1D5_spx_l2b-v27-2026-224.fits")


def test_key_index_is_compact():
    ids, code, dirs = s3._load_keys()
    assert ids.dtype.kind == "S" and len(ids) == 1_630_148 and code.dtype == np.int16 and np.all(ids[:-1] <= ids[1:])


# ---------------- banderas (Expl. Supplement v2.1, tabla 16; error 37/§8.0b) ----------------
def test_photometry_mask_is_official():
    bits = {b for b in range(32) if SP.HARD >> b & 1}
    assert bits == {2, 6, 7, 9, 10, 11, 15, 17, 26, 27, 28, 29}
    assert not SP.HARD & (1 << 1)          # OVERFLOW no se enmascara en fotometría
    assert not SP.HARD & (1 << 19)         # OUTLIER marca lo que se mueve: nunca enmascarar
    assert not SP.HARD & (1 << 21)         # SOURCE


# ---------------- ePSF (errores 44/45) ----------------
def _gauss_epsf(osamp=5, n=33, fwhm_px=1.6):
    s = fwhm_px * osamp / 2.355; y, x = np.indices((n, n)) - (n - 1) / 2
    p = np.exp(-0.5 * (x ** 2 + y ** 2) / s ** 2); return (p / p.sum()).astype(np.float32)


def _cut(x=12.3, y=11.7, A=100.0, bg=5.0, noise=0.5, seed=0):
    psf = _gauss_epsf(); c = dict(img=np.zeros((25, 25)), flg=np.zeros((25, 25), np.int64), var=np.full((25, 25), noise ** 2), psf=psf, osamp=5, x=x, y=y)
    M = SP.psf_model(c, mode="sample")
    c["img"] = A * M + bg + np.random.default_rng(seed).normal(0, noise, (25, 25)); return c, M


def test_psf_model_sampled_is_normalized():
    _, M = _cut()
    assert abs(M.sum() - 1) < 0.01


def test_sampled_is_sharper_than_integrated():
    c, Ms = _cut(); Mi = SP.psf_model(c, mode="integrate")
    assert Ms.max() > Mi.max() * 1.05      # integrar convoluciona otra vez con el píxel


def test_psf_photometry_recovers_amplitude_without_apcor():
    c, _ = _cut(A=100.0)
    f, e, _ = SP.psf_photometry(c, R=4.0)
    A_fit = f / (SP.OMEGA_PIX * 1e9)
    assert abs(A_fit / 100.0 - 1) < 0.02
    assert SP.apcor(5) == 1.0 and SP.APPLY_APCOR is False   # la calibración de SPHEREx es por ePSF (§8.0c)


def test_psf_photometry_trailed_model_conserves_flux():
    c, _ = _cut(); c.update(xs=10.0, ys=11.7, xe=14.6, ye=11.7)
    assert abs(SP.psf_model(c, nsteps=15).sum() - 1) < 0.02


# ---------------- paquete estático (§6.10) ----------------
def test_export_package():
    d = json.load(open(ROOT / "apps/web/static/data/neo/index.json"))
    assert d["counts"]["A"] + d["counts"]["B"] == 28 and d["counts"]["candidates"] == 86
    for o in d["objects"]:
        pts = json.load(open(ROOT / f"apps/web/static/data/neo/{o['slug']}.json"))["points"]
        assert len(pts) >= (8 if o["tier"] in ("A", "B") else 2)
        assert o["D16"] <= o["D_km"] <= o["D84"]
    w = json.load(open(ROOT / "apps/web/static/data/targets/wise-0855.json"))["spectrum"]
    assert all(s["f"] < 0.1 for s in w if s["lam"] < 3.0) and all(s["f"] > 0.3 for s in w if 4.2 <= s["lam"] <= 4.7)
    cal = {v["band"]: v["ratio"] for v in json.load(open(ROOT / "apps/web/static/data/calibration.json"))["validation"]}
    assert all(0.9 < r < 1.05 for r in cal.values())


def test_channels_match_dr1_cube_labels():
    ch = json.load(open(ROOT / "apps/web/static/data/channels.json"))["channels"]
    assert len(ch) == 102 and abs(ch[85]["wavelength_um"] - 4.435) < 0.002   # = data_cube_crval3_arr[85] del HiPS DR1


# ---------------- con red: archivos reales ----------------
@pytest.mark.network
def test_epsf_row_read_equals_full_table():
    from astropy.io import fits
    url = s3.s3_url("x", "2026W31_2A_0016_1", "D5")
    with fitsio.open_l2(url) as h:
        hd = h["IMAGE"].header
        from astropy.wcs import WCS
        ra, dec = WCS(hd).celestial.pixel_to_world_values(1000.0, 700.0)
        tab = h["EPSF"].data
    c = SP.cutout_psf("x", "2026W31_2A_0016_1", "D5", float(ra), float(dec))
    z = int(np.argmin(np.hypot(tab["XCENTER"] - c["x_full"], tab["YCENTER"] - c["y_full"])))
    assert c["zone"] == z and np.abs(tab["EPSF"][z] - c["psf"]).max() < 1e-6


def test_epsf_row_grid_depends_on_detector():
    # D1, D2, D4, D5, D6: 441 filas = 21 x 21. D3: 451 filas = 11 (x) x 41 (y). x-rápido. (AUDIT H1)
    assert SP.epsf_row(441, 1000.0, 700.0) == 7 * 21 + 10
    assert SP.epsf_row(451, 1900.0, 1900.0) == 38 * 11 + 10
    assert SP.epsf_row(451, 0.0, 0.0) == 0 and SP.epsf_row(451, 2039.9, 2039.9) == 450 and SP.epsf_row(441, 2039.9, 2039.9) == 440
    with pytest.raises(ValueError):
        SP.epsf_row(400, 10, 10)


@pytest.mark.network
def test_epsf_row_detector3_uses_11x41_grid():
    from astropy.io import fits
    from astropy.wcs import WCS
    url = s3.s3_url("x", "2026W19_2A_1286_1", "D3")
    with fitsio.open_l2(url) as h:
        ra, dec = WCS(h["IMAGE"].header).celestial.pixel_to_world_values(1900.0, 1900.0)
        tab = h["EPSF"].data
    assert len(tab) == 451
    c = SP.cutout_psf("x", "2026W19_2A_1286_1", "D3", float(ra), float(dec))
    z = int(np.argmin(np.hypot(tab["XCENTER"] - c["x_full"], tab["YCENTER"] - c["y_full"])))
    assert c["zone"] == z and np.abs(tab["EPSF"][z] - c["psf"]).max() < 1e-6


def _qr2_key(obs, det):
    """Clave v20 de QR2 listando el bucket (no depende de índices sin versionar)."""
    import re, requests
    week = obs.rsplit("_", 2)[0]; tok, pat = None, f"level2_{obs}D{det}_spx_"
    while True:
        prm = {"list-type": "2", "prefix": f"qr2/level2/{week}/", "max-keys": "1000"}
        if tok: prm["continuation-token"] = tok
        t = requests.get(s3.S3, params=prm, timeout=60).text
        hit = [k for k in re.findall(r"<Key>([^<]+)</Key>", t) if pat in k]
        if hit: return sorted(hit)[-1]
        m = re.search(r"<NextContinuationToken>([^<]+)</NextContinuationToken>", t)
        if not m: return None
        tok = m.group(1)


@pytest.mark.network
def test_dr1_wavelength_shift_d5():
    from astropy.io import fits
    from astropy.wcs import WCS
    obs = "2025W21_1B_0112_1"; k20 = _qr2_key(obs, 5)
    if k20 is None:
        pytest.skip("la exposición ya no está en qr2/")
    lam = []
    for url in (s3.S3 + k20, s3.s3_url("x", obs, "D5")):
        with fitsio.open_l2(url) as h:
            lam.append(WCS(h["IMAGE"].header, key="W", fobj=h).pixel_to_world_values(1020, 1020)[0])
    assert 5.5 < (lam[1] - lam[0]) * 1000 < 7.0   # D5: +6.3 nm (§8.0b)
