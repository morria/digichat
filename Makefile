.PHONY: help install format lint test check pre-commit clean

help:  ## Show this help message
	@echo "DigiChat Development Commands"
	@echo "=============================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install development dependencies
	pip install --upgrade pip
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt
	pre-commit install

format:  ## Auto-format code (isort + black)
	@echo "Running isort..."
	isort src tests
	@echo "Running black..."
	black src tests
	@echo "✓ Code formatted"

lint:  ## Run all linters (isort check, black check, ruff, mypy)
	@echo "Checking import sorting with isort..."
	isort --check-only --diff src tests
	@echo "Checking code formatting with black..."
	black --check --diff src tests
	@echo "Running ruff linter..."
	ruff check src tests
	@echo "Running mypy type checker..."
	mypy src
	@echo "✓ All linting checks passed"

test:  ## Run tests with coverage
	@echo "Running tests..."
	pytest --cov=digichat --cov-report=term-missing --cov-report=html
	@echo "✓ Tests completed. Coverage report: htmlcov/index.html"

check: lint test  ## Run all checks (lint + test) - same as CI

pre-commit:  ## Run pre-commit on all files
	pre-commit run --all-files

clean:  ## Clean up generated files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

.DEFAULT_GOAL := help
