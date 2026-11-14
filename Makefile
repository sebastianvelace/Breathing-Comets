.PHONY: dev api test check deploy-api

dev:
	cd apps/web && npm run dev

api:
	uv run granian --interface asgi --host 127.0.0.1 --port 8000 services.api.app.main:app

test:
	uv run pytest

check:
	cd apps/web && npm run check && npm run build

deploy-api:
	flyctl deploy . --config services/api/fly.toml --dockerfile "$(CURDIR)/services/api/Dockerfile" --remote-only --ha=false
