"""Join retained CV ratios to published NEOWISE V2 catalog diameters.

No thermal fit or SPHEREx photometry is executed. The reference aggregation is
the same per-designation median used by the validation's catalog preparation.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
from astropy.table import Table

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/validation/neowise_neos.tbl"
DESTINATION = ROOT / "apps/web/static/data/neo/validation_diameters.json"
CATALOG_URL = "https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query"
QUERY = {"catalog": "neowisesbpropv2", "spatial": "None", "outfmt": 1,
         "selcols": "asteroid_number,prov_desig,diameter", "constraints": "type='neos'", "outrows": 10000}


def main():
    table = Table.read(RAW, format="ascii.ipac")
    grouped = {}
    for row in table:
        key = (str(row["prov_desig"]).strip() if np.ma.is_masked(row["asteroid_number"])
               else str(int(row["asteroid_number"])))
        if not np.ma.is_masked(row["diameter"]):
            grouped.setdefault(key, []).append(float(row["diameter"]))
    cv = json.loads((DESTINATION.parent / "validation.json").read_text())["cv"]
    missing = [r["key"] for r in cv if r["key"] not in grouped]
    if missing:
        raise ValueError(f"Catalog reference diameters missing: {missing}")
    points = []
    for row in cv:
        diameter = float(np.median(grouped[row["key"]]))
        points.append({"key": row["key"], "neowise_km": diameter,
                       "spherex_km": diameter*row["D_ratio"], "ratio": row["D_ratio"],
                       "reference_rows": len(grouped[row["key"]])})
    packet = {"source": "https://irsa.ipac.caltech.edu/data/WISE/NEOWISE_SB/gator_docs/neowisesbprop_colDescriptions.html",
              "catalog": QUERY["catalog"], "query_url": CATALOG_URL, "query": QUERY,
              "reference_source": "NEOWISE V2, median of published diameter entries per designation",
              "retained_source": str(RAW.relative_to(ROOT)), "sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
              "display_method": "D_SPHEREx = exported CV D_ratio × catalog D_NEOWISE; ratios retain export rounding; no thermal model is refitted",
              "cv_n": len(cv), "points": points}
    DESTINATION.write_text(json.dumps(packet, separators=(",", ":"), allow_nan=False) + "\n")
    print(f"Wrote {len(points)}/{len(cv)} NEOWISE diameter pairs")


if __name__ == "__main__":
    main()
