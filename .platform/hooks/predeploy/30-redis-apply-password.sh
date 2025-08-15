#!/usr/bin/env bash
set -euxo pipefail

# If REDIS_PASSWORD is set as an EB env var, append/refresh requirepass.
# (Keeps your repo copy free of secrets.)
if [[ -n "${REDIS_PASSWORD-}" ]]; then
  sed -i '/^requirepass /d' /etc/redis6/redis.conf
  echo "requirepass ${REDIS_PASSWORD}" >> /etc/redis6/redis.conf
fi
