#!/usr/bin/env bash
# Pull a given image tag and roll it out via docker compose, with a
# post-deploy health check. Intended to run on the production host (or
# from CI over SSH).
#
# Usage: ./scripts/deploy.sh <image_tag>
set -euo pipefail

TAG="${1:?Usage: $0 <image_tag>}"
COMPOSE_FILE="docker-compose.prod.yml"
HEALTH_URL="http://localhost:80/health"
MAX_WAIT_SECONDS=60

echo "==> Deploying image tag: ${TAG}"
export IMAGE_TAG="${TAG}"

echo "==> Pulling images"
docker compose -f "${COMPOSE_FILE}" pull backend frontend

echo "==> Ensuring database is up"
docker compose -f "${COMPOSE_FILE}" up -d db
docker compose -f "${COMPOSE_FILE}" exec -T db sh -c 'until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do sleep 1; done'

# Uncomment once Alembic migrations are introduced (post Milestone 1):
# echo "==> Running database migrations"
# docker compose -f "${COMPOSE_FILE}" run --rm backend alembic upgrade head

echo "==> Rolling out backend and frontend"
docker compose -f "${COMPOSE_FILE}" up -d --no-deps backend frontend

echo "==> Waiting for health check at ${HEALTH_URL}"
elapsed=0
until curl -fsS "${HEALTH_URL}" > /dev/null 2>&1; do
  if [ "${elapsed}" -ge "${MAX_WAIT_SECONDS}" ]; then
    echo "!! Health check failed after ${MAX_WAIT_SECONDS}s — deploy aborted."
    echo "!! Check logs: docker compose -f ${COMPOSE_FILE} logs backend frontend"
    exit 1
  fi
  sleep 2
  elapsed=$((elapsed + 2))
done

echo "==> Healthy. Pruning dangling images."
docker image prune -f > /dev/null

echo "==> Deploy of ${TAG} complete."
