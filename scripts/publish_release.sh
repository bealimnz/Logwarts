#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <pypi|internal> [--dry-run]"
  exit 1
fi

TARGET="$1"
DRY_RUN="${2:-}"

if [[ "$DRY_RUN" == "--dry-run" ]]; then
  BASE_CMD=(poetry publish --dry-run --build)
else
  BASE_CMD=(poetry publish --build)
fi

case "$TARGET" in
  pypi)
    "${BASE_CMD[@]}"
    ;;
  internal)
    "${BASE_CMD[@]}" -r internal
    ;;
  *)
    echo "Invalid target: $TARGET (expected pypi or internal)"
    exit 1
    ;;
esac
