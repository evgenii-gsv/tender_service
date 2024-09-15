#!/usr/bin/env bash

set -e

RUN_MANAGE_PY='poetry run python3 -m tender_service.manage'

echo 'Collecting static files...'
$RUN_MANAGE_PY collectstatic --no-input

echo 'Running migrations...'
$RUN_MANAGE_PY migrate --no-input

exec poetry run gunicorn tender_service.project.wsgi:application -b ${SERVER_ADDRESS:-0.0.0.0:8080} -w 3
