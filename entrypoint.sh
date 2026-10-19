#!/bin/sh
set -e

echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
while ! python -c "
import os, socket
host = os.environ.get('DB_HOST', 'db')
port = int(os.environ.get('DB_PORT', '5432'))
s = socket.socket()
s.settimeout(1)
try:
    s.connect((host, port))
except Exception:
    raise SystemExit(1)
finally:
    s.close()
" 2>/dev/null; do
  sleep 1
done
echo "PostgreSQL is ready."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
