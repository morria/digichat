# DigiChat Development Guide

This guide covers the development workflow, including linting, testing, and CI/CD setup.

## Quick Start

1. **Install development dependencies:**
   ```bash
   make install
   ```

2. **Run all checks (same as CI):**
   ```bash
   make check
   ```

## Development Workflow

### Available Commands

Run `make` or `make help` to see all available commands:

- `make install` - Install development dependencies and pre-commit hooks
- `make format` - Auto-format code (isort + black)
- `make lint` - Run all linters (isort, black, ruff, mypy)
- `make test` - Run tests with coverage
- `make check` - Run all checks (lint + test) - **same as CI**
- `make pre-commit` - Run pre-commit on all files
- `make clean` - Clean up generated files

### Code Quality Tools

DigiChat uses several tools to ensure code quality:

1. **isort** - Sorts imports alphabetically and separates them into sections
2. **black** - Opinionated code formatter for consistent style
3. **ruff** - Fast Python linter (replaces flake8, pylint, etc.)
4. **mypy** - Static type checker
5. **pytest** - Testing framework with coverage reporting

All tools are configured in `pyproject.toml`.

## Pre-commit Hooks

Pre-commit hooks automatically run linters and tests before each commit. This ensures that:
- Code is properly formatted
- Imports are sorted
- Linting checks pass
- Type checking passes
- Tests pass

### Installation

Pre-commit hooks are automatically installed when you run `make install` or when Claude Code starts a session.

Manual installation:
```bash
pip install pre-commit
pre-commit install
```

### Running Pre-commit Manually

To run pre-commit on all files:
```bash
pre-commit run --all-files
```

To run pre-commit on staged files only:
```bash
pre-commit run
```

### Skipping Pre-commit Hooks

**Not recommended**, but you can skip hooks with:
```bash
git commit --no-verify
```

However, your changes will still be checked by CI, so it's better to fix issues locally.

## CI/CD Pipeline

### GitHub Actions Workflow

The CI pipeline runs on:
- All pull requests to `main` or `master`
- All pushes to `main` or `master`

The workflow (`.github/workflows/ci.yml`) performs the following checks:

1. **Import Sorting Check** (`isort --check-only`)
2. **Code Formatting Check** (`black --check`)
3. **Linting** (`ruff check`)
4. **Type Checking** (`mypy`)
5. **Tests with Coverage** (`pytest --cov`)

The pipeline runs on Python 3.9, 3.10, 3.11, and 3.12 to ensure compatibility.

### PR Requirements

Pull requests must pass all CI checks before they can be merged. If any check fails:

1. The PR will be blocked from merging
2. You'll see detailed error messages in the GitHub Actions tab
3. Fix the issues locally and push again

### Running the Same Checks Locally

To run exactly what CI runs:
```bash
make check
```

This runs all linters and tests, giving you confidence that CI will pass.

## Claude Code Integration

### SessionStart Hook

DigiChat includes a `.claude/SessionStart` hook that automatically:

1. Installs development dependencies
2. Installs pre-commit hooks
3. Updates pre-commit to the latest versions
4. Shows available commands

This ensures Claude Code always has the tools it needs to:
- Run linters before committing
- Fix linting errors automatically
- Run tests and fix failures
- Maintain code quality standards

### How It Works

When Claude Code starts a session, it:

1. Runs `.claude/SessionStart` to set up the environment
2. Gets access to all the same tools that CI uses
3. Can run `make lint`, `make test`, etc. to check code
4. Pre-commit hooks run automatically before commits
5. If hooks fail, Claude Code sees the errors and can fix them

This means **Claude Code will never push code that fails CI checks**.

## Workflow Examples

### Adding a New Feature

1. Create a new branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make your changes and run tests:
   ```bash
   make test
   ```

3. Format and lint your code:
   ```bash
   make format
   make lint
   ```

4. Commit (pre-commit hooks will run automatically):
   ```bash
   git commit -m "Add my feature"
   ```

5. If hooks fail, fix the issues and commit again

6. Push and create a PR:
   ```bash
   git push -u origin feature/my-feature
   ```

### Fixing Linting Issues

If linting fails, you can often auto-fix issues:

```bash
# Auto-format code
make format

# Some ruff issues can be auto-fixed
ruff check --fix src tests

# Type checking issues usually need manual fixes
mypy src
```

### Running Tests in Watch Mode

For test-driven development:

```bash
pytest --watch
```

Or with coverage:

```bash
pytest --cov=digichat --cov-report=term-missing -v
```

## Configuration Files

- `.github/workflows/ci.yml` - GitHub Actions CI configuration
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `pyproject.toml` - Tool configurations (black, ruff, mypy, pytest, isort)
- `requirements-dev.txt` - Development dependencies
- `Makefile` - Convenient commands for development
- `.claude/SessionStart` - Claude Code session initialization

## Troubleshooting

### Pre-commit is Slow

Pre-commit caches environments. If it's slow, try:
```bash
pre-commit clean
pre-commit install-hooks
```

### Tests Failing Locally But Not in CI

Ensure you have the same Python version as CI (3.9, 3.10, 3.11, or 3.12).

### Import Errors When Running Tests

Make sure the package is installed in editable mode:
```bash
pip install -e ".[dev]"
```

### Type Checking Fails

Ensure you have type stubs installed:
```bash
pip install types-setuptools
```

## Best Practices

1. **Always run `make check` before pushing** to ensure CI will pass
2. **Let pre-commit hooks fix issues** rather than skipping them
3. **Write tests for new features** to maintain coverage
4. **Run tests frequently** during development
5. **Use type hints** to catch bugs early with mypy
6. **Keep dependencies up to date** with `pip list --outdated`

## Getting Help

- Run `make help` to see available commands
- Check CI logs in GitHub Actions for detailed error messages
- Review tool documentation:
  - [black](https://black.readthedocs.io/)
  - [ruff](https://docs.astral.sh/ruff/)
  - [mypy](https://mypy.readthedocs.io/)
  - [pytest](https://docs.pytest.org/)
  - [pre-commit](https://pre-commit.com/)
