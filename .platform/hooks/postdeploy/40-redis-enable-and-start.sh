#!/usr/bin/env bash
set -euxo pipefail

# Ensure systemd knows about any changes and (re)start Redis
systemctl daemon-reload || true
systemctl enable redis6
systemctl restart redis6

# Optional sanity check (won't fail the deploy)
if command -v redis6-cli >/dev/null 2>&1; then
  if [[ -n "${REDIS_PASSWORD-}" ]]; then
    redis6-cli -a "$REDIS_PASSWORD" ping || true
  else
    redis6-cli ping || true
  fi
fi
