#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  VERSION="$(poetry version -s)"
fi

TAG="v${VERSION}"

if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Tag ${TAG} already exists."
  exit 1
fi

git tag -a "$TAG" -m "Release ${TAG}"
echo "Created tag ${TAG}"
echo "Push with: git push origin ${TAG}"
