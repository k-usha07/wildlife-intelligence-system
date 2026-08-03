# Wildlife Population Intelligence System — Milestone 1

**Milestone 1: Project Initialization, Design Process & Core Setup (Week 1 & 2)**

This repository contains the deliverables for Milestone 1 of the AI-powered Wildlife
Population Intelligence System:

1. Project objectives and biodiversity monitoring workflows — [`docs/architecture.md`](docs/architecture.md)
2. System architecture and database schema — [`docs/architecture.md`](docs/architecture.md), [`database/schema.sql`](database/schema.sql)
3. UI wireframes and workflow planning — [`docs/wireframes.md`](docs/wireframes.md)
4. Frontend and backend environment setup — [`backend/`](backend/), [`frontend/`](frontend/)
5. Authentication and role-based access control — [`backend/app/auth/`](backend/app/auth/)
6. Wildlife monitoring workflows (surveys, monitoring sites, camera traps, audio sensors) —
   [`backend/app/routers/`](backend/app/routers/)
7. Wildlife image/audio dataset integration — [`backend/app/datasets/`](backend/app/datasets/)

## Repository layout

```
wildlife-intelligence-system/
├── docs/
│   ├── architecture.md          # system architecture, objectives, workflows
│   └── wireframes.md            # low-fi wireframes for each role dashboard
├── database/
│   └── schema.sql                # PostgreSQL + PostGIS schema
├── backend/                      # FastAPI service
│   ├── app/
│   │   ├── main.py
│   │   ├── core/                 # config, security, database session
│   │   ├── models/                # SQLAlchemy models
│   │   ├── schemas/               # Pydantic schemas
│   │   ├── auth/                  # JWT + RBAC
│   │   ├── routers/               # API endpoints
│   │   └── datasets/              # dataset download/ingestion scripts
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/                     # React (Vite) app
│   ├── src/
│   │   ├── pages/                 # Login, Register, role dashboards
│   │   ├── dashboards/
│   │   ├── context/AuthContext.jsx
│   │   ├── api/client.js
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml            # Postgres + PostGIS, backend, frontend
```

## Quick start (local, Docker)

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

- Backend API: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:5173
- PostgreSQL/PostGIS: localhost:5432 (db `wildlife_db`)

Seed roles + a demo admin user:

```bash
docker compose exec backend python -m app.core.seed
```

## Production deployment

See [`docs/deployment.md`](docs/deployment.md) for the full workflow
(CI build → registry push → host rollout with health checks and rollback).
Quick summary:

```bash
# CI builds and pushes ghcr.io/<org>/wpi-backend:<sha> and wpi-frontend:<sha>
# On the production host:
cp backend/.env.prod.example backend/.env.prod   # fill in real secrets
IMAGE_TAG=<sha> ./scripts/deploy.sh <sha>
```

Production-specific files:
- `backend/Dockerfile.prod`, `frontend/Dockerfile.prod` — multi-stage, non-root, healthchecked images
- `frontend/nginx.conf` — serves the compiled SPA and proxies `/api` to the backend
- `docker-compose.prod.yml` — immutable images, internal-only backend/db network, restart policies
- `scripts/deploy.sh` — pull → migrate → roll out → health-check → prune
- `.github/workflows/deploy.yml` — CI: test → build & push images → (approved) deploy over SSH

## Quick start (manual, no Docker)

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL if not using Docker Postgres
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

**Database** (if not using Docker): install PostgreSQL 15+ with the PostGIS extension,
create a database `wildlife_db`, then run:
```bash
psql -d wildlife_db -f database/schema.sql
```

## Milestone 1 exit criteria (from project brief)

- [x] Project initialization completed
- [x] Authentication implemented (JWT + OAuth2 password flow + role-based access)
- [x] Wildlife monitoring workflows operational (surveys, monitoring sites, camera
      traps, audio sensors, observation logging)
- [x] Wildlife datasets integrated (download/prep scripts for Snapshot Serengeti,
      iNaturalist, BirdCLEF, Animal Kingdom, GBIF)

## Next milestones (not in scope here)

- Milestone 2: Species recognition + bioacoustic recognition + biodiversity analytics
- Milestone 3: Population estimation + habitat intelligence + conservation recommendations
- Milestone 4: Dashboards, reports/GIS, testing, deployment
