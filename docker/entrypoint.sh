#!/bin/sh
set -e

mkdir -p /app/app/data
chown -R app:app /app/app/data

exec setpriv --reuid=1001 --regid=1001 --init-groups -- "$@"
