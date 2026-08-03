# Docker Deployment Workflow

This describes how the Wildlife Population Intelligence System moves from a
laptop to a running production stack, entirely via Docker. It covers three
environments and the pipeline that connects them.

```
 ┌────────────┐     git push      ┌────────────────────┐     image push     ┌──────────────┐
 │  Local dev  │ ───────────────► │  CI (GitHub Actions) │ ─────────────────► │  Registry      │
 │  docker      │                  │  build, test, lint,  │                     │  (GHCR/ECR/ACR)│
 │  compose up  │                  │  build & tag images  │                     └──────┬────────┘
 └────────────┘                  └────────────────────┘                            │
                                                                                      │ pull + up -d
                                                                                      ▼
                                                                            ┌────────────────────┐
                                                                            │  Production host     │
                                                                            │  docker compose       │
                                                                            │  -f docker-compose.   │
                                                                            │  prod.yml             │
                                                                            └────────────────────┘
```

## 1. Environments

| Environment | Compose file                              | Purpose                                   |
|-------------|--------------------------------------------|---------------------------------------------|
| Local dev    | `docker-compose.yml`                       | Hot-reload, bind-mounted source, single host |
| Production   | `docker-compose.prod.yml`                  | Immutable pre-built images, no source mounts, healthchecks, restart policies |

Both share the same `database/schema.sql` and app code — only how the
images are built and run differs.

## 2. Image build strategy

- **Backend**: multi-stage `backend/Dockerfile.prod` — installs
  dependencies in a builder stage, copies only the venv + app code into a
  slim runtime stage, runs as a non-root user, serves with
  `uvicorn`/`gunicorn` workers (no `--reload`).
- **Frontend**: multi-stage `frontend/Dockerfile.prod` — `npm run build`
  produces static assets in a Node builder stage, then an `nginx:alpine`
  stage serves the compiled bundle and proxies `/api` to the backend
  container. No Node runtime ships in the final image.
- **Database**: the official `postgis/postgis` image is used as-is; schema
  is applied via an init script the first time the volume is created, and
  via Alembic migrations thereafter (see §5).

Images are tagged with both `:latest` and the Git SHA
(`ghcr.io/<org>/wpi-backend:<sha>`), so a bad deploy can be rolled back by
redeploying the previous tag.

## 3. Local development workflow

```bash
cp backend/.env.example backend/.env
docker compose up --build          # builds from source, hot-reloads on save
docker compose exec backend python -m app.core.seed
```

Iterate; `docker compose logs -f backend` / `frontend` to watch output.

## 4. CI workflow (`.github/workflows/deploy.yml`)

On every push to `main`:

1. **Lint & test** — spin up a throwaway Postgres/PostGIS service
   container, install backend deps, run `pytest` (add tests as they're
   written) and a basic import/syntax check; run `npm ci && npm run build`
   for the frontend to catch build breaks early.
2. **Build & push images** — `docker buildx build` for `backend/Dockerfile.prod`
   and `frontend/Dockerfile.prod`, tag with the commit SHA and `latest`,
   push to the configured container registry (GHCR by default — swap for
   ECR/ACR by changing the `registry` step).
3. **Deploy** (optional, gated on a manual approval environment) — SSH into
   the target host and run `scripts/deploy.sh`, which pulls the new images
   and does a rolling `docker compose up -d`.

## 5. Database migrations in production

Milestone 1 ships schema as a single `schema.sql` for simplicity. For
production rollouts once the schema starts changing after initial
release, wire in Alembic:

```bash
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

Run this as its own CI/CD step **before** swapping traffic to the new
backend image, so schema changes land before new code that depends on
them.

## 6. Production deploy steps (on the host)

```bash
# one-time host setup
git clone <repo> && cd wildlife-intelligence-system
cp backend/.env.example backend/.env.prod   # fill in real secrets
cp frontend/.env.example frontend/.env.prod

# every deploy
./scripts/deploy.sh <image_tag>
```

`scripts/deploy.sh`:
1. Pulls `wpi-backend:<tag>` and `wpi-frontend:<tag>` from the registry.
2. Runs pending Alembic migrations against the production DB.
3. `docker compose -f docker-compose.prod.yml up -d` — Docker replaces
   containers whose image changed and leaves the DB container untouched.
4. Runs `GET /health` against the new backend container; if it doesn't
   return 200 within a timeout, the script exits non-zero (CI treats this
   as a failed deploy and stops before removing the old containers).
5. Prunes dangling images to keep disk usage bounded.

## 7. Secrets & configuration

- Local dev: plain `.env` files (already gitignored).
- Production: `backend/.env.prod` / `frontend/.env.prod` on the host,
  loaded via `env_file` in `docker-compose.prod.yml` — **never committed**.
  For a managed platform (AWS/Azure/GCP), swap these for the platform's
  secrets manager (Secrets Manager, Key Vault, Secret Manager) and inject
  as environment variables at container start instead of files on disk.
- `SECRET_KEY` (JWT signing) and the Postgres password must be rotated
  from the example values before any non-local deployment.

## 8. Networking & TLS

`docker-compose.prod.yml` exposes only the frontend's nginx container on
`80`/`443` to the host; the backend and database are reachable only on the
internal Docker network (`wpi_internal`), not published to the host. Put a
reverse proxy or managed load balancer (Caddy, Traefik, or a cloud LB) in
front of the frontend container for TLS termination — a `Caddyfile`
example is included in `scripts/Caddyfile.example`.

## 9. Rollback

Because images are tagged by Git SHA, rollback is:

```bash
./scripts/deploy.sh <previous_sha>
```

No rebuild required — the previous image is pulled from the registry and
the containers are swapped back.

## 10. Health & observability

- `GET /health` on the backend is used both by the deploy script and by
  Docker's own `HEALTHCHECK` directive in `backend/Dockerfile.prod`, so
  `docker compose ps` reports `unhealthy` if the app can't serve requests
  (misconfigured DB URL, migration not applied, etc.).
- `docker compose logs -f` (or ship logs to your platform's log
  aggregator) is sufficient for Milestone 1; a dedicated
  monitoring/logging stack is a later-milestone concern per the original
  architecture diagram (Prometheus/Grafana, ELK).
