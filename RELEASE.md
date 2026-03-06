# Release Guide

## Versioning Strategy (SemVer)

Logwarts uses Semantic Versioning:

- `MAJOR`: incompatible API changes.
- `MINOR`: backward-compatible features.
- `PATCH`: backward-compatible fixes only.

Version tags must be prefixed with `v`:

- `v1.2.3`

## Changelog Policy

- Keep all upcoming changes under `## [Unreleased]` in `CHANGELOG.md`.
- At release time:
  - Move unreleased entries into `## [X.Y.Z] - YYYY-MM-DD`.
  - Keep entries grouped by `Added`, `Changed`, `Fixed`, `Removed`.

## Local Release Steps

1. Ensure branch is up to date and tests pass.
2. Update `CHANGELOG.md` (`Unreleased` -> new version section).
3. Bump version:
   - `poetry version patch` or `poetry version minor` or `poetry version major`
4. Validate packaging:
   - `poetry check`
   - `poetry build`
   - `poetry publish --dry-run --build`
5. Commit release files and tag:
   - `git commit -am "release: vX.Y.Z"`
   - `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
6. Push commit and tag:
   - `git push`
   - `git push origin vX.Y.Z`

## Publishing Targets

### PyPI

Configure token:

```bash
poetry config pypi-token.pypi "$PYPI_TOKEN"
```

Publish:

```bash
poetry publish --build
```

### Internal Registry

Configure repository and token:

```bash
poetry config repositories.internal "$INTERNAL_PYPI_URL"
poetry config pypi-token.internal "$INTERNAL_PYPI_TOKEN"
```

Publish:

```bash
poetry publish --build -r internal
```
