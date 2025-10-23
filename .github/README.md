# GitHub Configuration

This directory contains GitHub-specific configuration files for the Kubera Python API project.

## Files and Purpose

### Issue Templates (`ISSUE_TEMPLATE/`)

- **`bug_report.yml`** - Structured bug report template with required fields
- **`feature_request.yml`** - Feature request template for new functionality
- **`config.yml`** - Configuration for issue templates, links to discussions and docs

### Workflows (`workflows/`)

- **`ci.yml`** - Continuous Integration workflow
  - Runs on: pushes to main, PRs, manual trigger
  - Tests: Python 3.10, 3.11, 3.12 on Ubuntu, macOS, Windows
  - Checks: linting (ruff), formatting (ruff), type checking (mypy), tests (pytest)
  - Coverage: uploads to Codecov
  - Build: validates package build

- **`dependabot-auto-merge.yml`** - Auto-merge for Dependabot PRs
  - Auto-approves: minor and patch dependency updates
  - Auto-merges: after CI passes
  - Manual review required: major version updates
  - Applies to: both Python dependencies and GitHub Actions

### Other Files

- **`SECURITY.md`** - Security policy and vulnerability reporting guidelines
- **`PULL_REQUEST_TEMPLATE.md`** - Template for pull requests with checklist

### Dependabot Configuration (`dependabot.yml`)

Automatic dependency updates configured for:

**Python Dependencies:**
- Schedule: Weekly on Mondays at 9:00 AM
- Groups minor/patch updates together
- Separate PRs for major updates (require manual review)
- Auto-label with `dependencies` and `python`

**GitHub Actions:**
- Schedule: Weekly on Mondays at 9:00 AM
- Groups all action updates together
- Auto-label with `dependencies` and `github-actions`

## CI/CD Pipeline

### On Every Push/PR

1. **Linting**: `ruff check .`
2. **Formatting**: `ruff format --check .`
3. **Type Checking**: `mypy kubera`
4. **Tests**: `pytest --cov=kubera`
5. **Build**: Package build verification

### Matrix Testing

Tests run on:
- **OS**: Ubuntu, macOS, Windows
- **Python**: 3.10, 3.11, 3.12

### Dependabot Auto-Merge Flow

1. Dependabot opens PR
2. CI runs automatically
3. Auto-approve (for minor/patch)
4. Wait for CI to pass
5. Auto-merge (squash)

**Major updates require manual review!**

## Setup Required

### Repository Settings

To enable auto-merge, configure these in your repository:

1. **Settings → General → Pull Requests**
   - ✅ Enable "Allow auto-merge"
   - ✅ Enable "Allow squash merging"

2. **Settings → Branches → Branch protection for `main`**
   - ✅ Require status checks to pass before merging
   - ✅ Require "All checks passed" status check
   - ✅ Require branches to be up to date before merging

3. **Settings → Code security and analysis**
   - ✅ Enable Dependabot alerts
   - ✅ Enable Dependabot security updates

### Secrets (Optional)

- **`CODECOV_TOKEN`** - For code coverage reporting (get from codecov.io)

## Badges

The following badges are displayed in the main README:

- **CI Status** - Shows if tests are passing
- **Python Version** - Supported Python versions
- **License** - MIT License badge

## Issue Labels

Consider creating these labels for better issue management:

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `needs-triage` - Needs initial review
- `dependencies` - Dependency updates
- `python` - Python dependency updates
- `github-actions` - GitHub Actions updates

## Contributing

All GitHub configurations follow best practices:
- Issue templates ensure complete bug reports
- PR template ensures quality contributions
- CI ensures code quality before merge
- Dependabot keeps dependencies secure and up-to-date

See [CONTRIBUTING.md](../CONTRIBUTING.md) for full contribution guidelines.
