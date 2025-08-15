#!/usr/bin/env bash
set -euxo pipefail

# Copy your versioned redis.conf into place
install -o root -g root -m 0644 \
  /opt/elasticbeanstalk/deployment/app_source/.platform/files/redis.conf \
  /etc/redis6/redis.conf
