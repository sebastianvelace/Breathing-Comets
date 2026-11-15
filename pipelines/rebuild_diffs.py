"""Rebuild the prepared Diff λ packages from the published epoch stacks.

Uses only files already in apps/web/static/data/targets: no network access.
The epoch stacks are not modified; their flags keep the resampling used when
they were precomputed (see docs/FINDINGS.md, scientific audit 2026-11-15).
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from spxcore import sky, spxf

TARGETS = Path(__file__).resolve().parents[1]/"apps/web/static/data/targets"


def rebuild(directory, check_only=False):
    manifest = json.loads((directory/"manifest.json").read_text())
    report = []
    for detector, diff_file in manifest.get("diff", {}).items():
        header, frames = spxf.read_spxf(directory/manifest["stacks"][detector])
        old_header, old_frames = spxf.read_spxf(directory/diff_file)
        info, result = sky.difference_stack(header["frames"], frames, header["grid"])
        finite = np.concatenate([f["flux"][np.isfinite(f["flux"])] for f in result])
        changed = sum(int(np.sum(~np.isclose(o["flux"], n["flux"], atol=1e-5, equal_nan=True)))
                      for o, n in zip(old_frames, result))
        report.append({"target": manifest["slug"], "detector": detector, "frames": len(result),
                       "available": sum(m["diff_available"] for m in info), "changed_pixels": changed,
                       "median_fallback_pixels": int(sum(np.count_nonzero(f["flags"] & (1 << 15)) for f in result))})
        if check_only:
            continue
        low, high = np.percentile(finite, [0.5, 99.5]) if len(finite) else (0., 0.)
        new_header = {**old_header,
                      "frames": [{**m, "k": i} for i, m in enumerate(info)],
                      "stretch_hint": {**old_header["stretch_hint"], "lo": float(low), "hi": float(high)},
                      "provenance": {**old_header.get("provenance", {}),
                                     "rebuilt": datetime.now(UTC).isoformat(),
                                     "rebuild": "pipelines/rebuild_diffs.py: hard-masked references, median-fallback flag"}}
        spxf.write_spxf(directory/diff_file, new_header, result)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    for directory in sorted(p for p in TARGETS.iterdir() if (p/"manifest.json").exists()):
        for row in rebuild(directory, args.check_only):
            print(json.dumps(row))


if __name__ == "__main__":
    main()
