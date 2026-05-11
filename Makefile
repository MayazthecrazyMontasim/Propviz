.PHONY: dev build up down logs worker frontend migrate seed

# ── Local dev (no Docker) ────────────────────────────────────────────────────
dev:
	cd backend && uvicorn app.main:app --reload --port 8000

worker:
	cd backend && celery -A app.workers.celery_app:celery worker \
		--loglevel=info \
		--queues=ingest,parse,reconstruct,synthesize,postprocess

frontend:
	cd frontend && npm run dev

# ── Docker ───────────────────────────────────────────────────────────────────
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

# ── Database ─────────────────────────────────────────────────────────────────
migrate:
	cd backend && alembic upgrade head

migrate-new:
	cd backend && alembic revision --autogenerate -m "$(msg)"

# ── Setup ─────────────────────────────────────────────────────────────────────
install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

install: install-backend install-frontend

env:
	cp .env.example .env
	@echo "Created .env — fill in your API keys."
