#!/usr/bin/env bash
set -euxo pipefail

# Install Redis using AL2023's package manager (dnf)
# (yum is a compat alias, but dnf is canonical on AL2023)
dnf -y install redis

# Create data & log directories with correct ownership
mkdir -p /var/lib/redis
mkdir -p /var/log/redis
touch /var/log/redis/redis-server.log
chown -R redis:redis /var/lib/redis /var/log/redis /var/log/redis/redis-server.log
chmod 0755 /var/lib/redis

# Some recommended kernel settings for Redis (safe on dev/small workloads)
# Overcommit helps background save operations
sysctl -w vm.overcommit_memory=1
# Disable Transparent Huge Pages at runtime (best-effort; non-fatal if path differs)
if [ -f /sys/kernel/mm/transparent_hugepage/enabled ]; then
  echo never > /sys/kernel/mm/transparent_hugepage/enabled || true
fi
