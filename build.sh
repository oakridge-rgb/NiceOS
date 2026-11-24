#!/bin/sh
# Build the NiceOS ISO.
#
#   Native (Debian 13 host):      sudo ./build.sh
#   Container (any Linux host):   docker build -t niceos-builder .
#                                 docker run --rm --privileged \
#                                     -v "$PWD":/niceos niceos-builder
#
# Output: binary.iso (rename as you like).
set -e
cd "$(dirname "$0")"

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: live-build must run as root. Try: sudo $0" >&2
    exit 1
fi

exec ./auto/build "$@"
