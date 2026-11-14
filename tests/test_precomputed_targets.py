"""Acceptance checks against actual precomputed mission images, never synthetic sky."""

import gzip
import json
import struct
import subprocess

import numpy as np
import pytest
from astropy.wcs import WCS
from spxcore import ephem, known
from spxcore.config import ROOT, STATIC_DIR

TARGETS = [t["slug"] for t in known.targets()]


def _reject_constant(value):
    raise ValueError(f"Invalid JSON constant: {value}")


def read_stack(path):
    raw = gzip.decompress(path.read_bytes())
    magic, version, bitflags, length, reserved = struct.unpack_from("<4sHHII", raw)
    assert (magic, version, reserved) == (b"SPXF", 1, 0)
    assert length % 8 == 0
    header = json.loads(raw[16:16+length], parse_constant=_reject_constant)
    nx, ny = header["grid"]["nx"], header["grid"]["ny"]
    pixels, offset = nx*ny, 16+length

    def plane():
        nonlocal offset
        data = np.frombuffer(raw[offset:offset+pixels*4], np.uint8)
        offset += (pixels*4+7)//8*8
        if bitflags & 1:
            data = data.reshape(4, pixels).T.copy().ravel()
        return data.view("<f4").reshape(ny, nx)

    frames = []
    for _ in header["frames"]:
        image = plane()
        if header.get("has_var"):
            plane()
        flags = np.frombuffer(raw[offset:offset+pixels*2], "<u2").reshape(ny, nx)
        offset += (pixels*2+7)//8*8
        frames.append((image, flags))
    assert offset == len(raw)
    return header, frames


@pytest.mark.parametrize("slug", TARGETS)
def test_target_has_all_detectors_and_fits_budget(slug):
    folder = STATIC_DIR / "targets" / slug
    manifest = json.loads((folder / "manifest.json").read_text())
    assert set(manifest["stacks"]) == {str(i) for i in range(1, 7)}
    assert not manifest["unavailable_detectors"]
    assert sum(p.stat().st_size for p in folder.iterdir() if p.is_file()) <= 25_000_000
    for detector, filename in manifest["stacks"].items():
        path = folder / filename
        assert path.stat().st_size <= 6_000_000
        header, frames = read_stack(path)
        assert header["grid"]["north_up"]
        assert header["grid"]["nx"] == header["grid"]["ny"] == 147
        assert len(header["frames"]) == len(frames)
        assert all(np.isfinite(frame[0]).any() for frame in frames)
        assert all(np.isfinite(meta["lam_um"]) and meta["bw_um"] > 0 for meta in header["frames"])
        assert int(detector) == header["det"]
    default = str(manifest["default_det"])
    header, frames = read_stack(folder / manifest["stacks"][default])
    assert len(frames) >= 10
    diff_header, diff = read_stack(folder / manifest["diff"][default])
    assert len(diff) == len(frames)
    assert any(meta["diff_available"] for meta in diff_header["frames"])
    assert all(np.isfinite(frame[0]).any() for meta, frame in zip(diff_header["frames"], diff) if meta["diff_available"])
    assert manifest["caveat"] == json.loads((STATIC_DIR / "targets" / f"{slug}.json").read_text())["caveat"]
    gaia = json.loads((folder / "gaia.json").read_text())
    assert isinstance(gaia, list) and gaia
    assert manifest["gaia_schema"] == 2


def test_barnard_gaia_moves_between_real_epochs():
    folder = STATIC_DIR / "targets/barnard"
    manifest = json.loads((folder / "manifest.json").read_text())
    header, _ = read_stack(folder / manifest["stacks"]["4"])
    star = next(s for s in json.loads((folder / "gaia.json").read_text()) if s["source_id"] == manifest["gaia_target_id"])
    grid = header["grid"]
    wcs = WCS(naxis=2)
    wcs.wcs.ctype, wcs.wcs.crval = grid["ctype"], grid["crval"]
    wcs.wcs.crpix, wcs.wcs.cdelt = grid["crpix"], grid["cdelt_deg"]
    points = []
    for frame in (header["frames"][0], header["frames"][-1]):
        ra, dec = ephem.propagate(star["ra"], star["dec"], star["pmra"], star["pmdec"], star["ref_epoch"], frame["mjd"], star["parallax"])
        points.append(np.array(wcs.world_to_pixel_values(ra, dec)))
    assert 1 < np.linalg.norm(points[1]-points[0]) < 3


def test_wise0855_grid_uses_propagated_reference_position():
    folder = STATIC_DIR / "targets/wise-0855"
    header, _ = read_stack(folder / "D6.spxf.gz")
    target = next(t for t in known.targets() if t["slug"] == "wise-0855")
    assert header["grid"]["crval"] == target["pos_2026_01_01"]


def test_r_dra_samples_full_baseline():
    header, _ = read_stack(STATIC_DIR / "targets/r-dra/D6.spxf.gz")
    assert header["frames"][0]["date"][:10] <= "2025-04-30"
    assert header["frames"][-1]["date"][:10] >= "2026-09-01"
    assert len(header["visits"]) > 2


def test_all_actual_stacks_parse_in_typescript():
    script = """
      import {readFileSync,readdirSync} from 'node:fs';
      import {gunzipSync} from 'node:zlib';
      import {parseSpxf} from './apps/web/src/lib/data/spxf.ts';
      let count=0;
      const root='apps/web/static/data/targets';
      for(const item of readdirSync(root,{withFileTypes:true})) {
        if(!item.isDirectory()) continue;
        for(const name of readdirSync(`${root}/${item.name}`)) {
          if(!name.endsWith('.spxf.gz')) continue;
          const b=gunzipSync(readFileSync(`${root}/${item.name}/${name}`));
          const p=parseSpxf(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));
          if(p.frames.length<10 || p.header.grid.nx!==147) throw Error('Invalid target stack');
          if(p.header.kind==='stack' && !p.frames.every(f=>f.flux.some(Number.isFinite))) throw Error('No real pixels');
          count++;
        }
      }
      if(count!==35) throw Error(`Expected 35 stacks, received ${count}`);
    """
    subprocess.run(["node", "--input-type=module", "-e", script], cwd=ROOT, check=True, capture_output=True)
