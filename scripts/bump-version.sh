#!/bin/bash

set -e

if [ -z "$1" ]; then
  echo "Usage: ./scripts/bump-version.sh <major|minor|patch>"
  exit 1
fi

CURRENT_VERSION=$(cat VERSION)
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"

MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

case $1 in
  major)
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    ;;
  minor)
    MINOR=$((MINOR + 1))
    PATCH=0
    ;;
  patch)
    PATCH=$((PATCH + 1))
    ;;
  *)
    echo "Invalid argument: $1"
    exit 1
    ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"

echo "================================================"
echo "Bumping version from $CURRENT_VERSION to $NEW_VERSION"
echo "================================================"

# Update VERSION file
echo "$NEW_VERSION" > VERSION
echo "✓ Updated VERSION file"

# Update backend/__init__.py
if [ -f "backend/app/__init__.py" ]; then
  sed -i "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" backend/app/__init__.py
  echo "✓ Updated backend/app/__init__.py"
else
  echo "⚠ backend/app/__init__.py not found - creating it"
  mkdir -p backend/app
  echo "__version__ = \"$NEW_VERSION\"" > backend/app/__init__.py
fi

# Update frontend/package.json
if [ -f "frontend/package.json" ]; then
  sed -i "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" frontend/package.json
  echo "✓ Updated frontend/package.json"
else
  echo "⚠ frontend/package.json not found"
fi

# Update README.md
if [ -f "README.md" ]; then
  sed -i "s/\*\*v[0-9]*\.[0-9]*\.[0-9]*\*\*/**v$NEW_VERSION**/" README.md
  echo "✓ Updated README.md"
fi

echo ""
echo "================================================"
echo "Version successfully bumped to $NEW_VERSION"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Update CHANGELOG.md with release date and entries"
echo "2. Create release notes: RELEASE_NOTES/v$NEW_VERSION.md"
echo "3. Review changes: git diff"
echo "4. Commit: git commit -am 'chore: bump version to $NEW_VERSION'"
echo "5. Create tag: git tag -a v$NEW_VERSION -m 'Release v$NEW_VERSION'"
echo "6. Push: git push origin main && git push origin v$NEW_VERSION"
echo ""
