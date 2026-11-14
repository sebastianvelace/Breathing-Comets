"""Gnomonic coverage queries and visit-stratified frame selection."""

from functools import lru_cache

import numpy as np
import pyarrow.parquet as pq
from scipy.spatial import cKDTree

from .config import INDEX_DIR


def unit_vectors(ra, dec):
    ra, dec = np.deg2rad(ra), np.deg2rad(dec)
    return np.stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)], axis=-1)


def polygon_contains(corners, ra, dec, margin_arcsec=0):
    r, d = np.deg2rad(corners[..., 0]), np.deg2rad(corners[..., 1])
    r0, d0 = np.deg2rad([ra, dec])
    dr = r-r0
    denominator = np.sin(d0)*np.sin(d)+np.cos(d0)*np.cos(d)*np.cos(dr)
    x = np.cos(d)*np.sin(dr)/denominator
    y = (np.cos(d0)*np.sin(d)-np.sin(d0)*np.cos(d)*np.cos(dr))/denominator
    ex, ey = np.roll(x, -1, axis=-1)-x, np.roll(y, -1, axis=-1)-y
    cross = ex*(-y)-ey*(-x)
    tolerance = np.deg2rad(margin_arcsec/3600)*np.hypot(ex, ey)
    return (((cross >= -tolerance).all(axis=-1) | (cross <= tolerance).all(axis=-1))
            & (denominator > 0).all(axis=-1))


class ExposureIndex:
    def __init__(self, path=None):
        self.table = pq.read_table(path or INDEX_DIR / "spherex_exposures_d456_dr1_qr3.parquet")
        self.corners = np.column_stack([self.table[f"c{i}"].to_numpy() for i in range(8)]).reshape(-1, 4, 2)
        centers = unit_vectors(self.corners[..., 0], self.corners[..., 1]).mean(axis=1)
        centers /= np.linalg.norm(centers, axis=1)[:, None]
        self.tree = cKDTree(centers)

    def query(self, ra, dec, det="all", t0=None, t1=None):
        candidate = np.array(self.tree.query_ball_point(unit_vectors(ra, dec), 2*np.sin(np.deg2rad(4)/2)), dtype=int)
        if not len(candidate):
            return []
        selected = self.table.take(candidate).to_pylist()
        detectors = list(range(1, 7)) if det == "all" else [int(det)]
        result = []
        for detector in detectors:
            if detector not in range(1, 7):
                raise ValueError("Detector must be between 1 and 6")
            pair = detector+3 if detector <= 3 else detector
            inside = polygon_contains(self.corners[candidate], ra, dec, 18*6.15 if detector <= 3 else 0)
            for row, covered in zip(selected, inside):
                if not covered or int(str(row["det"])[-1]) != pair:
                    continue
                mjd = float(row["t_min"])+56.79/86400
                if (t0 is not None and mjd < t0) or (t1 is not None and mjd > t1):
                    continue
                result.append({"obs_id": row["obs_id"], "det": detector,
                               "collection": row["coll"], "mjd": mjd})
        unique = {(r["obs_id"], r["det"], r["collection"]): r for r in result if not r["collection"].endswith("_cal")}
        rows = sorted(unique.values(), key=lambda r: (r["mjd"], r["det"]))
        times = sorted({r["mjd"] for r in rows})
        visits, visit = {}, 0
        previous = None
        for t in times:
            if previous is not None and t-previous > 2:
                visit += 1
            visits[t], previous = visit, t
        return [{**r, "visit": visits[r["mjd"]]} for r in rows]


@lru_cache(maxsize=1)
def get_index():
    return ExposureIndex()


def sample_visits(rows, max_frames):
    """Allocate frames across visits, then cover time or wavelength within each visit."""
    if max_frames < 1:
        raise ValueError("max_frames must be positive")
    ordered = sorted(rows, key=lambda r: (r["mjd"], r["obs_id"]))
    if len(ordered) <= max_frames:
        return ordered
    groups = {}
    for r in ordered:
        groups.setdefault(r["visit"], []).append(r)
    visits = list(groups)
    if len(visits) > max_frames:
        visits = [visits[i] for i in np.linspace(0, len(visits)-1, max_frames).round().astype(int)]
    quota = {v: 0 for v in visits}
    remaining = max_frames
    while remaining:
        for v in visits:
            if quota[v] < len(groups[v]) and remaining:
                quota[v] += 1
                remaining -= 1
        if all(quota[v] == len(groups[v]) for v in visits):
            break
    chosen = []
    for v in visits:
        group = sorted(groups[v], key=lambda r: r.get("lam_um", r["mjd"]))
        picks = np.linspace(0, len(group)-1, quota[v]).round().astype(int)
        chosen.extend(group[i] for i in picks)
    return sorted(chosen, key=lambda r: r["mjd"])
