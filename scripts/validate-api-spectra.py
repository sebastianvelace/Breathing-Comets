"""Request three observed stellar spectra and retain every success and rejection."""

import argparse
import asyncio
import csv
import json
import time
from pathlib import Path

import httpx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def compare(star, records, bands):
    points = [p for p in records if "flux_mjy" in p]
    result = {"designation": star["designation"], "points": len(points),
              "rejected": sum("error" in p for p in records), "bands": {}}
    for name in ("Ks", "W2"):
        band = bands[name]
        values = [p["flux_mjy"] for p in points if band["lo_um"] <= p["lam_um"] <= band["hi_um"] and not p["sat"]]
        flux = float(np.median(values)) if values else None
        catalog = band["zero_jy"]*1000*10**(-.4*float(star[band["magnitude_column"]]))
        result["bands"][name] = {"n": len(values), "median_mjy": flux, "catalog_mjy": catalog,
                                  "ratio": flux/catalog if flux is not None else None}
    return result


async def run(base, replay):
    folder = ROOT / "data/validation"
    bands = json.loads((folder / "photometric_bands.json").read_text())["bands"]
    stars = list(csv.DictReader((folder / "stars.csv").open()))
    summaries = []
    async with httpx.AsyncClient(timeout=300) as client:
        for star in stars:
            destination = folder / (star["designation"]+".json")
            start = time.monotonic()
            if replay:
                records = json.loads(destination.read_text())["records"]
            else:
                records = []
                async with client.stream("GET", base+"/v1/spectrum", params={"ra": star["ra_2025.9"], "dec": star["dec_2025.9"]}) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            records.append(json.loads(line))
            summary = compare(star, records, bands)
            summary["seconds"] = time.monotonic()-start if not replay else None
            summary["api"] = base
            if not replay:
                destination.write_text(json.dumps({"star": star, "summary": summary, "records": records}, allow_nan=False))
            summaries.append(summary)
            print(json.dumps(summary), flush=True)
    passed = all(s["points"] >= 50 and all(b["ratio"] is not None and .95 <= b["ratio"] <= 1.05 for b in s["bands"].values()) for s in summaries)
    (folder / "summary.json").write_text(json.dumps({"passed": passed, "replayed": replay, "comparisons": summaries}, indent=2, allow_nan=False)+"\n")
    if not passed:
        raise SystemExit("Stellar spectrum acceptance failed; retained all observed results")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="https://api.breathingcomets.org")
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    asyncio.run(run(args.base.rstrip("/"), args.replay))
