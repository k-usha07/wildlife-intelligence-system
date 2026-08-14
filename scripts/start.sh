#!/usr/bin/env bash
# ============================================================================
# Backend startup script for Render / Docker production
# ============================================================================

set -euo pipefail

echo "🦁 Wildlife Intelligence Backend starting..."

# ── Wait for database ────────────────────────────────────────────────────
echo "⏳ Checking database connectivity..."
for i in $(seq 1 30); do
    if python -c "
import psycopg2, os
conn = psycopg2.connect(os.environ['DATABASE_URL'])
conn.close()
" 2>/dev/null; then
        echo "✅ Database is ready"
        break
    fi
    echo "  Attempt $i/30 — waiting 2s..."
    sleep 2
done

# ── Run Alembic migrations (if configured) ────────────────────────────────
if [ -d "alembic" ] && [ -f "alembic.ini" ]; then
    echo "📦 Running database migrations..."
    alembic upgrade head || echo "⚠️  Migration failed, continuing..."
fi

# ── Seed roles if table is empty ─────────────────────────────────────────
echo "🌱 Seeding roles..."
python -c "
import psycopg2, os, uuid
conn = psycopg2.connect(os.environ['DATABASE_URL'])
conn.autocommit = True
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM roles')
if cur.fetchone()[0] == 0:
    cur.execute(\"\"\"
        INSERT INTO roles (name, description) VALUES
        ('admin', 'Full platform administration'),
        ('researcher', 'Wildlife Researcher'),
        ('conservation_officer', 'Conservation Officer'),
        ('forest_department', 'Forest Department Officer')
    \"\"\")
    print('  ✅ Roles seeded')
else:
    print('  ℹ️  Roles already exist')
cur.close()
conn.close()
" || echo "⚠️  Role seeding skipped"

# ── Download ML models if missing ─────────────────────────────────────────
MODELS_DIR="${YOLO_MODEL_PATH%/*}"
if [ ! -z "$MODELS_DIR" ] && [ ! -d "$MODELS_DIR" ]; then
    mkdir -p "$MODELS_DIR"
fi

if [ "${ENABLE_ML_MODELS:-false}" = "true" ]; then
    echo "🤖 Checking ML models..."
    if [ ! -f "${YOLO_MODEL_PATH:-/dev/null}" ]; then
        echo "  📥 YOLOv8 model not found — will download on first use (ultralytics auto-download)"
    else
        echo "  ✅ YOLOv8 model found"
    fi
fi

# ── Start application ────────────────────────────────────────────────────
WORKERS="${WEB_CONCURRENCY:-4}"
PORT="${PORT:-8000}"

echo "🚀 Starting uvicorn with $WORKERS workers on port $PORT"
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers "$WORKERS" \
    --no-access-log \
    --proxy-headers \
    --forwarded-allow-ips='*'