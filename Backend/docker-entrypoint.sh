#!/usr/bin/env sh
set -e

mkdir -p "${UPLOAD_DIR:-./uploads}" "$(dirname "${LOG_FILE:-./logs/icms.log}")"

python - <<'PY'
import os
import socket
import sys
import time
from urllib.parse import urlparse

database_url = os.environ.get("DATABASE_URL", "")
if not database_url or database_url.startswith("sqlite"):
    sys.exit(0)

parsed = urlparse(database_url)
host = parsed.hostname
port = parsed.port or 5432
timeout = int(os.environ.get("WAIT_FOR_DB_TIMEOUT", "60"))

if not host:
    sys.exit(0)

for attempt in range(1, timeout + 1):
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"Database is reachable at {host}:{port}")
            sys.exit(0)
    except OSError:
        if attempt == timeout:
            print(f"Timed out waiting for database at {host}:{port}", file=sys.stderr)
            sys.exit(1)
        time.sleep(1)
PY

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  alembic upgrade head
fi

if [ "${RUN_SEED_DATA:-false}" = "true" ]; then
  python scripts/seed_data.py
fi

exec uvicorn core.main:app \
  --host "${HOST:-0.0.0.0}" \
  --port "${PORT:-8000}"
