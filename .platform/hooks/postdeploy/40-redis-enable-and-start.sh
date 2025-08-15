#!/usr/bin/env bash
set -euxo pipefail

# Ensure systemd knows about any changes and (re)start Redis
systemctl daemon-reload || true
systemctl enable redis
systemctl restart redis

# Optional sanity check (won't fail the deploy)
if command -v redis-cli >/dev/null 2>&1; then
  if [[ -n "${REDIS_PASSWORD-}" ]]; then
    redis-cli -a "$REDIS_PASSWORD" ping || true
  else
    redis-cli ping || true
  fi
fi
