#!/bin/bash

set -e

# activate our virtual environment here
#. /opt/pysetup/.venv/bin/activate

WORKERS=${WORKERS:-1}
LOG_LEVEL=${LOG_LEVEL:-INFO}

usage() {
  echo "Usage: $0 [celery|fastapi]"
  echo "  - fastapi: start the fastapi server"
  echo "  - celery: start the celery worker"
}

if [[ "$1" == "celery" ]]; then
  python worker/main.py
elif [[ "$1" == "fastapi" ]]; then
  python api/main.py
else
  echo "Unknown or missing sub-command: '$1'"
  usage
  exit 1
fi
