# Version Management & Release Notes

## Overview

This document defines the versioning strategy and release notes workflow for the TPRM Agent project.

## Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH

Examples:
- 1.0.0 - Initial release
- 1.1.0 - New feature (Combined Analysis)
- 1.1.1 - Bug fix
- 2.0.0 - Breaking change (API redesign)
```

### Version Increments

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backward-compatible functionality)
- **PATCH**: Bug fixes (backward-compatible fixes)

---

## Current Version

**v1.0.0** - Initial Release (2024-11-20)

---

## Planned Releases

### v1.1.0 - Combined Document Analysis (Target: Week 2)
- Multi-document analysis endpoint
- Cross-document synthesis with AI
- Comprehensive vendor risk reports
- Decision recommendations (Go/No-Go)

### v1.2.0 - Risk Matrix (Target: Week 4)
- Configurable risk matrix
- Visual heatmap component
- Criticality scoring system
- Matrix-based vendor positioning

### v1.3.0 - EntraID Authentication (Target: Week 6)
- Microsoft Entra ID (Azure AD) integration
- SSO support
- User role management
- Audit logging

### v2.0.0 - AI Agent System (Target: Week 8)
- Full autonomous AI agent with LangGraph
- Memory system with vector store
- MCP tool integration
- CASB integration (Microsoft Defender, Netskope)

---

## Release Process

### 1. Pre-Release Checklist

- [ ] All features implemented and tested
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Release notes drafted
- [ ] Version bumped in all files
- [ ] Docker images built and tagged
- [ ] Security scan passed
- [ ] Performance benchmarks met

### 2. Version Bump

Update version in these files:

**Backend**:
```python
# backend/app/__init__.py
__version__ = "1.1.0"
```

**Frontend**:
```json
// frontend/package.json
{
  "version": "1.1.0"
}
```

**README.md**:
```markdown
## Version

**v1.1.0** - Combined Document Analysis
```

**CLAUDE.md**: Update "Current Application State" section

### 3. Create Release Notes

**File**: `RELEASE_NOTES/v1.1.0.md`

Template:

```markdown
# Release Notes - v1.1.0

**Release Date**: YYYY-MM-DD
**Type**: Minor Release

## Summary

Brief 2-3 sentence summary of the release.

## New Features

### Combined Document Analysis
- **Description**: Analyze all vendor documents together for holistic risk assessment
- **User Story**: As a risk analyst, I want to analyze all documents at once so I can identify cross-document inconsistencies
- **Implementation**: New `/vendors/{id}/analyze-all` endpoint with multi-document context
- **UI Changes**: "Analyze All Documents" button on vendor detail page
- **Configuration**: Enable with `FEATURE_COMBINED_ANALYSIS=true`

## Improvements

- Enhanced AI prompts for better risk detection
- Improved error handling in document upload
- Faster document text extraction

## Bug Fixes

- Fixed issue with upload count showing 0
- Resolved Airtable query failures for linked records
- Fixed Gemini API model compatibility

## Breaking Changes

None

## Migration Guide

No migration needed - backward compatible with v1.0.0

## API Changes

### New Endpoints

**POST** `/vendors/{vendor_id}/analyze-all`
```json
Request: {}
Response: {
  "overall_risk_score": 65,
  "overall_risk_level": "Medium",
  "consolidated_findings": [...],
  "cross_document_insights": [...],
  "recommendations": [...],
  "decision_recommendation": {
    "decision": "CONDITIONAL",
    "justification": "...",
    "required_actions": [...]
  }
}
```

### Modified Endpoints

None

### Deprecated Endpoints

None

## Database Changes

### Airtable Schema Updates

**Vendors Table**: New fields
- `Overall Risk Score` (Number)
- `Overall Risk Level` (Single select: Low, Medium, High)
- `Decision Status` (Single select: Go, Conditional, No-Go)
- `Last Full Analysis` (Date)

## Dependencies

### Added
- None (uses existing Gemini AI)

### Updated
- None

## Configuration

### New Environment Variables

- `FEATURE_COMBINED_ANALYSIS` - Enable combined analysis (default: true)
- `MAX_COMBINED_ANALYSIS_DOCS` - Max docs to analyze together (default: 10)

### Modified Environment Variables

None

## Deployment

### Kubernetes

Update deployment:
```bash
kubectl set image deployment/tprm-backend \
  fastapi=your-registry/tprm-backend:1.1.0 \
  -n tprm-agent

kubectl set image deployment/tprm-frontend \
  nextjs=your-registry/tprm-frontend:1.1.0 \
  -n tprm-agent
```

### Docker Compose

```bash
docker-compose pull
docker-compose up -d
```

## Known Issues

- Large document sets (>20 files) may timeout - increase `GEMINI_TIMEOUT` if needed
- Analysis of very long documents may hit token limits

## Testing

### Manual Testing Checklist

- [ ] Upload multiple documents for a vendor
- [ ] Click "Analyze All Documents"
- [ ] Verify results show cross-document insights
- [ ] Check decision recommendation appears
- [ ] Ensure individual document analyses still work

### Automated Tests

- `test_analyze_all_documents()` - Combined analysis endpoint
- `test_cross_document_synthesis()` - AI synthesis logic
- `test_decision_recommendation()` - Go/No-Go logic

## Performance

- Combined analysis: ~30s for 5 documents
- Memory usage: +200MB during analysis
- No impact on single-document analysis

## Security

- No new security vulnerabilities introduced
- All API calls authenticated with EntraID (v1.3.0+)

## Rollback Plan

If issues occur:

```bash
# Rollback to v1.0.0
kubectl rollout undo deployment/tprm-backend -n tprm-agent
kubectl rollout undo deployment/tprm-frontend -n tprm-agent

# Or set specific version
kubectl set image deployment/tprm-backend \
  fastapi=your-registry/tprm-backend:1.0.0 \
  -n tprm-agent
```

## Contributors

- @your-username - Combined analysis implementation
- @contributor - AI prompt engineering

## Acknowledgments

Thanks to the team for feedback on the combined analysis feature!

---

For questions or issues, please open a GitHub issue or contact the development team.
```

### 4. Update CHANGELOG.md

**File**: `CHANGELOG.md`

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Risk matrix visualization
- EntraID authentication
- AI agent system with MCP tools

## [1.1.0] - YYYY-MM-DD

### Added
- Combined multi-document analysis endpoint
- Cross-document synthesis with AI
- Decision recommendations (Go/No-Go)
- "Analyze All Documents" button in UI

### Changed
- Enhanced AI prompts for better risk detection
- Improved error handling in document upload

### Fixed
- Upload count showing 0 after successful upload
- Airtable query failures for linked records

## [1.0.0] - 2024-11-20

### Added
- FastAPI backend with async support
- Next.js frontend with dark theme
- Multi-file document upload
- Real Gemini AI analysis (gemini-2.5-flash)
- Airtable integration (Vendors + Documents tables)
- Document storage with accessible URLs
- Individual document analysis
- Risk scoring and findings display
- Local storage with cloud-ready architecture

### Infrastructure
- Docker support
- Kubernetes manifests
- Environment-based configuration

### Documentation
- README.md with setup instructions
- CLAUDE.md for AI-assisted development
- AI_AGENT_ARCHITECTURE.md for future autonomous agents
- NO_CODE_AGENT_PLATFORMS.md for n8n integration
- KUBERNETES.md for production deployment

---

[Unreleased]: https://github.com/your-org/tprm-agent/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/your-org/tprm-agent/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/your-org/tprm-agent/releases/tag/v1.0.0
```

---

## Git Workflow

### Creating a Release

```bash
# 1. Create release branch
git checkout -b release/v1.1.0

# 2. Bump version in files
# - backend/app/__init__.py
# - frontend/package.json
# - README.md

# 3. Update CHANGELOG.md
# Add release date and finalize entries

# 4. Create release notes
mkdir -p RELEASE_NOTES
cat > RELEASE_NOTES/v1.1.0.md << EOF
[Release notes content]
EOF

# 5. Commit changes
git add .
git commit -m "chore: bump version to 1.1.0"

# 6. Merge to main
git checkout main
git merge release/v1.1.0

# 7. Create git tag
git tag -a v1.1.0 -m "Release v1.1.0: Combined Document Analysis"

# 8. Push to remote
git push origin main
git push origin v1.1.0

# 9. Delete release branch
git branch -d release/v1.1.0
```

### GitHub Release

After pushing the tag, create a GitHub Release:

1. Go to **Releases** > **Draft a new release**
2. Select tag: `v1.1.0`
3. Release title: `v1.1.0 - Combined Document Analysis`
4. Description: Copy from `RELEASE_NOTES/v1.1.0.md`
5. Attach built artifacts (optional):
   - `tprm-backend-1.1.0.tar.gz`
   - `tprm-frontend-1.1.0.tar.gz`
6. Click **Publish release**

---

## Automated Release Workflow

**GitHub Actions**: `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Extract version
      id: version
      run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

    - name: Build Docker images
      run: |
        docker build -t ghcr.io/${{ github.repository }}/tprm-backend:${{ steps.version.outputs.VERSION }} ./backend
        docker build -t ghcr.io/${{ github.repository }}/tprm-frontend:${{ steps.version.outputs.VERSION }} ./frontend

    - name: Push Docker images
      run: |
        echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin
        docker push ghcr.io/${{ github.repository }}/tprm-backend:${{ steps.version.outputs.VERSION }}
        docker push ghcr.io/${{ github.repository }}/tprm-frontend:${{ steps.version.outputs.VERSION }}

    - name: Create GitHub Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ steps.version.outputs.VERSION }}
        body_path: RELEASE_NOTES/v${{ steps.version.outputs.VERSION }}.md
        draft: false
        prerelease: false

    - name: Deploy to K8s (optional)
      if: github.ref == 'refs/tags/v*'
      run: |
        # Add deployment commands here
        echo "Deploying to production..."
```

---

## Version File Tracking

Create a central version file:

**File**: `VERSION`

```
1.1.0
```

**Script**: `scripts/bump-version.sh`

```bash
#!/bin/bash

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

echo "Bumping version from $CURRENT_VERSION to $NEW_VERSION"

# Update VERSION file
echo "$NEW_VERSION" > VERSION

# Update backend/__init__.py
sed -i "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" backend/app/__init__.py

# Update frontend/package.json
sed -i "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" frontend/package.json

# Update README.md
sed -i "s/\*\*v[0-9]*\.[0-9]*\.[0-9]*\*\*/**v$NEW_VERSION**/" README.md

echo "Version bumped to $NEW_VERSION"
echo "Next steps:"
echo "1. Update CHANGELOG.md"
echo "2. Create release notes in RELEASE_NOTES/v$NEW_VERSION.md"
echo "3. Commit: git commit -am 'chore: bump version to $NEW_VERSION'"
echo "4. Tag: git tag -a v$NEW_VERSION -m 'Release v$NEW_VERSION'"
echo "5. Push: git push origin main && git push origin v$NEW_VERSION"
```

**Usage**:

```bash
# Bump minor version (1.0.0 → 1.1.0)
./scripts/bump-version.sh minor

# Bump patch version (1.1.0 → 1.1.1)
./scripts/bump-version.sh patch

# Bump major version (1.1.1 → 2.0.0)
./scripts/bump-version.sh major
```

---

## Communication

### Announcement Template

**Subject**: TPRM Agent v1.1.0 Released - Combined Document Analysis

**Body**:

```
Hi Team,

We're excited to announce the release of TPRM Agent v1.1.0!

🎉 What's New:
- Combined Document Analysis: Analyze all vendor documents together for comprehensive risk assessment
- Cross-Document Insights: AI identifies contradictions and patterns across multiple documents
- Decision Recommendations: Get automated Go/No-Go decisions with justification

📖 Full release notes: https://github.com/your-org/tprm-agent/releases/tag/v1.1.0

🚀 Upgrade Instructions:
For K8s deployments, run:
  kubectl set image deployment/tprm-backend fastapi=registry/tprm-backend:1.1.0 -n tprm-agent
  kubectl set image deployment/tprm-frontend nextjs=registry/tprm-frontend:1.1.0 -n tprm-agent

For local development:
  git pull origin main
  git checkout v1.1.0
  docker-compose pull && docker-compose up -d

❓ Questions or Issues?
Open a GitHub issue or reach out to the team.

Happy risk analyzing!
- The TPRM Team
```

---

## Release Checklist Template

Copy this for each release:

```markdown
## Release Checklist - v1.1.0

### Pre-Release (1 week before)
- [ ] All features merged to `main`
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Security scan completed
- [ ] Performance benchmarks met

### Release Week
- [ ] Version bumped with `./scripts/bump-version.sh minor`
- [ ] CHANGELOG.md updated with release date
- [ ] Release notes created in `RELEASE_NOTES/v1.1.0.md`
- [ ] Docker images built and tested
- [ ] K8s manifests updated with new version
- [ ] Staging deployment successful
- [ ] UAT (User Acceptance Testing) completed

### Release Day
- [ ] Create release branch: `git checkout -b release/v1.1.0`
- [ ] Final commit: `git commit -am "chore: release v1.1.0"`
- [ ] Merge to main
- [ ] Create tag: `git tag -a v1.1.0 -m "Release v1.1.0"`
- [ ] Push: `git push origin main && git push origin v1.1.0`
- [ ] GitHub Release created
- [ ] Production deployment started
- [ ] Deployment verified
- [ ] Announcement sent to team
- [ ] Documentation site updated

### Post-Release
- [ ] Monitor logs for 24 hours
- [ ] Address any hotfix issues
- [ ] Update project board
- [ ] Retrospective scheduled
```

---

This version management system ensures consistent, documented, and traceable releases for every feature update to the TPRM Agent.
