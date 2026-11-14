FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1
ENV PYTHONPATH=/app/packages/spxcore
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY packages/spxcore ./packages/spxcore
COPY services/api ./services/api
COPY data/spherex_exposures_d456_dr1_qr3.parquet data/spherex_s3_keys_compact.npz ./data/
COPY apps/web/static/data ./apps/web/static/data
EXPOSE 8000
CMD ["uv","run","--frozen","--no-dev","granian","--interface","asgi","--host","0.0.0.0","--port","8000","--workers","1","services.api.app.main:app"]
