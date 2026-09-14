#!/bin/sh
set -eu

alembic upgrade head

# exec "$@"

if [ "$#" -eq 0 ]; then
    set -- uvicorn main:app \
        --host 0.0.0.0 \
        --port "${PORT:-8000}"
fi

exec "$@"
# exec uvicorn main:app \
#   --host 0.0.0.0 \
#   --port "${PORT:-8000}"