"""Write the minimal channel table used by the landing ribbon.

``apps/web/static/data/channels.json`` carries 9 fields per channel; the ribbon needs
``frame``, ``wavelength_um`` and ``R``. Keeping them as ``[frame, lam, R]`` rows trims the
initial landing JS. Source of truth stays ``channels.json``; this file is derived.

Usage: ``python pipelines/channels_lite.py``
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "apps/web/static/data/channels.json"
OUT = ROOT / "apps/web/src/lib/data/channels-lite.json"


def main():
    channels = json.loads(SRC.read_text())["channels"]
    rows = [[c["frame"], round(c["wavelength_um"], 3), round(c["R"])] for c in channels]
    OUT.write_text(json.dumps({"source": "static/data/channels.json", "columns": ["frame", "wavelength_um", "R"], "rows": rows},
                              separators=(",", ":")))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} channels")


if __name__ == "__main__":
    main()
