"""Paths shared by the scientific core and pipelines."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INDEX_DIR = Path(os.getenv("SPX_INDEX_DIR", ROOT / "data"))
CACHE_DIR = Path(os.getenv("SPX_DATA_DIR", ROOT / "data/cache"))
STATIC_DIR = ROOT / "apps/web/static/data"
