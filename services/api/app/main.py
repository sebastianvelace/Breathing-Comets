"""Public API for SPHEREx sky exploration."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.requests import Request

app = FastAPI(title="Breathing Comets API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "SPX_ALLOWED_ORIGINS",
        "https://breathingcomets.org,https://www.breathingcomets.org,http://localhost:5173",
    ).split(","),
    allow_origin_regex=r"https://[a-zA-Z0-9-]+\.pages\.dev",
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
    expose_headers=["X-SPX-Data-Version", "Retry-After"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def data_version(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-SPX-Data-Version"] = "dr1+qr3;l2b-v27"
    return response


@app.get("/v1/health")
async def health():
    """Report service availability separately from scientific data readiness."""
    index = Path(__file__).resolve().parents[3] / "data/spherex_exposures_d456_dr1_qr3.parquet"
    rows = 0
    if index.is_file():
        from pyarrow.parquet import ParquetFile

        rows = ParquetFile(index).metadata.num_rows
    return {
        "ok": True,
        "index_rows": rows,
        "index_built": index.is_file(),
        "collections": ["dr1", "qr3"] if index.is_file() else [],
        "swcs": None,
    }
