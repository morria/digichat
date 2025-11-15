.PHONY: help system-deps install format lint test check pre-commit clean

help:  ## Show this help message
	@echo "DigiChat Development Commands"
	@echo "=============================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

system-deps:  ## Install required system dependencies (requires sudo)
	@echo "Installing system dependencies..."
	@if command -v apt-get >/dev/null 2>&1; then \
		echo "Detected Debian/Ubuntu system"; \
		sudo apt-get update && sudo apt-get install -y portaudio19-dev python3-dev; \
	elif command -v dnf >/dev/null 2>&1; then \
		echo "Detected Fedora/RHEL system"; \
		sudo dnf install -y portaudio-devel python3-devel; \
	elif command -v pacman >/dev/null 2>&1; then \
		echo "Detected Arch Linux system"; \
		sudo pacman -S --noconfirm portaudio; \
	elif command -v brew >/dev/null 2>&1; then \
		echo "Detected macOS with Homebrew"; \
		brew install portaudio; \
	else \
		echo "Unknown package manager. Please install portaudio development headers manually:"; \
		echo "  - Debian/Ubuntu: sudo apt-get install portaudio19-dev python3-dev"; \
		echo "  - Fedora/RHEL: sudo dnf install portaudio-devel python3-devel"; \
		echo "  - Arch Linux: sudo pacman -S portaudio"; \
		echo "  - macOS: brew install portaudio"; \
		exit 1; \
	fi
	@echo "✓ System dependencies installed"

install:  ## Install development dependencies
	@echo "Checking for required system dependencies..."
	@if ! pkg-config --exists portaudio-2.0 2>/dev/null; then \
		echo "Error: PortAudio development headers not found."; \
		echo "Please run 'make system-deps' first to install system dependencies."; \
		echo ""; \
		echo "Or install manually:"; \
		echo "  Debian/Ubuntu: sudo apt-get install portaudio19-dev python3-dev"; \
		echo "  Fedora/RHEL: sudo dnf install portaudio-devel python3-devel"; \
		echo "  Arch Linux: sudo pacman -S portaudio"; \
		echo "  macOS: brew install portaudio"; \
		exit 1; \
	fi
	@echo "✓ System dependencies found"
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
