#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <patch|minor|major|X.Y.Z>"
  exit 1
fi

TARGET="$1"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Working tree is not clean. Commit or stash changes before preparing a release."
  exit 1
fi

if [[ "$TARGET" =~ ^(patch|minor|major)$ ]]; then
  poetry version "$TARGET"
else
  poetry version "$TARGET"
fi

NEW_VERSION="$(poetry version -s)"
TAG="v${NEW_VERSION}"

poetry check
poetry build
poetry publish --dry-run --build

echo "Release prepared for ${NEW_VERSION}"
echo "Next steps:"
echo "  1) Update CHANGELOG.md release date/entries if needed"
echo "  2) git add pyproject.toml poetry.lock CHANGELOG.md"
echo "  3) git commit -m \"release: ${TAG}\""
echo "  4) git tag -a ${TAG} -m \"Release ${TAG}\""
echo "  5) git push && git push origin ${TAG}"
