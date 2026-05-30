#!/usr/bin/env bash
set -euo pipefail

exec celery -A app.worker.tasks:celery_app worker -l info
