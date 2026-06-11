#!/bin/bash
#!/bin/bash
#!/usr/bin/env bash
# Release automation for WRedis
# Usage: ./release.sh <version>
# Example: ./release.sh 1.0.1

set -euo pipefail

VERSION="${1:-}"
if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.0.1"
    exit 1
fi

# Validate semver
if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "Error: Version must be semver (e.g., 1.0.1)"
    exit 1
fi

echo "=== WRedis Release: $VERSION ==="

# 1. Check clean working tree
if [ -n "$(git status --porcelain)" ]; then
    echo "Error: Working tree is not clean. Commit or stash changes first."
    exit 1
fi

# 2. Run tests
echo "[1/7] Running tests..."
python -m pytest tests/unit --cov=wredis -q --tb=short --timeout=5
echo "Tests passed."

# 3. Run lint
echo "[2/7] Running lint checks..."
python -m ruff check wredis/ tests/
python -m ruff format --check wredis/ tests/
echo "Lint passed."

# 4. Run typecheck
echo "[3/7] Running type checks..."
python -m mypy wredis/ --ignore-missing-imports
echo "Type checks passed."

# 5. Update version
echo "[4/7] Updating version to $VERSION..."
sed -i "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# 6. Update CHANGELOG
echo "[5/7] Updating CHANGELOG.md..."
DATE=$(date +%Y-%m-%d)
CHANGELOG_ENTRY="## v$VERSION ($DATE)\n\n### Changes\n- See git log for details\n"
if grep -q "## Unreleased" CHANGELOG.md; then
    sed -i "s/## Unreleased/## Unreleased\n\n$CHANGELOG_ENTRY/" CHANGELOG.md
else
    sed -i "1i\\# Changelog\n\n## Unreleased\n\n$CHANGELOG_ENTRY" CHANGELOG.md
fi

# 7. Commit and tag
echo "[6/7] Creating commit and tag..."
git add pyproject.toml CHANGELOG.md
git commit -m "Release v$VERSION"
git tag -a "v$VERSION" -m "Release v$VERSION"

# 8. Build
echo "[7/7] Building package..."
python -m build

echo ""
echo "=== Release v$VERSION prepared ==="
echo "Next steps:"
echo "  1. Review: git show v$VERSION"
echo "  2. Push: git push origin main --tags"
echo "  3. Publish: twine upload dist/wredis-$VERSION*"
echo "  4. Create GitHub release from tag v$VERSION"
