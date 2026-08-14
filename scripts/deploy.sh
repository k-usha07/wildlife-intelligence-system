#!/usr/bin/env bash
# ============================================================================
# Production deployment script
# Usage: IMAGE_TAG=<sha> ./scripts/deploy.sh <sha>
# ============================================================================

set -euo pipefail

TAG="${1:-latest}"
REGISTRY="${REGISTRY:-ghcr.io/k-usha07/wildlife-intelligence-system}"

echo "🚀 Deploying Wildlife Intelligence System"
echo "   Image tag: $TAG"
echo "   Registry:  $REGISTRY"

# ── Pull images ──────────────────────────────────────────────────────────
echo "📦 Pulling images..."
docker pull "$REGISTRY/wpi-backend:$TAG"
docker pull "$REGISTRY/wpi-frontend:$TAG"

# ── Run migrations ───────────────────────────────────────────────────────
echo "📦 Running database migrations..."
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# ── Roll out new containers ─────────────────────────────────────────────
echo "🔄 Rolling out new containers..."
export IMAGE_TAG="$TAG"
docker compose -f docker-compose.prod.yml up -d

# ── Health check ────────────────────────────────────────────────────────
echo "🩺 Running health checks..."
for i in $(seq 1 20); do
    if curl -sf http://localhost/health > /dev/null 2>&1; then
        echo "✅ All services healthy!"
        break
    fi
    echo "  Attempt $i/20 — waiting 5s..."
    sleep 5
done

# ── Prune old images ────────────────────────────────────────────────────
echo "🧹 Pruning old images..."
docker image prune -f

echo "✅ Deployment complete!"