#!/bin/bash
set -e

echo "Running migrations..."
alembic upgrade head

until curl -s -f http://keycloak:8080/realms/master > /dev/null; do
  echo "Keycloak is still unavailable (master realm not ready) - sleeping"
  sleep 2
done

echo "Keycloak is up! Starting application..."

echo "Starting application..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
