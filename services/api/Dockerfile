FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY packages/spxcore ./packages/spxcore
COPY services/api ./services/api
EXPOSE 8000
CMD ["uv","run","--frozen","--no-dev","granian","--interface","asgi","--host","0.0.0.0","--port","8000","--workers","1","services.api.app.main:app"]
