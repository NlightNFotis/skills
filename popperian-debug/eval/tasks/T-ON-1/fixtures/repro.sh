#!/usr/bin/env bash
# Reproduce the failing test. Exits non-zero when the bug is present.
set -u
cd "$(dirname "$0")"
export PYTHONPATH="$PWD"
exec python3 -m pytest tests/ -q
