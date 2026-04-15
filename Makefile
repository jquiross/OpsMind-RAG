.PHONY: dev up down logs api web test lint fmt

dev:
	docker compose up --build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

api:
	cd apps/api && .venv/bin/pytest tests/ -v || pytest tests/ -v

web-install:
	cd apps/web && npm ci

web-build:
	cd apps/web && npm run build

web-lint:
	cd apps/web && npm run lint

lint:
	cd apps/api && ruff check app tests
	cd apps/web && npm run lint

fmt:
	cd apps/api && ruff format app tests && black app tests
